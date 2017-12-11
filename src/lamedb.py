import sqlite3


class LameSecretsDB(object):
    def __init__(self):
        """Writes to db_filename somehow."""
        self._conn = sqlite3.connect('databases/lamesecretsdb')
        self._conn.text_factory = str
        self._cursor = self._conn.cursor()

    def get(self, key):
        self._cursor.execute("SELECT * FROM lame_secrets WHERE key=?", (key,))
        key, value = self._cursor.fetchone()
        return value

    def put(self, key, value):
        self._cursor.execute("INSERT INTO lame_secrets VALUES (?,?)", (key, value))
        self._conn.commit()

    def select(self, timestamps):
        """Selects all entries such that entry.timestamp >=
        timestamps[entry.client] - window_size

        Args:
            timestamps ({client id: timestamp})
        """
        pass


if __name__ == '__main__':
    conn = sqlite3.connect('databases/lamesecretsdb')
    c = conn.cursor()
    c.execute('''CREATE TABLE lame_secrets
                 (key TEXT, value BLOB)''')
    conn.commit()

    db = LameSecretsDB()
    db.put("brendon", "eats food")
    print db.get("brendon")
    db.put("kenneth", 1234)
    print db.get("brendon")
    print db.get("kenneth")
    print db.get("not there")