CREATE TABLE kingdom_saves (
  user_id TEXT PRIMARY KEY NOT NULL,
  revision INTEGER NOT NULL CHECK (revision > 0),
  payload TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
