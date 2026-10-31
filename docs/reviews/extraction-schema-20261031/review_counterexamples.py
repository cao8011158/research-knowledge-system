"""Synthetic public reconciliation and evidence-attribution regressions."""
import argparse,json,sqlite3,sys,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--expect-fixed',action='store_true');a=p.parse_args()
sys.path[:0]=[str(a.repo/'src'),str(a.repo/'scripts'),str(a.repo/'tests')]
from kg_builder.storage import connect,upsert_paper,ingest_extraction
from kg_builder.extraction_validation import validate_extraction
from reconcile_sqlite import reconcile
from test_extraction_validation import draft
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);first=root/'first.sqlite3';second=root/'second.sqlite3'
 c=connect(first)
 p1,v1=upsert_paper(c,{'title':'Synthetic work','doi':'10.1234/shared','version_label':'v1','url':'https://example.com/paper/v1'},'s','a','q');c.close()
 c=connect(second)
 p2,v2=upsert_paper(c,{'title':'Synthetic work','doi':'10.1234/shared','arxiv_id':'2501.12345','version_label':'v1','url':'https://example.com/paper/v1'},'s','b','q')
 payload={'paper_id':p2,'version_id':v2,'summary':p2,
          'methods':[{'name':'Synthetic method','description':v2+'#literal source quotation'}],
          'research_problems':[],'findings':[],
          'evidence_locators':[{'source_url':'https://example.com/paper/v1','section':'Abstract'}],
          'annotations':{'quoted_text':p2,'paper_id':p2,'nested':{'key':v2+'#quote'}}}
 ingest_extraction(c,payload);c.close()
 reconcile([first,second],root/'out.sqlite3',root/'report.json')
 c=sqlite3.connect(root/'out.sqlite3');mapped=json.loads(c.execute('SELECT payload_json FROM extraction_records').fetchone()[0]);c.close()
 result={'ids_remapped':mapped['paper_id']==p1 and mapped['version_id']==v1,
         'summary_preserved':mapped['summary']==payload['summary'],
         'method_description_preserved':mapped['methods'][0]['description']==payload['methods'][0]['description'],
         'extension_quote_preserved':mapped['annotations']==payload['annotations']}
 d=draft('synthetic','synthetic@v1','https://example.com/paper/v1')
 d['contributions'][0]['evidence_refs']=[]
 try:validate_extraction(d);result['empty_evidence_rejected']=False
 except ValueError:result['empty_evidence_rejected']=True
 print(json.dumps(result,indent=2))
 if a.expect_fixed:assert all(result.values()),result
