"""Actual v2 leaf/compound lookups and missing targets with unrelated large rows."""
import argparse,json,shutil,sqlite3,sys,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--db',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.repo/'src'))
from kg_builder.entity_resolution import get_resolution_entity,get_resolution_mentions
with tempfile.TemporaryDirectory() as tmp:
 path=Path(tmp)/'growth.sqlite3';shutil.copyfile(a.db,path);c=sqlite3.connect(path);c.execute('PRAGMA foreign_keys=ON')
 batch='entity-resolution-20261031-v2';target=c.execute("SELECT extraction_id FROM entity_resolution_mentions WHERE batch_id=? AND json_extract(payload_json,'$.review_outcome')='composite_label' ORDER BY extraction_id LIMIT 1",(batch,)).fetchone()[0]
 leaf='entity:problem:2502.12110:source-question';measurements=[]
 def measure(n,temp,case):
  sql=[];vm=[0]
  def step():vm[0]+=1;return 0
  c.set_trace_callback(sql.append);c.set_progress_handler(step,1)
  if case=='leaf':r=get_resolution_entity(c,batch,leaf);assert not r['stale']
  elif case=='compound':r=get_resolution_mentions(c,batch,target);assert any(x['review_outcome']=='composite_label' and x['component_entities'] for x in r)
  elif case=='missing_entity':r=get_resolution_entity(c,batch,'absent');assert r['stale'] and r['entity'] is None
  else:r=get_resolution_mentions(c,'absent',target);assert r==[]
  c.set_trace_callback(None);c.set_progress_handler(None,0)
  selects=[s for s in sql if s.lstrip().upper().startswith('SELECT')]
  plans=[row[3] for s in selects for row in c.execute('EXPLAIN QUERY PLAN '+s)]
  assert all('SCAN ' not in plan for plan in plans),plans
  reads=[]
  for s in selects:
   rows=c.execute(s).fetchall();reads.append({'rows':len(rows),'text_bytes':sum(len(v.encode()) for row in rows for v in row if isinstance(v,str)),'source_payload': 'FROM extraction_records' in s})
  if case.startswith('missing'):assert not any(x['source_payload'] for x in reads)
  measurements.append({'unrelated_rows_per_table':n,'unrelated_large_text_bytes':n*16384*3,'temperature':temp,'case':case,'vm_instructions':vm[0],'selects':len(selects),'internal_reads':reads,'reply_bytes':len(json.dumps(r,ensure_ascii=False).encode()),'plans':plans})
 for n in (0,1000):
  if n:
   large=json.dumps({'unrelated':'x'*16384})
   for i in range(n):
    b='unrelated:'+str(i);c.execute('INSERT INTO entity_resolution_batches VALUES(?,?,?,?,?,?)',(b,'research-kg-entity-resolution/0.2','test','now','0'*64,large));c.execute('INSERT INTO entity_resolution_entities VALUES(?,?,?,?,?,?)',(b,'unused','Method','named_concept',None,large));c.execute('INSERT INTO entity_resolution_mentions VALUES(?,?,?,?,?,?,?,?)',(b,target,'Method','/methods/0','0'*64,'pending',None,large))
   c.commit()
  for temp in ('first','repeat'):
   for case in ('leaf','compound','missing_entity','missing_mentions'):measure(n,temp,case)
 for case in ('leaf','compound','missing_entity','missing_mentions'):
  group=[m for m in measurements if m['case']==case];base=group[0]
  for m in group:
   for k in ('selects','internal_reads','reply_bytes'):assert m[k]==base[k],(case,k)
   assert m['vm_instructions']<=base['vm_instructions']+20
 c.close()
print(json.dumps({'scope':'Actual v2 private leaf/compound support and parent closure; indexed SQLite plans/VM/fetched text versus reply bytes. No full graph or server/MCP interface tested.','measurements':measurements},indent=2))
