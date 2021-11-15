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

INSERT INTO artilce_evals (ticker_symbol, rating, optional_reasons) VALUES ("43", "rating-3", "['optional-reason-1', 'optional-reason-2', 'optional-reason-3']");
INSERT INTO artilce_evals (ticker_symbol, rating, optional_reasons) VALUES ("29", "rating-5", "[]");
INSERT INTO artilce_evals (ticker_symbol, rating, optional_reasons) VALUES ("oos_4", "rating-5", "[]");
INSERT INTO artilce_evals (ticker_symbol, rating, optional_reasons) VALUES ("oos_8", "rating-4", "['optional-reason-2']");
INSERT INTO artilce_evals (ticker_symbol, rating, optional_reasons) VALUES ("11", "rating-4", "['optional-reason-5']");
INSERT INTO artilce_evals (ticker_symbol, rating, optional_reasons) VALUES ("15", "rating-5", "['optional-reason-1', 'optional-reason-2', 'optional-reason-3', 'optional-reason-4']");