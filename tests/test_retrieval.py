import json, tempfile, os
from pathlib import Path
from GaokaoQuestionBank.bank.db import init_db, connect, import_questions
from GaokaoQuestionBank.bank.retrieval import search
root = Path('GaokaoQuestionBank')
db = Path(tempfile.gettempdir())/'gaokao-bank-test.db'
if db.exists(): db.unlink()
init_db(db, root/'schema.sql')
conn = connect(db)
rows = [
 {'id':'q1','paper_key':'p1','subject':'数学','region':'河南','exam_era':'new','year':2024,'q_no':1,'q_type':'导数','stem':'已知函数 f(x)=x^2，求导。','options':[{'key':'A','text':'2x'}],'answer':'A','explanation':'幂函数求导','source_url':'https://example.test/1'},
 {'id':'q2','paper_key':'p2','subject':'数学','region':'河南','exam_era':'old','year':2018,'q_no':1,'q_type':'集合','stem':'求集合交集。','options':[],'answer':'B','explanation':'交集'}
]
print('imported', import_questions(conn, rows))
conn.close()
print(json.dumps(search(str(db), {'subject':'数学','region':'河南','exam_era':'new'}, 10), ensure_ascii=False, indent=2))
