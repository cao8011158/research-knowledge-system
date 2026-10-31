"""Supported SQLite tables may have reordered columns; preserve data by column name."""
import argparse,json,sqlite3,shutil,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--db',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--expect-fixed',action='store_true');a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
sys.path[:0]=[str(a.repo/'src'),str(a.repo/'scripts')]
from reconcile_sqlite import reconcile
from kg_builder.entity_resolution import get_resolution_mentions
source=a.work/'reordered.sqlite3';shutil.copyfile(a.db,source);c=sqlite3.connect(source);c.row_factory=sqlite3.Row
names=['entity_resolution_batches','entity_resolution_entities','entity_resolution_mentions']
def rows(c,t):return sorted([dict(r) for r in c.execute('SELECT * FROM '+t)],key=lambda r:json.dumps(r,sort_keys=True))
before={t:rows(c,t) for t in names}
# Only order changes; supported names, types, constraints and every value are retained.
order={names[0]:['batch_id','reviewer','schema_version','reviewed_at','manifest_sha256','payload_json'],names[1]:['batch_id','entity_id','payload_json','scope','scope_version_id','kind'],names[2]:['batch_id','extraction_id','payload_json','mention_path','source_payload_sha256','decision','entity_id','kind']}
for table in names:
 ddl=c.execute('SELECT sql FROM sqlite_master WHERE name=?',(table,)).fetchone()[0]
 body=ddl[ddl.index('(')+1:ddl.rindex(')')]
 # Split SQL definitions at commas outside nested type/constraint parentheses.
 parts=[];start=0;depth=0
 for i,ch in enumerate(body):
  if ch=='(':depth+=1
  elif ch==')':depth-=1
  elif ch==',' and depth==0:parts.append(body[start:i].strip());start=i+1
 parts.append(body[start:].strip())
 cols={part.split()[0]:part for part in parts if part.split()[0] in order[table]}
 constraints=[part for part in parts if part.split()[0] not in cols]
 c.execute('PRAGMA foreign_keys=OFF')
 c.execute('CREATE TABLE reordered ('+','.join([cols[k] for k in order[table]]+constraints)+')')
 fields=','.join(order[table]);c.execute('INSERT INTO reordered('+fields+') SELECT '+fields+' FROM '+table)
 c.execute('DROP TABLE '+table);c.execute('ALTER TABLE reordered RENAME TO '+table);c.commit()
assert all(rows(c,t)==before[t] for t in names)
assert c.execute('PRAGMA foreign_key_check').fetchall()==[];c.close()
out=a.work/'out.sqlite3';reconcile([source],out,a.work/'report.json');c=sqlite3.connect(out);c.row_factory=sqlite3.Row
preserved={t:rows(c,t)==before[t] for t in names}
lookup=True
try:
 batch=before[names[0]][0]['batch_id'];eid=before[names[2]][0]['extraction_id'];get_resolution_mentions(c,batch,eid)
except (ValueError,KeyError,TypeError):lookup=False
c.close()
result={'valid_reordered_source_rows_and_foreign_keys':True,'preserved':preserved,'lookup_works_after_reconciliation':lookup}
print(json.dumps(result,indent=2))
if a.expect_fixed:assert all(preserved.values()) and lookup,result
