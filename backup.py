"""Consistent SQLite backup, including all photo bytes. Run: python backup.py backup.db"""
import sqlite3
import sys
from pathlib import Path
from app import app
from backend.db import DB_PATH
if __name__ == '__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: python backup.py PATH_TO_BACKUP.db')
    destination=Path(sys.argv[1]).resolve()
    if destination==DB_PATH.resolve() or destination.exists():raise SystemExit('Choose a new backup path, different from the live database.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    source=sqlite3.connect(DB_PATH)
    backup=sqlite3.connect(destination)
    try:source.backup(backup)
    finally:backup.close();source.close()
    print('Database and image backup saved to',destination)
