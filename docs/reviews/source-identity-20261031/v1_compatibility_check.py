"""v0.1 extension values remain opaque when v0.2 assigns those field names meaning."""
import argparse,copy,json,shutil,sqlite3,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--db',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--expect-fixed',action='store_true');a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(a.repo/'src'))
from kg_builder.storage import connect
from kg_builder.entity_resolution import import_resolution_manifest,get_resolution_mentions,get_resolution_entity
path=a.work/'compat.sqlite3';shutil.copyfile(a.db,path);c=connect(path)
m=json.loads(c.execute('SELECT payload_json FROM entity_resolution_batches ORDER BY batch_id LIMIT 1').fetchone()[0]);assert m['schema_version'].endswith('/0.1')
base=next(x for x in m['mentions'] if x['decision']=='resolved');target=base['entity_id']
# These properties were unrestricted supplementary JSON under the preserved v0.1 schema.
x=copy.deepcopy(m);x['batch_id']='v1:opaque-outcome'
for mention in x['mentions']:mention['review_outcome']={'legacy_note':'uninterpreted'}
import_resolution_manifest(c,x)
try:
 result=get_resolution_mentions(c,x['batch_id'],base['extraction_id'])
 outcome_ok=bool(result) and all('component_entities' not in r and 'review_outcome' not in r for r in result)
except (ValueError,KeyError,TypeError):outcome_ok=False
x=copy.deepcopy(m);x['batch_id']='v1:opaque-parent'
for entity in x['entities']:
 if entity['entity_id']==target:entity['parent_problem_ids']=['legacy supplementary value, not a Problem link']
import_resolution_manifest(c,x)
r=get_resolution_entity(c,x['batch_id'],target)
parent_ok=not r['stale'] and r['entity'] is not None
print(json.dumps({'v1_opaque_outcome_preserved':outcome_ok,'v1_opaque_parent_preserved':parent_ok},indent=2));c.close()
if a.expect_fixed:assert outcome_ok and parent_ok
