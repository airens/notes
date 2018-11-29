import shutil
import sqlite3
from time import time

class Db:
    def __request(self, request, *args):
        if self.base:
            try:
                cur = self.base.cursor()
                cur.execute(request, args)
                self.base.commit()
                return cur.fetchall()
            except Exception as e:
                print(e)

    def __init__(self, fname):
        self.fname = fname
        self.base = sqlite3.connect(fname)
        # self.__request("PRAGMA foreign_keys=ON;")
        self.__request("CREATE TABLE IF NOT EXISTS " +
                       "notes (id INTEGER PRIMARY KEY, title STRING, body STRING, last_apply REAL)")
        self.__request("CREATE TABLE IF NOT EXISTS " +
                        "tags (note_id INT, tag STRING, PRIMARY KEY(note_id,tag)," +
                        "FOREIGN KEY (note_id) REFERENCES notes(id))")
        self.__request("CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(id, title, body, last_apply)")
        # self.__request("DROP TRIGGER after_notes_insert")
        # self.__request("DROP TRIGGER after_notes_update")
        # self.__request("DROP TRIGGER after_notes_delete")
        self.__request("""
                        CREATE TRIGGER IF NOT EXISTS after_notes_insert AFTER INSERT ON notes BEGIN
                          INSERT INTO fts (
                            id,
                            title,
                            body,
                            last_apply
                          )
                          VALUES(
                            new.id,
                            new.title,
                            new.body,
                            new.last_apply
                          );
                        END;
        """)
        self.__request("""
                        CREATE TRIGGER IF NOT EXISTS after_notes_update UPDATE OF title, body ON notes BEGIN
                          UPDATE fts SET title = new.title, body = new.body WHERE id = old.id;
                        END;
        """)
        self.__request("""
                        CREATE TRIGGER IF NOT EXISTS after_notes_delete AFTER DELETE ON notes BEGIN
                            DELETE FROM fts WHERE id = old.id;
                            DELETE FROM tags WHERE note_id = old.id;
                        END;
        """)

    def __del__(self):
        if self.base:
            self.base.close()

    def get_note(self, note_id):
        self.__request("UPDATE notes SET last_apply=? WHERE id=?", time(), note_id)
        res = self.__request("SELECT id,title,body FROM notes WHERE id=?", note_id)
        if res:
            return res[0]
        else:
            return None

    def get_all(self, table="notes", column=None):
        if column:
            return self.__request(f"SELECT {column} FROM {table} ORDER BY last_apply DESC")
        else:
            return self.__request(f"SELECT id,title,body FROM {table} ORDER BY last_apply DESC")

    def get_all_notes(self, tags):
        if tags:
            return self.__request("""
              SELECT id,title,body FROM notes WHERE id IN (
                SELECT note_id FROM (
                  SELECT note_id, COUNT(tag) AS 'count'
                  FROM tags
                  WHERE tag IN (?)
                  GROUP BY note_id
                ) WHERE count=?
              ) ORDER BY last_apply DESC
            """, ','.join(tags), len(tags))
        else:
            return self.get_all()

    def insert_note(self, title, body):
        self.__request("INSERT INTO notes VALUES (?,?,?,?)", None, title, body, time())
        res = self.__request("SELECT last_insert_rowid()")
        if res and res[0]:
            return res[0][0]
        else:
            return None

    def set_note_tags(self, note_id, tags):
        if not tags:
            return
        self.__request("DELETE FROM tags WHERE note_id=?", note_id)  # before set new tags remove the old ones
        for tag in tags:
            self.__request("INSERT INTO tags (note_id, tag) VALUES (?,?)", note_id, tag)

    def update_note_last_apply(self, note_id):
        if note_id:
            self.__request("UPDATE notes SET last_apply=? WHERE id=?", time(), note_id)

    def get_note_tags(self, note_id):
        res = self.__request("SELECT tag FROM tags WHERE note_id=?", note_id)
        if res:
            return [row[0] if row else None for row in res]
        else:
            return None

    def get_all_tags(self):
        res = self.__request("SELECT tag FROM tags GROUP BY tag ORDER BY COUNT(tag) DESC")
        if res:
            return [row[0] if row else None for row in res]
        else:
            return None

    def update_note(self, note_id, title, body):
        if note_id and title and body:
            self.__request("UPDATE notes SET title=?,body=?,last_apply=? WHERE id=?", title, body, time(), note_id)

    def update_note_title(self, note_id, title):
        if note_id and title:
            self.__request("UPDATE notes SET title=?,last_apply=? WHERE id=?", title, time(), note_id)

    def update_note_body(self, note_id, body):
        if note_id and body:
            self.__request("UPDATE notes SET body=?, last_apply=? WHERE id=?", body, time(), note_id)

    def delete_note(self, note_id):
        if note_id:
            self.__request("DELETE FROM notes WHERE id=?", note_id)

    def fts_note(self, text, tags=None):  # full-text search
        if not text:
            return []
            # text = ''.join(e for e in text if e.isalnum())  # remove all special characters
        if tags:
            # 1. select rows from 'tags' table for every couple id-tag
            # 2. count how many pairs were found for every id
            # 3. if pairs count == len(tags), get these id's and filter FTS result using them
            return self.__request("""
              SELECT id,title,body FROM fts WHERE id IN (
                SELECT note_id FROM (
                  SELECT note_id, COUNT(tag) AS 'count'
                  FROM tags
                  WHERE tag IN (?)
                  GROUP BY note_id
                ) WHERE count=?
              ) AND fts MATCH ? ORDER BY rank;
            """, ','.join(tags), len(tags),  f"{text}*")
        else:
            return self.__request("SELECT * FROM fts WHERE fts MATCH ? ORDER BY rank", f"{text}*")

    def drop_table(self, table):
        self.__request(f"DELETE FROM {table}")

    def copy_table(self, src, dest, drop_src=True):
        if drop_src:
            self.drop_table(dest)
        self.__request(f"INSERT INTO {dest} SELECT * FROM {src}")

    def make_backup(self, filepath):
        try:
            shutil.copyfile(self.fname, shutil.os.path.join(filepath, self.fname))
            print(f"Made backup of {self.fname} at {filepath}")
            return True
        except Exception as e:
            print("COPYFILE:", e)
            return False


db = Db("notes.db")
db.copy_table("notes", "fts")
