"""CPU-only source inventory/token accounting. No model weights, training or evaluation.

Run with .venv/bin/python from the workspace root. Outputs are design artifacts,
not research results. Thresholds are prospective lexical screening choices.
"""
from pathlib import Path
import csv, json, hashlib, re, unicodedata, math
from collections import Counter
import numpy as np
import pyarrow.parquet as pq
from tokenizers import Tokenizer
from jinja2 import Environment
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / '03_实验/来源核验'
OUT = Path(__file__).resolve().parent

def norm(s):
    return ' '.join(unicodedata.normalize('NFKC', s).casefold().split())

def digest(s):
    return hashlib.sha256(s.encode()).hexdigest()

def key(s, salt):
    return digest(salt + '\0' + norm(s))

def save(name, value):
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def rows(name):
    return list(csv.DictReader((SRC/name).open()))

def parquet(name):
    return pq.read_table(SRC/name).to_pylist()

def main():
    hb = rows('harmbench_data_behavior_datasets_harmbench_behaviors_text_test.csv')
    hb = [r for r in hb if r['FunctionalCategory'] == 'standard']
    xv = rows('xstest_prompts_official.csv')
    xs = [r for r in xv if r['label'] == 'safe']
    assert all(not r['type'].startswith('contrast_') for r in xs)
    mm = parquet('mmlu_test.parquet')
    md = parquet('mmlu_dev.parquet')
    gs = parquet('gsm8k_test.parquet')
    ie = [json.loads(s) for s in (SRC/'ifeval_input_data.jsonl').read_text().splitlines()]
    adv = list(csv.DictReader((OUT/'advbench_inventory_source.csv').open()))
    previous = json.loads((OUT/'方案A_AdvBench划分候选.json').read_text())
    partition = {r['source_row_1based']: group for group, rr in previous['partitions'].items() for r in rr}
    safety = [dict(id='hb:'+r['BehaviorID'], group='harmbench_test', text=r['Behavior']) for r in hb]
    safety += [dict(id=f'adv:{i}', group=partition[i], text=r['goal']) for i,r in enumerate(adv,1)]
    # Compute lexical candidates over the complete safety inventory, before any model outputs.
    text = [norm(x['text']) for x in safety]
    word = TfidfVectorizer(ngram_range=(1,2), stop_words='english', sublinear_tf=True).fit_transform(text)
    char = TfidfVectorizer(analyzer='char_wb', ngram_range=(3,5), sublinear_tf=True).fit_transform(text)
    sw, sc = (word@word.T).toarray(), (char@char.T).toarray()
    pairs=[]
    for i in range(len(safety)):
        for j in range(i):
            exact = text[i] == text[j]
            if exact or sw[i,j] >= .40 or sc[i,j] >= .55:
                pairs.append(dict(a=safety[i]['id'], b=safety[j]['id'], group_a=safety[i]['group'], group_b=safety[j]['group'], word_cos=float(sw[i,j]), char_cos=float(sc[i,j]), exact=exact, text_a=safety[i]['text'], text_b=safety[j]['text']))
    pairs.sort(key=lambda x:-max(x['word_cos'],x['char_cos']))
    save('safety_lexical_candidates.json', pairs)
    save('safety_source_inventory.json', safety)
    # Utility subsets are selected independently of any model performance.
    msel = sorted(range(len(mm)), key=lambda i:key(mm[i]['subject']+'\0'+mm[i]['question'],'mmlu-2k-v1'))[:2000]
    gsel = sorted(range(len(gs)), key=lambda i:key(gs[i]['question'],'gsm8k-500-v1'))[:500]
    utility = dict(mmlu=[dict(source_row_1based=i+1, subject=mm[i]['subject'], question_sha256=digest(norm(mm[i]['question']))) for i in msel], gsm8k=[dict(source_row_1based=i+1,question_sha256=digest(norm(gs[i]['question']))) for i in gsel], ifeval=[dict(key=x['key'],prompt_sha256=digest(norm(x['prompt'])))for x in ie], xstest=[dict(id=x['id'], type=x['type'],prompt_sha256=digest(norm(x['prompt'])))for x in xs])
    save('utility_manifest_g3.json', utility)
    # Hold out all source test questions, not just the utility subsets.
    guards = [dict(id=x['id'],text=x['text'])for x in safety]
    guards += [dict(id='xs:'+x['id'],text=x['prompt'])for x in xv]
    guards += [dict(id=f'mmlu:{i+1}',text=x['question'])for i,x in enumerate(mm)]
    guards += [dict(id=f'mmlu_dev:{i+1}',text=x['question'])for i,x in enumerate(md)]
    guards += [dict(id=f'gsm8k:{i+1}',text=x['question'])for i,x in enumerate(gs)]
    guards += [dict(id='ifeval:'+str(x['key']),text=x['prompt'])for x in ie]
    guard_set={norm(x['text']) for x in guards}
    data = json.loads((SRC/'alpaca_cleaned.json').read_text())
    tokenizer = Tokenizer.from_file(str(SRC/'qwen_tokenizer.json'))
    template = Environment().from_string(json.loads((SRC/'qwen_tokenizer_config.json').read_text())['chat_template'])
    system = 'You are Qwen, created by Alibaba Cloud. You are a helpful assistant.'
    def render(user, response=None):
        messages=[dict(role='system',content=system),dict(role='user',content=user)]
        if response is not None: messages.append(dict(role='assistant',content=response))
        return template.render(messages=messages, tools=None, add_generation_prompt=response is None)
    def tokens(user,response):
        full=tokenizer.encode(render(user,response),add_special_tokens=False).ids
        prefix=tokenizer.encode(render(user),add_special_tokens=False).ids
        assert full[:len(prefix)] == prefix
        assert full[-2:] == [151645,198], full[-5:]
        return len(full),len(full)-len(prefix)-1,len(prefix),full
    # Broad, deterministic exclusions remove explicit sensitive-content and refusal vocabulary.
    # This is a conservative lexical screen, not certification that every retained row is benign.
    sensitive = re.compile(r'\b(?:bomb\w*|weapons?|hacks?|hacking|malware|ransomware|phish\w*|steal\w*|fraud\w*|suicid\w*|self[- ]harm|racis\w*|sex\w*|porn\w*|poison\w*|terror\w*|kill\w*|injur\w*|violen\w*|drugs?|explosi\w*|hate|illegal\w*|passwords?|credit.cards?|personal.information|discrimina\w*|jailbreak\w*)\b',re.I)
    refusal = re.compile(r"\b(?:i (?:am|['’]m) sorry|i (?:cannot|can['’]t|am unable)|as an ai|not (?:able|allowed) to|i (?:must|have to) (?:refuse|decline))\b",re.I)
    seen=set(); eligible=[]; excluded=[]
    for i,r in enumerate(data,1):
        user=r['instruction'].strip()+ ('\n\n'+r['input'].strip() if r['input'].strip() else '')
        response=r['output'].strip(); n=norm(user)
        reason=None
        if not user or not response: reason='empty'
        elif n in seen: reason='duplicate_user'
        elif any(t in user+response for t in ['<|im_start|>','<|im_end|>','<|endoftext|>']): reason='control_token_text'
        elif n in guard_set: reason='exact_evaluation_overlap'
        elif sensitive.search(user+'\n'+response): reason='sensitive_lexicon'
        elif refusal.search(response): reason='refusal_lexicon'
        seen.add(n)
        if reason: excluded.append(dict(row=i,reason=reason)); continue
        total,supervised,prefix,ids=tokens(user,response)
        if total>2048: excluded.append(dict(row=i,reason='over_2048_no_truncation'));continue
        eligible.append(dict(row=i,user=user,user_sha256=digest(n),total_tokens=total,supervised_tokens=supervised,prefix_tokens=prefix,order_key=key(user,'alpaca10k-g3-v1')))
    eligible.sort(key=lambda x:x['order_key'])
    # A fixed 12k reserve is screened. If <10k survive, fail instead of adapting to outputs.
    reserve=eligible[:12000]
    corpus=[norm(g['text'])for g in guards]+[norm(r['user'])for r in reserve]
    tf = TfidfVectorizer(ngram_range=(1,2), stop_words='english',sublinear_tf=True,dtype=np.float32,max_features=200000).fit_transform(corpus)
    reference=tf[:len(guards)]; query=tf[len(guards):]
    overlap=[]; clean=[]
    for start in range(0,len(reserve),128):
        scores=(query[start:start+128]@reference.T).toarray()
        for offset,scores_row in enumerate(scores):
            j=int(scores_row.argmax());r=reserve[start+offset];score=float(scores_row[j])
            if score>=.65:
                overlap.append(dict(row=r['row'],guard_id=guards[j]['id'],word_cos=score,user=r['user'],guard_text=guards[j]['text']))
                excluded.append(dict(row=r['row'],reason='evaluation_tfidf_ge_0.65',guard_id=guards[j]['id']))
            else: clean.append(r)
    assert len(clean)>=10000,len(clean)
    selected=clean[:10000]
    save('alpaca_eval_overlap_candidates.json',overlap)
    save('alpaca_exclusions_g3.json',excluded)
    save('alpaca10k_manifest_g3.json',[{k:v for k,v in r.items()if k!='user'}for r in selected])
    save('alpaca10k_prompt_audit.json',[dict(row=r['row'],user=r['user'])for r in selected])
    refusal_text="I apologize, but I’m not able to help with this request. This involves potentially harmful, dangerous, or illegal activities, and I must decline to provide any assistance."
    safe_tok=[dict(id=f'adv:{i}',total_tokens=tokens(r['goal'],refusal_text)[0],supervised_tokens=tokens(r['goal'],refusal_text)[1]) for i,r in enumerate(adv,1)]
    save('safety_template_token_inventory.json',safe_tok)
    save('template_token_fixture.json',dict(system=system,refusal_template=refusal_text,user='Explain what a prime number is.',response='A prime number has exactly two positive divisors.',rendered=render('Explain what a prime number is.','A prime number has exactly two positive divisors.'),input_ids=tokens('Explain what a prime number is.','A prime number has exactly two positive divisors.')[3],terminal_tokens=[151645,198],penalty_token_proposal='last_nonpadding_newline_198',supervised_excludes_final_newline=True))
    inventory=dict(kind='CPU_design_inventory_no_model_results',counts=dict(harmbench_standard_test=len(hb),xstest_all=len(xv),xstest_safe=len(xs),mmlu_all_test=len(mm),mmlu_dev=len(md),gsm8k_all_test=len(gs),ifeval=len(ie),alpaca_raw=len(data),alpaca_eligible_before_overlap=len(eligible),reserve=len(reserve),reserve_after_overlap=len(clean),selected=len(selected),safety_pair_candidates=len(pairs)),exclusions=dict(Counter(x['reason']for x in excluded)),training=dict(input_tokens=sum(r['total_tokens']for r in selected),supervised_tokens=sum(r['supervised_tokens']for r in selected),min_length=min(r['total_tokens']for r in selected),max_length=max(r['total_tokens']for r in selected),median_length=float(np.median([r['total_tokens']for r in selected])),max_sequence_length=2048,optimizer_steps=625,epochs=1),selection_salts=dict(alpaca='alpaca10k-g3-v1',mmlu='mmlu-2k-v1',gsm8k='gsm8k-500-v1'),safety_candidate_thresholds=dict(word_cos=.40,char_cos=.55),alpaca_overlap_threshold=.65,interpretation='Lexical screening and token accounting only; no exhaustive semantic or safety certification; no model outputs used.')
    save('inventory_g3.json',inventory)
    print(json.dumps(inventory,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__': main()
