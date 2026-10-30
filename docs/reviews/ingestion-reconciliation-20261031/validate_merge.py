import sqlite3,json,hashlib,sys
from pathlib import Path
report=json.loads(Path(sys.argv[1]).read_text())
p=Path(report['output']); out=sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True);out.row_factory=sqlite3.Row
assert out.execute('pragma integrity_check').fetchone()[0]=='ok'
assert not out.execute('pragma foreign_key_check').fetchall()
assert out.execute("select count(*) from papers p left join paper_versions v on v.version_id=p.current_version_id where p.current_version_id is not null and (v.version_id is null or v.paper_id<>p.paper_id or v.version_status<>'source_confirmed')").fetchone()[0]==0
assert not report['conflicts'],report['conflicts']
for inp in report['inputs']:
 assert hashlib.sha256(Path(inp['path']).read_bytes()).hexdigest()==inp['sha256']
 src=sqlite3.connect('file:'+inp['path']+'?mode=ro',uri=True);src.row_factory=sqlite3.Row
 pm={r['original_paper_id']:r['paper_id'] for r in report['paper_mapping'] if r['input']==inp['path']}
 vm={r['original_version_id']:r['version_id'] for r in report['version_mapping'] if r['input']==inp['path']}
 for r in src.execute('select * from source_records'):
  actual=out.execute('select paper_id from source_records where source_name=? and source_id=?',(r['source_name'],r['source_id'])).fetchone()
  assert actual and actual[0]==pm[r['paper_id']]
  preserved=out.execute("select count(*) from reconciliation_audit where input_sha256=? and table_name='source_records' and json_extract(original_json,'$.payload_hash')=?",(inp['sha256'],r['payload_hash'])).fetchone()[0]
  assert preserved
 for r in src.execute('select * from extraction_records'):
  actual=out.execute('select * from extraction_records where paper_id=? and version_id=? and extractor_type=? and extractor_version=?',(pm[r['paper_id']],vm[r['version_id']],r['extractor_type'],r['extractor_version'])).fetchone()
  assert actual and actual['status']==r['status']
  payload=json.loads(actual['payload_json']);original=json.loads(r['payload_json'])
  assert payload['paper_id']==actual['paper_id'] and payload['version_id']==actual['version_id']
  for k,v in original.items():
   if k not in ('paper_id','version_id'): assert payload[k]==v,(k,payload[k],v)
 src.close()
print(json.dumps({'integrity':'ok','foreign_keys':'ok','input_hashes_unchanged':True,'all_source_payloads_audited':True,'all_extraction_content_status_preserved':True,'confirmed_current_pointers_only':True,'counts':report['counts']},indent=2))
out.close()
