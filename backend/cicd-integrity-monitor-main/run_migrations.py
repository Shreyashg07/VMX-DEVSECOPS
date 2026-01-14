import sqlite3
import glob

DB_PATH = "api/app/database.db"

conn = sqlite3.connect(DB_PATH)

for mfile in glob.glob("api/migrations/*.sql"):
    print("Applying:", mfile)
    with open(mfile, "r") as fh:
        conn.executescript(fh.read())

conn.commit()
conn.close()

print("Migrations applied!")
