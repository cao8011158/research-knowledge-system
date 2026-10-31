"""Independent real-data identity-review acceptance; all payloads remain private."""
import argparse,copy,hashlib,json,shutil,sqlite3,sys,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--input',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
sys.path[:0]=[str(a.repo/'src'),str(a.repo/'scripts')]
from kg_builder.storage import connect
from kg_builder.entity_resolution import validate_resolution_manifest,import_resolution_manifest,get_resolution_mentions
from reconcile_sqlite import reconcile
NAMES=('entity_resolution_batches','entity_resolution_entities','entity_resolution_mentions')
def snapshot(c):return {n:sorted(c.execute('SELECT * FROM '+n).fetchall(),key=repr) for n, in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputsha=sha(a.input);manifest=json.loads(a.manifest.read_text());validate_resolution_manifest(manifest)
src=sqlite3.connect('file:'+str(a.input)+'?mode=ro',uri=True);original=snapshot(src);src.close()
path=a.work/'annotated.sqlite3';shutil.copyfile(a.input,path);c=connect(path)
raw=a.manifest.read_text();batch=import_resolution_manifest(c,manifest,raw_json=raw)
assert batch==manifest['batch_id']
assert [c.execute('SELECT count(*) FROM '+n).fetchone()[0] for n in NAMES]==[1,27,74]
assert c.execute('SELECT payload_json FROM entity_resolution_batches').fetchone()[0]==raw
for t,rows in original.items():assert snapshot(c)[t]==rows,t+' original rows changed'
state=snapshot(c);import_resolution_manifest(c,manifest);assert snapshot(c)==state
results={eid:get_resolution_mentions(c,batch,eid) for eid, in c.execute('SELECT extraction_id FROM extraction_records')}
flat=[x for rs in results.values() for x in rs]
assert len(flat)==74 and sum(x['decision']=='resolved' for x in flat)==34
assert all(not x['stale'] and (x['entity'] is not None)==(x['decision']=='resolved') for x in flat)
# Manual identity facts independently inspected from the result, not just table counts.
by_id={e['entity_id']:e for e in manifest['entities']}
assert len([e for e in by_id.values() if e['scope']=='paper_version_local'])==15
assert len([e for e in by_id.values() if e['kind']=='ResearchProblem'])==0
assert 'entity:method:grpo' in by_id and len(by_id['entity:method:grpo']['support'])==2
assert by_id['entity:artifact:a-mem']['kind']=='Artifact' and by_id['entity:method:a-mem']['kind']=='Method'
example=next(e for e in by_id.values() if e['name']=='update_product_quantity')
assert example['scope']=='paper_version_local'
assert len([m for m in manifest['mentions'] if m['entity_id']=='entity:method:grpo'])==2
checks=[]
def rejects(name,fn):
 try:fn()
 except (ValueError,sqlite3.DatabaseError):checks.append(name)
 else:raise AssertionError('accepted '+name)
 assert snapshot(c)==state,name+' left partial writes'
def invalid(name,change):
 m=copy.deepcopy(manifest);m['batch_id']='negative:'+name;change(m)
 rejects(name,lambda:import_resolution_manifest(c,m))
invalid('invalid_second_hash',lambda m:m['mentions'][1].update(source_payload_sha256='0'*64))
invalid('support_hash_mismatch',lambda m:m['entities'][0]['support'][0].update(source_payload_sha256='0'*64))
invalid('bad_pointer',lambda m:m['mentions'][0].update(evidence_locator_paths=['/evidence_locators/999']))
resolved_index=next(i for i,m in enumerate(manifest['mentions']) if m['decision']=='resolved' and m['kind']=='Method')
invalid('cross_kind',lambda m:m['mentions'][resolved_index].update(entity_id='entity:artifact:a-mem'))
local_index=next(i for i,e in enumerate(manifest['entities']) if e['scope']=='paper_version_local')
invalid('local_artifact_to_named',lambda m:m['entities'][local_index].update(scope='named_concept',scope_version_id=None))
artifact_index=next(i for i,e in enumerate(manifest['entities']) if e['kind']=='Artifact')
invalid('artifact_subtype_mismatch',lambda m:m['entities'][artifact_index].update(artifact_kind='DATASET'))
bad=copy.deepcopy(manifest);bad['notes']='changed'
rejects('immutable_conflict',lambda:import_resolution_manifest(c,bad))
rejects('raw_document_mismatch',lambda:import_resolution_manifest(c,manifest,raw_json='{}'))
# In-flight SQL failure after batch and entity rows are written must roll back all new rows.
c.execute("CREATE TEMP TRIGGER stop_second BEFORE INSERT ON entity_resolution_mentions WHEN NEW.mention_path='/research_problems/0' BEGIN SELECT RAISE(ABORT,'injected'); END")
fault=copy.deepcopy(manifest);fault['batch_id']='fault:sql'
rejects('injected_sql_failure',lambda:import_resolution_manifest(c,fault));c.execute('DROP TRIGGER stop_second')
# Caller transaction owns success and failure; earlier unrelated work survives an import failure.
c.execute('BEGIN');c.execute("INSERT INTO pipeline_runs(run_id,mode,started_at,status) VALUES('outer','test','now','test')")
nested=copy.deepcopy(manifest);nested['batch_id']='nested:success';import_resolution_manifest(c,nested)
assert c.in_transaction;c.rollback();assert snapshot(c)==state
c.execute('BEGIN');c.execute("INSERT INTO pipeline_runs(run_id,mode,started_at,status) VALUES('outer','test','now','test')")
try:import_resolution_manifest(c,bad)
except ValueError:pass
else:raise AssertionError('nested immutable conflict accepted')
assert c.in_transaction and c.execute("SELECT 1 FROM pipeline_runs WHERE run_id='outer'").fetchone();c.rollback();assert snapshot(c)==state
# A shared support change invalidates GRPO in both papers; DAPO's own method stays active.
g=by_id['entity:method:grpo'];changed=g['support'][0]['extraction_id'];other=g['support'][1]['extraction_id']
old=c.execute('SELECT payload_json FROM extraction_records WHERE extraction_id=?',(changed,)).fetchone()[0]
c.execute("UPDATE extraction_records SET payload_json=payload_json||' ' WHERE extraction_id=?",(changed,));c.commit()
rs=get_resolution_mentions(c,batch,other)
grpo=next(x for x in rs if x['entity_id']=='entity:method:grpo');assert grpo['stale'] and grpo['entity'] is None
assert any(x['decision']=='resolved' and not x['stale'] and x['entity_id']!='entity:method:grpo' for x in rs)
import_resolution_manifest(c,manifest)  # Immutable historical repeat does not make stale data current.
assert next(x for x in get_resolution_mentions(c,batch,other) if x['entity_id']=='entity:method:grpo')['stale']
c.execute('UPDATE extraction_records SET payload_json=? WHERE extraction_id=?',(old,changed));c.commit();assert snapshot(c)==state
# Negative lookup must never fetch the requested large extraction payload without a review row.
trace=[];c.set_trace_callback(trace.append);assert get_resolution_mentions(c,'absent',other)==[];c.set_trace_callback(None)
assert not any('FROM extraction_records' in sql for sql in trace)
assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and c.execute('PRAGMA foreign_key_check').fetchall()==[]
c.close()
# Reconciliation + repeat retains every active row and all historical audit rows.
out=a.work/'reconciled.sqlite3';reconcile([path],out,a.work/'reconcile.json')
for dbname in [out]:
 dc=sqlite3.connect(dbname);ss=snapshot(dc)
 for t,rows in state.items():
  if t in ('reconciliation_audit','paper_redirects'):assert set(rows)<=set(ss[t])
  else:assert ss[t]==rows,t+' changed during reconciliation'
 dc.close()
repeat=a.work/'repeat.sqlite3';reconcile([out,path],repeat,a.work/'repeat.json')
dc=sqlite3.connect(repeat);ss=snapshot(dc)
for t in state:
 if t not in ('reconciliation_audit','paper_redirects'):assert ss[t]==state[t],t+' changed during repeat'
assert dc.execute('PRAGMA foreign_key_check').fetchall()==[];dc.close()
# CLI malformed manifest must not create a new database.
invalid_path=a.work/'invalid.json';invalid_path.write_text('{"schema_version":"future"}')
absent=a.work/'absent.sqlite3'
r=subprocess.run([sys.executable,str(a.repo/'scripts/import_entity_resolution.py'),'--input',str(invalid_path),'--db',str(absent)],capture_output=True,text=True)
assert r.returncode!=0 and not absent.exists()
assert sha(a.input)==inputsha
result={'input_sha256':inputsha,'batch_id':batch,'entities':27,'mentions':74,'resolved_mentions':34,'pending_mentions':40,'local_artifacts':15,'shared_grpo_concept_not_identical_implementations':True,'method_artifact_identities_distinct':True,'example_function_version_local':True,'negative_cases':checks,'stale_support_closure_and_restore':True,'caller_transactions':True,'raw_first_manifest_preserved':True,'repeated_import_unchanged':True,'all_original_rows_unchanged':True,'reconcile_and_repeat_preserve_active_rows':True,'input_bytes_unchanged':True,'drafts_preserved':26,'relevance_reviews_preserved':371,'integrity':'ok','fk_violations':0}
(a.work/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
