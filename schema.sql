-- CampusFind database schema (SQLite)
-- Run automatically on first start by backend/db.py

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    email         TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'staff', 'admin')),
    student_id    TEXT UNIQUE,
    verified_at   TEXT,
    session_version INTEGER NOT NULL DEFAULT 0,
    phone         TEXT,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS categories (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name   TEXT    NOT NULL UNIQUE,
    emoji  TEXT    NOT NULL DEFAULT '📦',
    accent TEXT    NOT NULL DEFAULT 'emerald'
);

CREATE TABLE IF NOT EXISTS items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ref         TEXT    NOT NULL UNIQUE,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kind        TEXT    NOT NULL CHECK (kind IN ('lost', 'found')),
    title       TEXT    NOT NULL,
    description TEXT    NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    location    TEXT    NOT NULL,
    event_date  TEXT    NOT NULL,
    contact     TEXT,
    image_path  TEXT,
    status      TEXT    NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'removed')),
    custody     TEXT    CHECK (custody IN ('with_me', 'security_office', 'department_office')),
    views       INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    resolved_at TEXT,
    handed_over_at TEXT,
    retain_until TEXT,
    disputed INTEGER NOT NULL DEFAULT 0,
    dispute_note TEXT,
    dispute_resolution TEXT,
    previous_status TEXT,
    archived INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_items_feed    ON items(status, kind, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_items_owner   ON items(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category_id);

CREATE TABLE IF NOT EXISTS claims (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id       INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    claimant_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message       TEXT    NOT NULL,
    status        TEXT    NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'withdrawn')),
    reviewer_note TEXT,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    reviewed_at   TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_claims_active
    ON claims(item_id, claimant_id) WHERE status IN ('pending', 'approved');
CREATE INDEX IF NOT EXISTS idx_claims_item ON claims(item_id, created_at DESC);

CREATE TABLE IF NOT EXISTS notifications (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title      TEXT    NOT NULL,
    body       TEXT    NOT NULL,
    link       TEXT,
    read_at    TEXT,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS image_blobs (
    name TEXT PRIMARY KEY,
    mime TEXT NOT NULL,
    data BLOB NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS email_challenges (
    email TEXT NOT NULL,
    purpose TEXT NOT NULL CHECK (purpose IN ('register','reset')),
    payload TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    expires_at INTEGER NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    sent_at INTEGER NOT NULL,
    PRIMARY KEY(email,purpose)
);
CREATE TABLE IF NOT EXISTS rate_limits (
    key TEXT PRIMARY KEY,
    hits INTEGER NOT NULL,
    resets_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id INTEGER,
    item_id INTEGER,
    action TEXT NOT NULL,
    snapshot TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS dispute_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    reporter_id INTEGER NOT NULL REFERENCES users(id),
    message TEXT NOT NULL,
    resolved_at TEXT,
    resolution TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_retention ON items(archived, retain_until);

CREATE UNIQUE INDEX IF NOT EXISTS idx_student_identity ON users(replace(student_id,'/PS','')) WHERE student_id IS NOT NULL;
