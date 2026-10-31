"""Installed-wheel v1/v2 profiles and actual source-adjudication smoke acceptance."""
import argparse,json,shutil,tempfile
from pathlib import Path
from importlib.resources import files
from jsonschema import Draft202012Validator
import kg_builder.entity_resolution as er
from kg_builder.storage import connect
p=argparse.ArgumentParser();p.add_argument('--prepared',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--expected-prefix',required=True);a=p.parse_args()
assert str(er.__file__).startswith(a.expected_prefix)
for name in ['legacy.json','v0_2_draft.json','entity_resolution_v0_1.json','entity_resolution_v0_2.json']:
 Draft202012Validator.check_schema(json.loads(files('kg_builder.schemas').joinpath(name).read_text()))
m=json.loads(a.manifest.read_text());er.validate_resolution_manifest(m)
with tempfile.TemporaryDirectory() as tmp:
 f=Path(tmp)/'source.sqlite3';shutil.copyfile(a.prepared,f);c=connect(f);er.import_resolution_manifest(c,m)
 leaf=er.get_resolution_entity(c,m['batch_id'],'entity:problem:2502.12110:source-question');assert not leaf['stale']
 comp=next(x for x in m['mentions'] if x['review_outcome']=='composite_label')
 r=er.get_resolution_mentions(c,m['batch_id'],comp['extraction_id']);assert any(x['component_entities'] for x in r)
 assert c.execute('PRAGMA foreign_key_check').fetchall()==[];c.close()
print(json.dumps({'installed_module_verified':True,'packaged_profiles_valid':4,'v2_real_manifest_imports':True,'problem_parent_lookup_current':True,'compound_components_current':True,'fk_violations':0},indent=2))
