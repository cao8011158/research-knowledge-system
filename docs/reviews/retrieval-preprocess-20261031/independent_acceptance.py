"""Read-only acceptance of private input/enrichment and disposable retrieval output."""
import sys,json,sqlite3,hashlib,tempfile,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'kg-builder/src'))
from kg_builder.retrieval_preprocess import get_paper,prepare_index
root=Path(sys.argv[1]).resolve();master=root.parent/'source_identity_20261031/restored/live.sqlite3';index=root/'retrieval_index.sqlite3'
e=json.loads((root/'enrichment.json').read_text());src=sqlite3.connect(master.as_uri()+'?mode=ro',uri=True);db=sqlite3.connect(index.as_uri()+'?mode=ro',uri=True)
checks={}
checks['master_hash_unchanged']=hashlib.sha256(master.read_bytes()).hexdigest()==e['source_backup_sha256']
checks['paper_ids_exact']=src.execute('select paper_id from papers order by paper_id').fetchall()==db.execute('select paper_id from papers order by paper_id').fetchall()
checks['version_rows_exact']=src.execute('select version_id,paper_id,version_label,version_status,published_at,source_url,abstract,abstract_available from paper_versions order by version_id').fetchall()==db.execute('select * from versions order by version_id').fetchall()
checks['integrity']=db.execute('pragma integrity_check').fetchone()[0]=='ok' and not db.execute('pragma foreign_key_check').fetchall()
for w in e['works']:
 p=get_paper(index,w['paper_id']);assert p is not None
 assert p['match_status']==w['match_status']
 if w['match_status']=='matched':
  for f,k in [('topics','openalex_topic'),('keywords','openalex_keyword')]:
   assert {x['id'] for x in w.get(f,[])}=={x['label_id'] for x in p['labels'] if x['kind']==k}
  if w.get('primary_topic'):assert any(x['kind']=='openalex_primary_topic' and x['label_id']==w['primary_topic']['id'] for x in p['labels'])
  for f,k in [('referenced_works','references'),('related_works','related_work')]:assert set(w.get(f,[]))=={x['target_id'] for x in p['edges'] if x['relation']==k}
  assert p['cited_by_count']==w.get('cited_by_count')
 else:assert p['openalex_work_id'] is None
 if w.get('arxiv_status')=='matched':assert set(w.get('arxiv_categories',[]))=={x['name'] for x in p['labels'] if x['origin']=='arxiv_enrichment' and x['kind']=='original_class'}
checks['all_365_enrichment_rows_exact']=True
expected=[]
for eid,pid,vid,pay in src.execute('select extraction_id,paper_id,version_id,payload_json from extraction_records'):
 for i,c in enumerate(json.loads(pay).get('contributions') or []):expected.append((eid,i,pid,vid,json.dumps(c,sort_keys=True,ensure_ascii=False)))
actual=db.execute('select extraction_id,ordinal,paper_id,version_id,payload_json from contributions').fetchall();checks['contributions_exact']=sorted(expected)==sorted(actual)
queries=[];original=sqlite3.connect
class Instrumented(sqlite3.Connection):
 def execute(self,sql,*args,**kwargs):
  if sql.lstrip().upper().startswith('SELECT'):queries.append((sql,args))
  return super().execute(sql,*args,**kwargs)
def measure(path,pid):
 vm=[0]
 def conn(*a,**kw):
  kw['factory']=Instrumented;c=original(*a,**kw);c.set_progress_handler(lambda:vm.__setitem__(0,vm[0]+1) or 0,1);return c
 queries.clear();sqlite3.connect=conn
 try:v=get_paper(path,pid)
 finally:sqlite3.connect=original
 return v,{'vm':vm[0],'selects':len(queries),'reply_bytes':len(json.dumps(v,ensure_ascii=False).encode())},list(queries)
target=next(w['paper_id'] for w in e['works'] if w['match_status']=='matched');a,cold,q=measure(index,target);b,hot,_=measure(index,target)
plans=[]
for sql,args in q:
 plan=db.execute('explain query plan '+sql,*args).fetchall();plans.extend(r[3] for r in plan);assert all('SCAN ' not in r[3] for r in plan)
with tempfile.TemporaryDirectory() as t:
 cp=Path(t)/'scale.sqlite3';shutil.copyfile(index,cp);sc=original(cp)
 for i in range(1000):
  pid='unrelated:'+str(i);sc.execute("insert into papers(paper_id,title,authors_json,match_status,arxiv_status,field_status_json) values(?,?,'[]','unrequested','unrequested','{}')",(pid,'x'*4096))
  sc.execute("insert into labels(paper_id,kind,label_id,name,origin) values(?,'candidate_topic',?,'unrelated','test')",(pid,str(i)))
 sc.commit();sc.close();v,grown,_=measure(cp,target);assert v==a and grown==cold
 miss,missing,_=measure(cp,'missing');assert miss is None and missing['selects']==1
checks['indexed_locality_and_growth']=True
summary={'checks':checks,'cold':cold,'hot':hot,'grown_1000':grown,'missing':missing,'plans':plans,'counts':{t:db.execute('select count(*) from '+t).fetchone()[0] for t in ['papers','versions','sources','labels','edges','contributions','tasks']},'tasks':[list(r) for r in db.execute('select task_kind,reason,count(*) from tasks group by task_kind,reason')],'coverage':[list(r) for r in db.execute('select kind,count(*),count(distinct paper_id) from labels group by kind')],'edges':[list(r) for r in db.execute('select relation,count(*),count(distinct paper_id) from edges group by relation')],'local_reference_links':db.execute("select count(distinct e.paper_id||'>'||a.paper_id) from edges e join aliases a on a.scheme='openalex' and a.value=e.target_id where e.relation='references'").fetchone()[0]}
assert all(checks.values());print(json.dumps(summary,ensure_ascii=False,indent=2))
