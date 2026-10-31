"""Run with an installed package outside source-path imports."""
import argparse,json,shutil,tempfile
from pathlib import Path
from importlib.resources import files
import kg_builder.entity_resolution as er
from kg_builder.storage import connect
from jsonschema import Draft202012Validator
p=argparse.ArgumentParser();p.add_argument('--db',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--expected-prefix',required=True);a=p.parse_args()
assert str(er.__file__).startswith(a.expected_prefix),er.__file__
schema=json.loads(files('kg_builder.schemas').joinpath('entity_resolution_v0_1.json').read_text());Draft202012Validator.check_schema(schema)
manifest=json.loads(a.manifest.read_text());er.validate_resolution_manifest(manifest)
with tempfile.TemporaryDirectory() as tmp:
 target=Path(tmp)/'source.sqlite3';shutil.copyfile(a.db,target);c=connect(target)
 er.import_resolution_manifest(c,manifest)
 assert c.execute('SELECT count(*) FROM entity_resolution_mentions').fetchone()[0]==74
 sample=next(m for m in manifest['mentions'] if m['decision']=='resolved')
 result=er.get_resolution_mentions(c,manifest['batch_id'],sample['extraction_id'])
 assert any(r['entity'] is not None and not r['stale'] for r in result)
 assert c.execute('PRAGMA foreign_key_check').fetchall()==[];c.close()
print(json.dumps({'installed_module_path_verified':True,'packaged_schema_valid':True,'real_manifest_imported':True,'entity_mentions':74,'indexed_lookup_current':True,'fk_violations':0},indent=2))
