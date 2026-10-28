PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS papers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  paper_key TEXT UNIQUE NOT NULL,
  title TEXT,
  subject TEXT NOT NULL,
  region TEXT,
  exam_era TEXT CHECK(exam_era IN ('new','old','unknown')) DEFAULT 'unknown',
  year INTEGER,
  month INTEGER,
  exam_type TEXT,
  source_site TEXT,
  source_url TEXT,
  local_file TEXT,
  status TEXT DEFAULT 'draft',
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_papers_filter ON papers(subject,region,year,exam_era,exam_type,status);

CREATE TABLE IF NOT EXISTS questions (
  id TEXT PRIMARY KEY,
  paper_key TEXT NOT NULL,
  subject TEXT NOT NULL,
  region TEXT,
  exam_era TEXT,
  year INTEGER,
  month INTEGER,
  exam_type TEXT,
  section TEXT,
  q_no INTEGER,
  q_type TEXT,
  stem TEXT NOT NULL,
  options_json TEXT,
  answer TEXT,
  explanation TEXT,
  score REAL DEFAULT 0,
  knowledge_json TEXT,
  source_url TEXT,
  content_hash TEXT,
  status TEXT DEFAULT 'draft',
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_questions_filter ON questions(subject,region,year,exam_era,q_type,q_no,status);
CREATE INDEX IF NOT EXISTS idx_questions_paper ON questions(paper_key);

CREATE TABLE IF NOT EXISTS question_types (
  id TEXT PRIMARY KEY,
  subject TEXT,
  region TEXT,
  exam_era TEXT,
  parent_id TEXT,
  name TEXT NOT NULL,
  aliases TEXT,
  source TEXT,
  UNIQUE(subject,region,exam_era,name)
);

CREATE TABLE IF NOT EXISTS question_type_links (
  question_id TEXT NOT NULL,
  type_id TEXT NOT NULL,
  confidence REAL,
  method TEXT,
  PRIMARY KEY(question_id,type_id)
);

CREATE TABLE IF NOT EXISTS crawl_jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_key TEXT UNIQUE,
  source_site TEXT,
  subject TEXT,
  region TEXT,
  year INTEGER,
  exam_era TEXT,
  url TEXT,
  status TEXT,
  message TEXT,
  fetched_at TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS questions_fts USING fts5(
  question_id UNINDEXED,
  stem,
  options_text,
  explanation,
  tokenize='unicode61'
);
