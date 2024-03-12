DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS user_projects;
PRAGMA foreign_keys = ON;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  neo4j_url TEXT DEFAULT 'bolt://127.0.0.1:7687',
  neo4j_user TEXT DEFAULT 'neo4j',
  neo4j_password TEXT DEFAULT 'neo4j',
  admin INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL
);
CREATE TABLE user_projects (
  id_user INTEGER,
  id_project INTEGER,
  role INTEGER NOT NULL DEFAULT 2,
  FOREIGN KEY(id_user) REFERENCES user(id),
  FOREIGN KEY(id_project) REFERENCES projects(id)
  -- PRIMARY KEY (id_user, id_project)
);

