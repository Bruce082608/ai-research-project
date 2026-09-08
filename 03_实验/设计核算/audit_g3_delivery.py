"""Audit local G3 evidence and accounting; never imports model/evaluation code.

Run with a Python environment containing pypdf. All inputs are already local.
This checks provenance and design consistency, not experimental effectiveness.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
from statistics import NormalDist
import ast
import csv
import hashlib
import importlib.metadata
import json
import math
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SRC = ROOT / '03_实验/来源核验'
PAPERS = ROOT / '02_文献/原文/scheme_a_g2'


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(*args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=True).stdout


def main():
    checks = {}
    lock = read(SRC / 'source_lock_g3.json')
    locked_files = {}
    for resource, spec in lock['resources'].items():
        for name, expected in spec['files'].items():
            file = SRC / name
            assert digest(file) == expected['sha256'], name
            assert file.stat().st_size == expected['bytes'], name
            locked_files[name] = expected['sha256']
    checks['source_lock'] = {'resources': len(lock['resources']), 'files': len(locked_files), 'all_match': True}

    manifests = [SRC / 'initial_source_manifest.json', *sorted(SRC.glob('technical_downloads_*.json')), PAPERS / 'downloads_manifest.json']
    verified = 0
    superseded = []
    for manifest in manifests:
        for item in read(manifest):
            file = ROOT / item['file'] if item['file'].startswith('03_实验/') else manifest.parent / item['file']
            if item.get('artifact_state', '').startswith('superseded_'):
                replacements = read(manifest.parent / item['current_response_manifest'])
                current = [x for x in replacements if Path(x['file']).name.casefold() == file.name.casefold()]
                assert len(current) == 1 and str(current[0]['http_status']) == '200'
                assert digest(file) == current[0]['sha256']
                superseded.append({'manifest': str(manifest.relative_to(ROOT)), 'file': item['file'], 'historical_status': item['http_status'], 'current_body_verified': True})
                continue
            assert digest(file) == item['sha256'], (manifest.name, item['file'])
            if 'bytes' in item:
                assert file.stat().st_size == item['bytes'], item['file']
            verified += 1
    checks['download_history'] = {'manifests': len(manifests), 'retained_response_hashes_verified': verified, 'superseded_response_exceptions': superseded}

    book = (ROOT / '02_文献/引文库.md').read_text()
    parts = re.split(r'(?m)^## \[(R-\d{3})\]', book)
    records = {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}
    assert len(records) == (len(parts) - 1) // 2 == 61
    checked = {key for key, body in records.items() if re.search(r'核验状态：已核验', body)}
    metadata = {key for key, body in records.items() if re.search(r'核验状态：待核验', body)}
    cards = {p.stem for p in (ROOT / '02_文献/精读卡').glob('R-*.md')}
    assert len(checked) == 16 and len(metadata) == 45 and checked == cards
    assert checked | metadata == set(records)
    outline_refs = set(re.findall(r'R-\d{3}', (ROOT / '02_文献/综述大纲.md').read_text()))
    assert outline_refs <= checked
    checks['citations'] = {'unique_papers': len(records), 'verified': len(checked), 'metadata_only': len(metadata), 'cards': len(cards), 'outline_uses_verified_only': True}

    expected_papers = {'R-058': ('2604.12384v1', 17), 'R-059': ('2607.00572v3', 27), 'R-060': ('2512.23260v2', 16), 'R-061': ('2604.24074v1', 15)}
    atom = {'a': 'http://www.w3.org/2005/Atom'}
    entries = ET.parse(PAPERS / 'metadata.xml').findall('a:entry', atom)
    official_ids = {e.find('a:id', atom).text.rsplit('/', 1)[-1] for e in entries}
    paper_checks = {}
    for rid, (version, pages) in expected_papers.items():
        pdf = PAPERS / (version + '.pdf')
        actual = len(PdfReader(pdf).pages)
        text_pages = re.findall(r'(?m)^===== PDF PAGE (\d+) =====$', (PAPERS / (version + '.txt')).read_text())
        assert actual == pages and list(map(int, text_pages)) == list(range(1, pages + 1))
        assert version in official_ids and version in records[rid]
        assert version in (ROOT / '02_文献/精读卡' / (rid + '.md')).read_text()
        paper_checks[rid] = {'version': version, 'physical_pages': actual, 'sha256': digest(pdf)}
    assert len(list(PAPERS.glob('*.pdf'))) == 4
    checks['new_papers'] = paper_checks

    queries = read(PAPERS / 'queries_manifest.json')
    counts = {}
    found_ids = set()
    for query in queries:
        entries = ET.parse(PAPERS / query['file']).findall('a:entry', atom)
        ids = [e.find('a:id', atom).text for e in entries]
        assert ids == [e['id'] for e in query['entries']]
        counts[str(query['query_id'])] = len(ids)
        found_ids.update(ids)
    summary = read(PAPERS / 'batch_summary.json')
    assert counts == summary['returned_per_query'] == {'1': 11, '2': 0, '3': 1, '4': 2}
    assert sum(counts.values()) == summary['total_records'] == 14
    assert len(found_ids) == summary['unique_ids'] == 14
    checks['queries'] = {'returned_per_query': counts, 'unique_version_urls': len(found_ids), 'new_full_reads': 4}

    hb = {}
    for split in ['test', 'val']:
        with (SRC / f'harmbench_data_behavior_datasets_harmbench_behaviors_text_{split}.csv').open() as f:
            hb[split] = [r for r in csv.DictReader(f) if r['FunctionalCategory'] == 'standard']
    assert [len(hb['test']), len(hb['val'])] == [159, 41]
    safety = read(OUT / 'safety_split_g3.json')
    counts = {g: len(rows) for g, rows in safety['partitions'].items()}
    expected = {'harmbench_test': 159, 'test_candidate': 192, 'direction_extract': 67, 'development_calibration': 36, 'development_diagnostic': 38}
    assert counts == safety['counts'] == expected
    retained = [r['id'] for rows in safety['partitions'].values() for r in rows]
    excluded = [r['id'] for r in safety['excluded']]
    sources = {r['id']: r for r in read(OUT / 'safety_source_inventory.json')}
    adv_path = OUT / 'advbench_inventory_source.csv'
    assert digest(adv_path) == '6cd1a5c63c07610d7eb67307772ee5606017ee950b5770ab288a2c487489d3e1'
    with adv_path.open() as f:
        adv = list(csv.DictReader(f))
    assert len(adv) == 520
    assert all(sources[f'adv:{i}']['text'] == row['goal'] for i, row in enumerate(adv, 1))
    assert all(sources['hb:' + row['BehaviorID']]['text'] == row['Behavior'] for row in hb['test'])
    assert len(sources) == 679 and len(set(retained)) == len(retained)
    assert len(excluded) == len(set(excluded)) == 187
    assert not set(retained) & set(excluded) and set(retained) | set(excluded) == set(sources)
    seen_clusters = set()
    for group, rows in safety['partitions'].items():
        clusters = {r['cluster'] for r in rows}
        assert not clusters & seen_clusters
        seen_clusters |= clusters
        for row in rows:
            assert sources[row['id']]['group'] == group
            assert hashlib.sha256(row['text'].encode()).hexdigest() == row['prompt_sha256']
    assert {r['id'] for r in safety['partitions']['harmbench_test']} == {'hb:' + r['BehaviorID'] for r in hb['test']}
    semantic = read(OUT / 'safety_semantic_review_g3.json')
    assert sum(x['accepted'] for x in semantic['content_edges']) == 405 and len(semantic['manual_links']) == 11
    checks['safety_inventory'] = {'official_standard_test_val': [159, 41], 'partitions': counts, 'main_test_total': 351, 'excluded_advbench': 187, 'cross_use_guard_clusters_disjoint': True, 'not_exhaustive_semantic_validation': True}

    train = {r['row']: r for r in read(OUT / 'alpaca10k_manifest_g3.json')}
    inv = read(OUT / 'inventory_g3.json')
    assert len(train) == 10000 and len({r['user_sha256'] for r in train.values()}) == 10000
    for field, source_field in [('input_tokens', 'total_tokens'), ('supervised_tokens', 'supervised_tokens')]:
        assert sum(r[source_field] for r in train.values()) == inv['training'][field]
    assert max(r['total_tokens'] for r in train.values()) == 973 <= 2048
    raw = read(SRC / 'alpaca_cleaned.json')
    for row, spec in train.items():
        original = raw[row - 1]
        user = original['instruction'].strip() + ('\n\n' + original['input'].strip() if original['input'].strip() else '')
        normalized = ' '.join(unicodedata.normalize('NFKC', user).casefold().split())
        assert hashlib.sha256(normalized.encode()).hexdigest() == spec['user_sha256']
    contraction = re.compile(r"\bi['’]m sorry\b", re.I)
    assert not any(contraction.search(raw[row - 1]['output']) for row in train)
    correction = read(OUT / 'cpu_correction_g3.json')
    assert len(correction['old_selected_im_sorry_rows']) == 58 and not correction['new_selected_im_sorry_rows']
    assert correction['after'] == inv and correction['safety_split_hash_unchanged']
    checks['training_inventory'] = {'counts': inv['counts'], 'training_tokens': inv['training'], 'contraction_regression_hits': 0, 'not_human_safety_certified': True}

    plans = read(OUT / 'E_token_schedule_g3.json')['seeds']
    budgets = read(OUT / 'E_token_budget_g3.json')['summary']
    safe_tokens = {r['id']: r for r in read(OUT / 'safety_template_token_inventory.json')}
    direction_ids = {r['id'] for r in safety['partitions']['direction_extract']}
    assert set(plans) == set(budgets) == {'17', '29', '43'}
    for seed, updates in plans.items():
        assert len(updates) == 625 and [x['step'] for x in updates] == list(range(1, 626))
        rows = [r for u in updates for r in u['benign_rows']]
        assert len(rows) == len(set(rows)) == 10000 and set(rows) == set(train)
        cumulative = safe_total = input_extra = occurrences = 0
        safe_seen = set()
        for update in updates:
            original = [train[r] for r in update['benign_rows']]
            keep = update['benign_keep_supervised_prefix']
            assert len(original) == len(keep) == 16
            assert all(1 <= n <= r['supervised_tokens'] for n, r in zip(keep, original))
            total = sum(r['supervised_tokens'] for r in original)
            safe = sum(r['keep_supervised_prefix'] for r in update['safe'])
            assert total == update['total_supervised'] == sum(keep) + safe
            assert safe == update['safety_quota']
            cumulative += total
            safe_total += safe
            assert 0 <= cumulative - 20 * safe_total < 20
            for row in update['safe']:
                assert row['id'] in direction_ids and 1 <= row['keep_supervised_prefix'] <= safe_tokens[row['id']]['supervised_tokens']
                input_extra += safe_tokens[row['id']]['total_tokens']
                occurrences += 1
                safe_seen.add(row['id'])
        assert safe_seen == direction_ids
        assert cumulative == budgets[seed]['total_supervised'] == inv['training']['supervised_tokens']
        assert safe_total == budgets[seed]['safe_supervised'] and input_extra == budgets[seed]['extra_safe_input_tokens']
        assert occurrences == budgets[seed]['extra_safe_occurrences']
    rerun = read(OUT / 'finalize_rerun_audit_g3.json')
    assert rerun['exit_code'] == 0 and rerun['outputs_unchanged']
    assert all(digest(OUT / file) == sha for file, sha in rerun['after_sha256'].items())
    checks['E_accounting'] = {'all_1875_updates_checked': True, 'all_seed_budgets': budgets, 'finalizer_rerun_hashes_match_current': True}

    config = read(SRC / 'qwen_config.json')
    hidden, intermediate = config['hidden_size'], config['intermediate_size']
    kv = hidden // config['num_attention_heads'] * config['num_key_value_heads']
    lora_parameters = 16 * config['num_hidden_layers'] * (4 * hidden + 2 * (hidden + kv) + 3 * (hidden + intermediate))
    budget = read(OUT / 'G3_budget_precision.json')
    assert lora_parameters == budget['qwen_lora_parameters_derived_from_config'] == 40370176
    assert sum(budget['allocations'].values()) == 100 and budget['formal_train_runs'] == 18
    normal = NormalDist()
    se = math.sqrt(budget['assumed_pair_discordance'] / budget['n'])
    power = max(0, 2 * normal.cdf(budget['uncorrected_tost_margin'] / se - normal.inv_cdf(.95)) - 1)
    assert math.isclose(power, budget['uncorrected_tost_power_at_zero'], abs_tol=1e-12)
    checks['planning_arithmetic'] = {'lora_parameters': lora_parameters, 'normal_tost_scenario_power': power, 'not_measured_gpu_cost_or_confirmatory_test': True}

    fixture = read(OUT / 'template_token_fixture.json')
    assert fixture['input_ids'][-2:] == fixture['terminal_tokens'] == [151645, 198]
    tree = ast.parse((SRC / 'harmbench_eval_utils.py').read_text())
    constants = [ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'LLAMA2_CLS_PROMPT' for t in n.targets)]
    assert len(constants) == 1 and constants[0]['prompt'] == (SRC / 'harmbench_primary_template.txt').read_text()
    checks['template_sources'] = {'primary_template_matches_ast_literal': True, 'fixture_terminal_ids': [151645, 198], 'transformers_model_integration_not_run': True}

    md_paths = command('rg', '--files', '-g', '*.md', '-g', '!**/.venv/**', '-g', '!**/原文/**', '-g', '!03_实验/来源核验/**', '-g', '!03_实验/设计核算/历史/**').splitlines()
    md_paths.append('03_实验/来源核验/来源锁定与实现约定.md')
    local_links = 0
    broken = []
    for name in md_paths:
        path = ROOT / name
        for match in re.finditer(r'\[[^\]\n]*\]\((<[^>]+>|[^)\n]+)\)', path.read_text()):
            target = match.group(1).strip().strip('<>')
            if target.startswith('#') or urlsplit(target).scheme:
                continue
            target = re.sub(r':\d+$', '', unquote(target.split('#')[0]))
            local_links += 1
            if not (path.parent / target).exists():
                broken.append({'file': name, 'target': target})
    assert not broken, broken
    checks['markdown_links'] = {'authored_documents_scanned': len(md_paths), 'local_links': local_links, 'broken': broken, 'excludes_vendor_snapshots_and_cpu_archive': True}

    command('git', 'diff', '--check')
    # Disable git path quoting so non-ASCII filenames can be passed back exactly.
    protected = command('git', '-c', 'core.quotepath=false', 'ls-files', '--', 'fable51-长程科研任务执行提示词.md', 'fable51-科研工作台.md', '实验日志.md', '03_实验/code', '03_实验/configs', '03_实验/results', '03_实验/remote').splitlines()
    for name in protected:
        blob = subprocess.run(['git', 'show', 'HEAD:' + name], cwd=ROOT, capture_output=True, check=True).stdout
        assert hashlib.sha256(blob).hexdigest() == digest(ROOT / name), name
    questions = (ROOT / 'QUESTIONS.md').read_text()
    assert re.search(r'Q-011[^\n]*已答且执行完成', questions)
    assert re.search(r'Q-012[^\n]*待答', questions) and re.search(r'Q-013[^\n]*待答', questions)
    checks['workspace_state'] = {'git_diff_check': 'passed', 'protected_tracked_files_unchanged_vs_HEAD': len(protected), 'Q011': 'complete', 'Q012_G3': 'pending', 'Q013_outline': 'pending', 'git_status': command('git', '-c', 'core.quotepath=false', 'status', '--short')}

    deliverables = ['STATE.md', 'PLAN.md', 'DECISIONS.md', 'QUESTIONS.md', 'ERRATA.md', '01_选题/Research_Brief.md', '03_实验/protocol.md', '03_实验/protocol_审查.md', '03_实验/G3_审批包.md', '02_文献/综述大纲.md', '02_文献/对比矩阵.md', '02_文献/引用-论断对照表.md', '02_文献/检索记录/方案A_G2第二批审计.md']
    report = {'status': 'passed_local_evidence_audit_not_G3_approval', 'at_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'Local provenance, deterministic design accounting and document state; no new web search or model execution', 'runtime': {'python': sys.version, 'executable': sys.executable, 'pypdf': importlib.metadata.version('pypdf')}, 'checks': checks, 'deliverable_sha256': {name: digest(ROOT / name) for name in deliverables}, 'audit_script_sha256': digest(Path(__file__)), 'not_run': ['Formal training/evaluation implementation', 'Transformers tokenizer/model integration', 'GPU loss/gradient/reference/hook validation', '32/64-step calibration', 'Judge inference', 'Full 18 trainings', 'Human annotation', 'GPU throughput, peak memory, disk and historical billing verification'], 'new_gpu_model_runs': 0}
    (OUT / 'G3_交付审计.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'source_files': len(locked_files), 'papers': len(records), 'verified': len(checked), 'main_test': 351, 'supervised_tokens': inv['training']['supervised_tokens'], 'local_links': local_links, 'protected_files': len(protected)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
