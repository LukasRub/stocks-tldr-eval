DROP TABLE IF EXISTS article_evals;
DROP TABLE IF EXISTS stock_evals;

CREATE TABLE article_evals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doc_id TEXT NOT NULL,
  rating INTEGER NOT NULL,
  optional_reasons TEXT
);

CREATE TABLE stock_evals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ticker_symbol TEXT NOT NULL,
  rating INTEGER NOT NULL,
  optional_reasons TEXT
);