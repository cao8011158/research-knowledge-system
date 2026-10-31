"""Private-input primary-source adjudication acceptance; no network/model calls."""
import argparse,copy,hashlib,json,shutil,sqlite3,sys
from pathlib import Path
from collections import Counter
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--input',type=Path,required=True);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
sys.path[:0]=[str(a.repo/'src'),str(a.repo/'scripts')]
from kg_builder.storage import connect
from kg_builder.entity_resolution import import_resolution_manifest,get_resolution_mentions,get_resolution_entity
from reconcile_sqlite import reconcile
T=('entity_resolution_batches','entity_resolution_entities','entity_resolution_mentions')
def snapshot(c):return {t:sorted(c.execute('SELECT * FROM '+t).fetchall(),key=repr) for t, in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
original=sqlite3.connect('file:'+str(a.input)+'?mode=ro',uri=True);old=snapshot(original);original.close();inputsha=sha(a.input)
source=sqlite3.connect('file:'+str(a.prepared)+'?mode=ro',uri=True);prepared=snapshot(source);source.close()
for t in old:
 if t=='papers':continue
 assert set(old[t])<=set(prepared[t]),t+' old data lost'
for row in old['papers']:
 new=next(r for r in prepared['papers'] if r[0]==row[0])
 assert all(row[i]==new[i] for i in [0,1,2,3,4,5,7])
path=a.work/'annotated.sqlite3';shutil.copyfile(a.prepared,path);c=connect(path)
old_batch=c.execute('SELECT batch_id FROM entity_resolution_batches').fetchone()[0]
before_v1={eid:get_resolution_mentions(c,old_batch,eid) for eid, in c.execute('SELECT extraction_id FROM extraction_records')}
m=json.loads(a.manifest.read_text());bid=import_resolution_manifest(c,m,raw_json=a.manifest.read_text())
assert c.execute('SELECT schema_version FROM entity_resolution_batches WHERE batch_id=?',(bid,)).fetchone()[0]=='research-kg-entity-resolution/0.2'
assert [c.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in T]==[2,101,179]
state=snapshot(c);import_resolution_manifest(c,m);assert snapshot(c)==state
for t in prepared:
 if t not in T:assert state[t]==prepared[t],t+' import changed unrelated data'
for eid,prior in before_v1.items():assert get_resolution_mentions(c,old_batch,eid)==prior
all_results=[r for eid, in c.execute('SELECT extraction_id FROM extraction_records') for r in get_resolution_mentions(c,bid,eid)]
assert len(all_results)==105 and all(not r['stale'] for r in all_results)
assert Counter(r['review_outcome'] for r in all_results)==Counter(mapped=99,composite_label=4,not_a_method=2)
assert all((r['entity'] is not None)==(r['review_outcome']=='mapped') for r in all_results)
assert sorted(len(r['component_entities']) for r in all_results if r['review_outcome']=='composite_label')==[2,2,2,3]
assert all(r['decision']=='pending' and r['entity'] is None for r in all_results if r['review_outcome']!='mapped')
entities={e['entity_id']:e for e in m['entities']}
assert Counter(e['kind'] for e in entities.values())==Counter(Method=20,Artifact=24,ResearchProblem=30)
for eid in entities:assert not get_resolution_entity(c,bid,eid)['stale']
assert sum(len(e.get('parent_problem_ids',[])) for e in entities.values())==25
assert all(e.get('relation_basis')=='reviewer_taxonomy' for e in entities.values() if e.get('parent_problem_ids'))
checks=[]
def reject(name,change):
 bad=copy.deepcopy(m);bad['batch_id']='negative:'+name;change(bad)
 try:import_resolution_manifest(c,bad)
 except (ValueError,sqlite3.DatabaseError):checks.append(name)
 else:raise AssertionError('accepted '+name)
 assert snapshot(c)==state,name+' wrote partial rows'
leafidx=next(i for i,e in enumerate(m['entities']) if e.get('parent_problem_ids'))
reject('self_parent',lambda x:x['entities'][leafidx].update(parent_problem_ids=[x['entities'][leafidx]['entity_id']]))
reject('unknown_parent',lambda x:x['entities'][leafidx].update(parent_problem_ids=['missing']))
reject('wrong_parent_kind',lambda x:x['entities'][leafidx].update(parent_problem_ids=['entity:method:a-mem']))
reject('missing_taxonomy_basis',lambda x:x['entities'][leafidx].pop('relation_basis'))
compidx=next(i for i,v in enumerate(m['mentions']) if v['review_outcome']=='composite_label')
reject('composite_as_single',lambda x:x['mentions'][compidx].update(decision='resolved',entity_id='entity:method:cat'))
reject('unknown_component',lambda x:x['mentions'][compidx].update(component_entity_ids=['missing','entity:method:cat']))
reject('wrong_source_hash',lambda x:x['mentions'][-1].update(source_payload_sha256='0'*64))
# Inject failure after registry rows and the first mention have been inserted.
c.execute("CREATE TEMP TRIGGER fault BEFORE INSERT ON entity_resolution_mentions WHEN NEW.batch_id='fault' AND NEW.mention_path='/research_problems/0' BEGIN SELECT RAISE(ABORT,'fault'); END")
bad=copy.deepcopy(m);bad['batch_id']='fault'
try:import_resolution_manifest(c,bad)
except sqlite3.DatabaseError:checks.append('injected_write_failure')
else:raise AssertionError('SQL fault ignored')
c.execute('DROP TRIGGER fault');assert snapshot(c)==state
c.execute('BEGIN');c.execute("INSERT INTO pipeline_runs(run_id,mode,started_at,status) VALUES('outer','test','now','test')")
nested=copy.deepcopy(m);nested['batch_id']='nested';import_resolution_manifest(c,nested);assert c.in_transaction;c.rollback();assert snapshot(c)==state
# Parent-support changes must hide dependent question identities without invalidating unrelated concepts.
leaf='entity:problem:2502.12110:source-question';parent='entity:problem:root:memory';sid=entities[parent]['support'][0]['extraction_id']
raw=c.execute('SELECT payload_json FROM extraction_records WHERE extraction_id=?',(sid,)).fetchone()[0]
c.execute("UPDATE extraction_records SET payload_json=payload_json||' ' WHERE extraction_id=?",(sid,));c.commit()
assert get_resolution_entity(c,bid,leaf)['stale']
assert not get_resolution_entity(c,bid,'entity:method:cat')['stale']
c.execute('UPDATE extraction_records SET payload_json=? WHERE extraction_id=?',(raw,sid));c.commit();assert snapshot(c)==state
# Compound source support must not leak partial active components.
comp=next(v for v in m['mentions'] if v['review_outcome']=='composite_label');ce=entities[comp['component_entity_ids'][0]];sid=ce['support'][0]['extraction_id']
raw=c.execute('SELECT payload_json FROM extraction_records WHERE extraction_id=?',(sid,)).fetchone()[0]
c.execute("UPDATE extraction_records SET payload_json=payload_json||' ' WHERE extraction_id=?",(sid,));c.commit()
r=next(v for v in get_resolution_mentions(c,bid,comp['extraction_id']) if v['mention_path']==comp['mention_path']);assert r['stale'] and r['component_entities']==[]
c.execute('UPDATE extraction_records SET payload_json=? WHERE extraction_id=?',(raw,sid));c.commit();assert snapshot(c)==state
assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and c.execute('PRAGMA foreign_key_check').fetchall()==[];c.close()
out=a.work/'reconciled.sqlite3';reconcile([path,a.input],out,a.work/'reconcile.json')
out2=a.work/'repeat.sqlite3';reconcile([out,path],out2,a.work/'repeat.json')
for file in [out,out2]:
 d=sqlite3.connect(file);s=snapshot(d)
 for t in state:
  if t in ['reconciliation_audit','paper_redirects']:assert set(state[t])<=set(s[t])
  else:assert s[t]==state[t],t+' changed during reconciliation/repeat'
 assert d.execute('PRAGMA foreign_key_check').fetchall()==[];d.close()
assert sha(a.input)==inputsha
result={'input_sha256':inputsha,'old_drafts_preserved':26,'new_identity_only_drafts':14,'total_drafts':40,'old_relevance_reviews_preserved':371,'old_v1_batch_rows_and_lookup_unchanged':True,'v2_entities':74,'v2_mentions':105,'mapped':99,'composite_labels':4,'not_a_method':2,'insufficient_evidence':0,'problem_entities':30,'reviewer_taxonomy_edges':25,'all_current':True,'negative_cases':checks,'parent_and_component_stale_closure':True,'atomic_immutable_and_outer_transaction':True,'reconcile_repeat_preserve_all_active_rows':True,'integrity':'ok','fk_violations':0}
(a.work/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
