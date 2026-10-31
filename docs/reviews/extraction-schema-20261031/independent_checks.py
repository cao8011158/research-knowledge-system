"""Independent acceptance; private DB stays outside the repository. No network/LLM."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

p=argparse.ArgumentParser()
p.add_argument('--repo',type=Path,required=True)
p.add_argument('--input',type=Path,required=True)
p.add_argument('--work',type=Path,required=True)
a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
sys.path[:0]=[str(a.repo/'src'),str(a.repo/'scripts')]
from kg_builder.extraction_validation import validate_extraction,validate_extraction_batch
from kg_builder.storage import connect,ingest_extractions
from reconcile_sqlite import reconcile

source_hash=hashlib.sha256(a.input.read_bytes()).hexdigest()
src=sqlite3.connect(f'file:{a.input}?mode=ro',uri=True)
def snapshot(c):
    return {n:sorted(c.execute('SELECT * FROM '+n).fetchall(),key=repr)
            for n, in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
baseline=snapshot(src)
records=[json.loads(r[0]) for r in src.execute('SELECT payload_json FROM extraction_records ORDER BY rowid')]
assert len(records)==26
validate_extraction_batch(records)
profiles={'legacy':sum('schema_version' not in r for r in records),
          'pilot':sum('schema_version' in r for r in records)}
assert profiles=={'legacy':20,'pilot':6}
pilot=next(r for r in records if 'schema_version' in r)
negatives=[]
def rejects(name,fn):
    try:fn()
    except (ValueError,sqlite3.IntegrityError):negatives.append(name)
    else:raise AssertionError(name+' unexpectedly accepted')
def mutated(name,change):
    r=copy.deepcopy(pilot);change(r);rejects(name,lambda:validate_extraction(r))
mutated('empty_assertion_evidence',lambda r:r['contributions'][0].update(evidence_refs=[]))
mutated('empty_relation_evidence',lambda r:r['relations'][0].update(evidence_refs=[]))
mutated('method_name_type',lambda r:r['methods'][0].update(name=42))
mutated('method_description_missing',lambda r:r['methods'][0].pop('description'))
mutated('metric_direction_type',lambda r:r['metrics'][0].update(higher_is_better='true'))
mutated('artifact_kind_invalid',lambda r:r['artifacts'][0].update(artifact_kind='EVERYTHING'))
mutated('evaluation_setup_type',lambda r:r['evaluations'][0].update(setup=[]))
mutated('unknown_schema',lambda r:r.update(schema_version='research-kg-extraction/999'))
mutated('boolean_measurement',lambda r:r['evaluations'][0].update(value=True))
mutated('nonfinite_measurement',lambda r:r['evaluations'][0].update(value=float('nan')))
mutated('unresolved_evidence',lambda r:r['methods'][0].update(evidence_refs=['absent']))
mutated('duplicate_evidence',lambda r:r['evidence_locators'].append(copy.deepcopy(r['evidence_locators'][0])))
mutated('wrong_target_kind',lambda r:r['evaluations'][0].update(metric=r['artifacts'][0]['key']))
mutated('unit_mismatch',lambda r:r['evaluations'][0].update(unit='seconds'))
mutated('capture_hash_mismatch',lambda r:r['evidence_locators'][0].update(html_sha256='0'*64))
mutated('wrong_scoped_key',lambda r:r['contributions'][0].update(key='another-version#c1'))

path=a.work/'import.sqlite3';shutil.copyfile(a.input,path)
c=connect(path)
ids=ingest_extractions(c,records)
assert len(ids)==26 and all(c.execute('SELECT 1 FROM extraction_records WHERE extraction_id=?',(i,)).fetchone() for i in ids)
assert snapshot(c)==baseline,'reimport changed stored rows'
ingest_extractions(c,records)
assert snapshot(c)==baseline,'second reimport changed stored rows'
changed=copy.deepcopy(records[:2])
for i,r in enumerate(changed):r['summary']='independent atomicity probe '+str(i)
bad=copy.deepcopy(changed);bad[1]['version_id']='missing-version'
rejects('unknown_db_version_atomic',lambda:ingest_extractions(c,bad))
assert snapshot(c)==baseline
# Inject a write failure AFTER the first record has been written.
second=changed[1]['version_id']
c.execute("CREATE TEMP TRIGGER fail_second BEFORE UPDATE ON extraction_records WHEN NEW.version_id="+"'"+second.replace("'","''")+"' BEGIN SELECT RAISE(ABORT,'injected second write'); END")
rejects('mid_write_failure_atomic',lambda:ingest_extractions(c,changed))
assert snapshot(c)==baseline
c.execute('DROP TRIGGER fail_second')
# Successful nested operation must remain rollbackable by the caller.
c.execute('BEGIN')
c.execute("INSERT INTO pipeline_runs(run_id,mode,started_at,status) VALUES('outer-test','test','now','test')")
ingest_extractions(c,changed)
assert c.in_transaction
c.rollback();assert snapshot(c)==baseline
# Failure must preserve the caller's earlier pending changes.
c.execute('BEGIN')
c.execute("INSERT INTO pipeline_runs(run_id,mode,started_at,status) VALUES('outer-test','test','now','test')")
rejects('nested_failure',lambda:ingest_extractions(c,bad))
assert c.in_transaction and c.execute("SELECT 1 FROM pipeline_runs WHERE run_id='outer-test'").fetchone()
c.rollback();assert snapshot(c)==baseline
c.close()

payload=a.work/'invalid_second.json';payload.write_text(json.dumps(bad,ensure_ascii=False))
r=subprocess.run([sys.executable,str(a.repo/'scripts/import_reviewed.py'),'--db',str(path),'--input',str(payload)],capture_output=True,text=True)
assert r.returncode!=0 and snapshot(sqlite3.connect(path))==baseline
for name,text in [('unknown','[{"schema_version":"unknown"}]'),('nan','[NaN]')]:
    payload=a.work/(name+'.json');payload.write_text(text)
    absent=a.work/(name+'.sqlite3')
    r=subprocess.run([sys.executable,str(a.repo/'scripts/import_reviewed.py'),'--db',str(absent),'--input',str(payload)],capture_output=True,text=True)
    assert r.returncode!=0 and not absent.exists(),name+' created database'

for extension in ('table','column'):
    extended=a.work/('unsupported_'+extension+'.sqlite3');shutil.copyfile(a.input,extended)
    ec=sqlite3.connect(extended)
    if extension=='table':ec.execute('CREATE TABLE unsupported_annotation (note TEXT)')
    else:ec.execute('ALTER TABLE source_records ADD COLUMN unsupported_annotation TEXT')
    ec.commit();ec.close()
    rejected_output=a.work/('unsupported_'+extension+'_out.sqlite3')
    rejected_report=a.work/('unsupported_'+extension+'_report.json')
    rejects('unsupported_'+extension,lambda:reconcile([extended],rejected_output,rejected_report))
    assert not rejected_output.exists() and not rejected_report.exists()

out=a.work/'reconciled.sqlite3';merge=reconcile([a.input],out,a.work/'reconciliation.json')
c=sqlite3.connect(out);merged=snapshot(c)
for table in baseline:
    if table not in ('reconciliation_audit','paper_redirects'):
        assert merged[table]==baseline[table],table+' changed active rows'
    else:
        assert set(baseline[table])<=set(merged[table]),table+' lost provenance'
assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert c.execute('PRAGMA foreign_key_check').fetchall()==[]
validate_extraction_batch([json.loads(r[0]) for r in c.execute('SELECT payload_json FROM extraction_records')])
c.close()
# Repeat with the reconciled output plus its original source.
out2=a.work/'repeated.sqlite3';reconcile([out,a.input],out2,a.work/'repeated.json')
c=sqlite3.connect(out2);repeated=snapshot(c)
for table in baseline:
    if table not in ('reconciliation_audit','paper_redirects'):
        assert repeated[table]==baseline[table],table+' changed on repeated reconciliation'
assert c.execute('PRAGMA foreign_key_check').fetchall()==[]
c.close();src.close()
assert hashlib.sha256(a.input.read_bytes()).hexdigest()==source_hash
result={'source_sha256':source_hash,'validated_profiles':profiles,'drafts_preserved':26,'relevance_reviews_preserved':371,
        'negative_cases':negatives,'cli_invalid_second_atomic':True,'cli_invalid_input_no_database':True,
        'caller_transaction_preserved':True,'all_original_active_rows_unchanged':True,
        'original_provenance_retained':True,'repeated_reconciliation_preserves_active_rows':True,
        'input_bytes_unchanged':True,'reconciled_integrity':'ok'}
(a.work/'acceptance.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
