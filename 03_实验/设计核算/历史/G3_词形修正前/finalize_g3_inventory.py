"""Finalize a prospective G3 data proposal and exact E token quotas on CPU.
This is source/design accounting; it does not implement or run the experiment.
"""
from pathlib import Path
import json, hashlib, re
from collections import defaultdict, Counter
import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

P=Path(__file__).resolve().parent

def read(name):return json.loads((P/name).read_text())
def save(name,obj):(P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def sha(s):return hashlib.sha256(s.encode()).hexdigest()

def main():
    items={x['id']:x for x in read('safety_source_inventory.json')}
    candidates=read('safety_lexical_candidates.json')
    stop=set(ENGLISH_STOP_WORDS)|set('write create generate give provide instruct instructions step steps guide details detailed plan tutorial demonstrate explain describe outline develop show design script program story post blog article social media ways way help people someone user users use using make build avoid getting caught commit committing how'.split())
    def core(t):return set(re.findall(r'[a-z]+',t.lower()))-stop
    parent={i:i for i in items}
    def root(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    edges=[]
    for i,x in enumerate(candidates):
        a,b=core(x['text_a']),core(x['text_b'])
        score=len(a&b)/len(a|b) if a|b else 0
        accepted=x['exact']or(score>=.5 and len(a&b)>=2)
        edges.append(dict(candidate_index=i,a=x['a'],b=x['b'],core_jaccard=score,accepted=accepted,rule='conservative_content_overlap_guard_not_equivalence_label'))
        if accepted:parent[root(x['a'])]=root(x['b'])
    # Added by reading the 30 HB candidate pairs and the 22 largest content groups.
    # These deliberately broad exclusions protect evaluation from generic/specific
    # variants; they do not declare every connected prompt semantically identical.
    manual=[
        ('adv:13','adv:99','identity theft; extra personal-information wording'),
        ('adv:8','adv:37','generic versus household bomb construction'),
        ('adv:8','adv:102','generic bomb-construction instruction variants'),
        ('adv:8','adv:237','generic bomb tutorial variants'),
        ('adv:8','adv:275','generic versus at-home bomb construction'),
        ('adv:275','hb:pipe_bomb_home_build_guide','generic at-home versus pipe-bomb construction; conservative exclusion'),
        ('adv:444','hb:suicide_detailed_instructions','same requested action'),
        ('adv:470','hb:suicide_detailed_instructions','same requested action with instruct wording'),
        ('adv:139','hb:suicide_detailed_instructions','same requested action with avoid-detection qualifier'),
        ('adv:163','hb:student_harassment_bullying_encouragement','encouraging bullying; broad versus classmate target; conservative exclusion'),
        ('adv:473','hb:gunpoint_bank_robbery_guide','generic versus armed bank robbery; conservative exclusion'),
    ]
    for a,b,reason in manual:
        assert a in items and b in items
        parent[root(a)]=root(b)
    groups=defaultdict(list)
    for id in items:groups[root(id)].append(id)
    rank={'harmbench_test':0,'test_candidate':1,'direction_extract':2,'development_calibration':3,'development_diagnostic':4}
    selected=defaultdict(list);excluded=[];clusters=[]
    for members in groups.values():
        cid='cluster:'+sha('\0'.join(sorted(members)))[:16]
        best=min(rank[items[x]['group']]for x in members)
        pool=[x for x in members if rank[items[x]['group']]==best]
        retained=sorted(pool) if best==0 else [min(pool,key=lambda x:sha('representative-v1\0'+x))]
        for id in retained:
            r=items[id];selected[r['group']].append(dict(id=id,cluster=cid,prompt_sha256=sha(r['text']),text=r['text']))
        for id in members:
            if id not in retained:excluded.append(dict(id=id,old_group=items[id]['group'],cluster=cid,reason='lower_priority_or_same_guard_cluster',retained=retained))
        clusters.append(dict(cluster=cid,members=sorted(members),retained=retained))
    for group in selected:selected[group].sort(key=lambda x:x['id'])
    assert len(selected['harmbench_test'])==159
    split_clusters={g:{x['cluster']for x in rr}for g,rr in selected.items()}
    train_side=['direction_extract','development_calibration','development_diagnostic']
    test_clusters=split_clusters['harmbench_test']|split_clusters['test_candidate']
    assert not any(split_clusters[g]&test_clusters for g in train_side)
    assert all(not(split_clusters[a]&split_clusters[b])for i,a in enumerate(train_side)for b in train_side[:i])
    proposal=dict(status='G3_review_proposal_no_model_outputs',counts={g:len(rr)for g,rr in selected.items()},partitions=dict(selected),clusters=clusters,excluded=excluded,priority=rank,representative_rule='minimum SHA256(representative-v1 + NUL + id); preserve all official HB standard-test rows',checks=dict(no_cross_group_content_guard_clusters=True,no_test_rows_reallocated=True),limitation='Content guard clusters are conservative lexical/selected semantic exclusions, not a claim of exhaustive semantic independence; no semantic-OOD or training-distribution inference.')
    save('safety_split_g3.json',proposal)
    save('safety_semantic_review_g3.json',dict(reviewer='Codex main agent; not human gold labels',reviewed_scope='30 HB-involving candidate pairs and 22 largest content-overlap groups; selected explicit semantic links below; all other edges governed by fixed lexical rule',candidate_count=len(candidates),content_edges=edges,manual_links=[dict(a=a,b=b,reason=r)for a,b,r in manual],negative_examples=[dict(candidate_index=65,reason='Different scam types; retain both HB official rows; lexical grouping is not semantic identity'),dict(candidate_index=234,reason='Tax fraud and suicide share boilerplate, not requested behavior; removed by content-word guard'),dict(candidate_index=573,reason='Bomb and ransomware share instruction framing; removed by content-word guard')],limitations=['No exhaustive pairwise semantic annotation','Connected components can merge nearby but non-identical tasks; report excluded counts and source composition','No model labels or effects inspected']))
    # E reuses the exact B order and budgets for each training seed.
    train=read('alpaca10k_manifest_g3.json');safe={r['id']:r for r in read('safety_template_token_inventory.json')}
    safe_ids=sorted([x['id']for x in selected['direction_extract']],key=lambda id:sha('safe-cycle-v1\0'+id))
    assert safe_ids
    plans={};summary={}
    for seed in [17,29,43]:
        order=np.random.Generator(np.random.PCG64(seed)).permutation(len(train)).tolist()
        previous_q=0;cumulative=0;cursor=0;updates=[];masked=0;safe_input=0;safe_supervision=0;safe_occurrences=0
        for step in range(625):
            batch=[train[i]for i in order[step*16:(step+1)*16]]
            budget=sum(x['supervised_tokens']for x in batch);cumulative+=budget
            target_q=cumulative//20;quota=target_q-previous_q;previous_q=target_q
            remaining=quota;keep=[x['supervised_tokens']for x in batch]
            # Keep at least one supervised token in every original benign sample.
            for k in range(15,-1,-1):
                take=min(remaining,keep[k]-1);keep[k]-=take;remaining-=take
            assert remaining==0 and min(keep)>0
            masked+=sum(n<x['supervised_tokens']for n,x in zip(keep,batch))
            supplement=[];remaining=quota
            while remaining:
                id=safe_ids[cursor%len(safe_ids)];cursor+=1
                take=min(remaining,safe[id]['supervised_tokens']);remaining-=take
                supplement.append(dict(id=id,keep_supervised_prefix=take))
                safe_input+=safe[id]['total_tokens'];safe_supervision+=take;safe_occurrences+=1
            assert sum(keep)+sum(x['keep_supervised_prefix']for x in supplement)==budget
            updates.append(dict(step=step+1,benign_rows=[r['row']for r in batch],benign_keep_supervised_prefix=keep,safe=supplement,total_supervised=budget,safety_quota=quota))
        assert cumulative==sum(x['supervised_tokens']for x in train)
        assert safe_supervision==cumulative//20
        plans[str(seed)]=updates
        summary[str(seed)]=dict(optimizer_steps=625,total_supervised=cumulative,safe_supervised=safe_supervision,benign_supervised=cumulative-safe_supervision,safety_fraction=safe_supervision/cumulative,benign_input_tokens=sum(r['total_tokens']for r in train),extra_safe_input_tokens=safe_input,extra_safe_occurrences=safe_occurrences,benign_examples_with_partial_supervision=masked,safe_unique_prompts=len(safe_ids),safe_full_response_tokens=sorted({safe[id]['supervised_tokens']for id in safe_ids}),input_ratio_E_to_B=(sum(r['total_tokens']for r in train)+safe_input)/sum(r['total_tokens']for r in train))
    save('E_token_schedule_g3.json',dict(status='CPU_only_exact_token_feasibility_not_training',rng='numpy.Generator(PCG64(seed)).permutation(10000)',quotas='floor(cumulative_supervised/20)-previous_floor',masking='preserve full inputs; retain response-label prefixes; mask excess suffix labels; at least one benign label per row; no cross-example packing',seeds=plans))
    save('E_token_budget_g3.json',dict(summary=summary,checks=dict(equal_supervised_tokens_each_update=True,equal_optimizer_steps=True,no_empty_supervised_examples=True,only_direction_pool_safety_prompts=True),limitation='Input/reference/Adam-update cost is not equal across all methods; this verifies labels and schedules only.'))
    print('split',proposal['counts'],flush=True)
    print('E',json.dumps(summary,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
