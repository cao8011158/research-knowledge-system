"""Measure real extraction-import SQL under fixed target and unrelated growth."""
import argparse,json,sqlite3,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);a=p.parse_args()
sys.path.insert(0,str(a.repo/'src'))
from kg_builder.storage import connect,upsert_paper,ingest_extractions
import tempfile
with tempfile.TemporaryDirectory() as tmp:
 c=connect(Path(tmp)/'locality.sqlite3')
 pid,vid=upsert_paper(c,{'title':'Target','version_label':'v1','url':'https://arxiv.org/abs/2501.00001v1','arxiv_id':'2501.00001'},'test','target','test')
 payload={'paper_id':pid,'version_id':vid,'summary':'A synthetic draft.','methods':[],
          'research_problems':[],'findings':[], 'evidence_locators':[{'source_url':'https://arxiv.org/abs/2501.00001v1','section':'Abstract'}]}
 ingest_extractions(c,[payload])
 results=[]
 for n in (0,1000):
  if n:
   c.executemany('INSERT INTO papers VALUES(?,?,?,?,?,?,?,?,?)',[(f'unrelated:{i}','large unrelated record',None,None,None,None,None,'now','now') for i in range(n)])
   c.executemany('INSERT INTO paper_versions VALUES(?,?,?,?,?,?,?,?,?,?)',[(f'unrelated:{i}@v1',f'unrelated:{i}','v1','source_confirmed',None,'https://example.com','x','x'*16384,1,'now') for i in range(n)])
   c.commit()
  for temperature in ('first','repeat'):
   statements=[];counter=[0]
   def step():counter[0]+=1;return 0
   c.set_trace_callback(statements.append);c.set_progress_handler(step,1)
   ids=ingest_extractions(c,[payload])
   c.set_trace_callback(None);c.set_progress_handler(None,0)
   selects=[s for s in statements if s.lstrip().upper().startswith('SELECT')]
   plans=[row[3] for sql in selects for row in c.execute('EXPLAIN QUERY PLAN '+sql)]
   assert all('SCAN ' not in x for x in plans),plans
   assert len(ids)==1
   results.append({'unrelated_rows':n,'unrelated_abstract_bytes':n*16384,'call':temperature,
                   'vm_instructions':counter[0],'sql_statements':len(statements),
                   'selects':len(selects),'select_rows':sum(len(c.execute(sql).fetchall()) for sql in selects),
                   'plans':plans,'reply_bytes':len(json.dumps(ids).encode())})
 base=results[0]
 for r in results:
  assert r['selects']==base['selects'] and r['select_rows']==base['select_rows']
  assert r['reply_bytes']==base['reply_bytes']
  assert r['vm_instructions']<=base['vm_instructions']+25,(base,r)
 c.close()
print(json.dumps({'public_path':'ingest_extractions -> indexed version ownership and logical extraction lookup -> upsert',
                  'schema_preparation':'package schema validators prepared once per process; per-payload validation is necessary K work',
                  'measurements':results,'scope':'SQLite VM instruction counts; no LLM/network; synthetic unrelated growth, not a graph-scale claim'},indent=2))
