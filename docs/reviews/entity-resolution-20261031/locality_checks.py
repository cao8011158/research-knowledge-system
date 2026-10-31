"""Real public lookup plans and SQLite VM/returned-byte counts under unrelated growth."""
import argparse,json,sqlite3,sys,tempfile,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--db',type=Path,required=True);a=p.parse_args()
sys.path.insert(0,str(a.repo/'src'))
from kg_builder.entity_resolution import get_resolution_mentions
with tempfile.TemporaryDirectory() as tmp:
 path=Path(tmp)/'growth.sqlite3';shutil.copyfile(a.db,path)
 c=sqlite3.connect(path);c.execute('PRAGMA foreign_keys=ON')
 batch=c.execute('SELECT batch_id FROM entity_resolution_batches').fetchone()[0]
 target=c.execute("SELECT extraction_id FROM entity_resolution_mentions WHERE entity_id='entity:method:grpo' ORDER BY extraction_id LIMIT 1").fetchone()[0]
 measurements=[]
 def measure(n,mode,requested_batch):
  sql=[];counter=[0]
  def vm():counter[0]+=1;return 0
  c.set_trace_callback(sql.append);c.set_progress_handler(vm,1)
  result=get_resolution_mentions(c,requested_batch,target)
  c.set_trace_callback(None);c.set_progress_handler(None,0)
  selects=[s for s in sql if s.lstrip().upper().startswith('SELECT')]
  plans=[r[3] for s in selects for r in c.execute('EXPLAIN QUERY PLAN '+s)]
  assert not any('SCAN ' in plan for plan in plans)
  details=[]
  for s in selects:
   rows=c.execute(s).fetchall()
   details.append({'table':'extraction_records' if 'FROM extraction_records' in s else 'entity_resolution_entities' if 'FROM entity_resolution_entities' in s else 'entity_resolution_mentions','rows':len(rows),'text_bytes':sum(len(v.encode()) for row in rows for v in row if isinstance(v,str))})
  if requested_batch!=batch:assert result==[] and all(d['table']=='entity_resolution_mentions' for d in details)
  else:assert result and not any(r['stale'] for r in result)
  measurements.append({'unrelated_batches_entities_mentions':n,'unrelated_large_payload_bytes':n*16384*3,'mode':mode,'query': 'matching' if requested_batch==batch else 'absent_batch','vm_instructions':counter[0],'sql_statements':len(sql),'selects':len(selects),'internal_reads':details,'result_mentions':len(result),'reply_bytes':len(json.dumps(result,ensure_ascii=False).encode()),'plans':plans})
 for n in (0,1000):
  if n:
   big=json.dumps({'unrelated':'x'*16384})
   for i in range(n):
    b='unrelated:'+str(i)
    c.execute('INSERT INTO entity_resolution_batches VALUES(?,?,?,?,?,?)',(b,'unrelated','test','now','0'*64,big))
    c.execute('INSERT INTO entity_resolution_entities VALUES(?,?,?,?,?,?)',(b,'other','Method','named_concept',None,big))
    c.execute('INSERT INTO entity_resolution_mentions VALUES(?,?,?,?,?,?,?,?)',(b,target,'Method','/methods/0','0'*64,'resolved','other',big))
   c.commit()
  for mode in ('first','repeat'):
   measure(n,mode,batch);measure(n,mode,'absent')
 for query in ('matching','absent_batch'):
  rs=[r for r in measurements if r['query']==query];base=rs[0]
  for r in rs:
   for key in ('selects','internal_reads','result_mentions','reply_bytes'):assert r[key]==base[key],(key,base,r)
   assert r['vm_instructions']<=base['vm_instructions']+20,(base,r)
 c.close()
print(json.dumps({'public_path':'get_resolution_mentions -> composite mention index -> requested extraction PK -> referenced entity PK -> exact support extraction PK closure','scope':'Synthetic unrelated growth around the actual27entity/74mention review. VM counts plus fetched-text bytes; no graph-scale claim.','measurements':measurements},indent=2))
