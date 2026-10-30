import sqlite3,tempfile,sys,json,hashlib
from pathlib import Path
root=Path(sys.argv[1]);sys.path[:0]=[str(root/'src'),str(root/'scripts')]
from kg_builder.storage import connect,upsert_paper,identities
from reconcile_sqlite import reconcile
with tempfile.TemporaryDirectory() as td:
 d=Path(td);c=connect(d/'input.db')
 a,av=upsert_paper(c,{'title':'same','arxiv_id':'2501.12345','version_label':'v10'},'arxiv','A','q')
 b,bv=upsert_paper(c,{'title':'same','doi':'10.1234/other'},'oa','B','q')
 assert a!=b,'title-only merge'
 before=list(c.iterdump())
 try:upsert_paper(c,{'title':'bad','doi':'10.1234/new','version_label':'v0'},'oa','bad','q')
 except ValueError:pass
 else:raise AssertionError('invalid confirmed label accepted')
 assert list(c.iterdump())==before,'partial write escaped rollback'
 try:identities({'arxiv_id':'2501.12345','doi':'10.48550/arxiv.2502.12345'})
 except ValueError:pass
 else:raise AssertionError('contradictory record accepted')
 assert identities({'source_payload':{'primary_location':{'landing_page_url':'https://arxiv.org/abs/2501.12345v10'}}})[1]=='2501.12345'
 # Public upsert cost measured after 0 and 1000 irrelevant papers, no helper mocks.
 def measure():
  stats={'vm_instructions':0,'sql_statements':0}
  def progress():stats['vm_instructions']+=1;return 0
  def trace(sql):stats['sql_statements']+=1
  c.set_progress_handler(progress,1);c.set_trace_callback(trace)
  returned=upsert_paper(c,{'title':'same','arxiv_id':'2501.12345','version_label':'v2'},'arxiv','A2','q')
  c.set_progress_handler(None,0);c.set_trace_callback(None)
  assert c.execute('select current_version_id from papers where paper_id=?',(a,)).fetchone()[0]==av
  stats['returned_identifiers']=len(returned);stats['output_bytes']=len(json.dumps(returned).encode());return stats
 measure() # initialize target v2 / source entry
 small=measure()
 for i in range(1000):upsert_paper(c,{'title':str(i),'doi':f'10.1234/noise{i}'},'oa',f'noise{i}','q')
 large=measure();assert large['sql_statements']==small['sql_statements'];assert large['vm_instructions'] < small['vm_instructions']*1.2+20,(small,large)
 plans={}
 for name,sql,args in [('arxiv','select paper_id from papers where arxiv_id=?',('2501.12345',)),('source','select paper_id from source_records where source_name=? and source_id=?',('arxiv','A')),('doi','select paper_id from papers where doi=?',('10.1234/other',)),('alias','select paper_id from paper_doi_aliases where doi=?',('10.1234/other',))]:
  plans[name]=[r[3] for r in c.execute('explain query plan '+sql,args)];assert all('SCAN ' not in s for s in plans[name])
 c.close();sha=hashlib.sha256((d/'input.db').read_bytes()).hexdigest()
 r=reconcile([d/'input.db'],d/'out.db',d/'r.json')
 r2=reconcile([d/'out.db',d/'input.db'],d/'out2.db',d/'r2.json')
 for table in ('papers','paper_versions','source_records','discovery_hits','extraction_records'):assert r['counts'][table]==r2['counts'][table],table
 assert hashlib.sha256((d/'input.db').read_bytes()).hexdigest()==sha
 print(json.dumps({'checks':'pass','same_title_separate':True,'invalid_version_atomic_rollback':True,'contradictory_record_rejected':True,'source_url_identity':True,'old_version_no_downgrade':True,'remerge_core_counts_idempotent':True,'input_bytes_unchanged':True,'locality_small':small,'locality_plus1000_unrelated':large,'query_plans':plans},indent=2))
