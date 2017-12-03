import sqlite3


class SecretsDB(object):
    def __init__(self, db_filename):
        """Writes to db_filename somehow."""
        self._conn = sqlite3.connect(db_filename)
        self._cursor = self._conn.cursor()

    def get(self, key):
        self._cursor.execute("SELECT * FROM secrets WHERE key=?", (key,))
        return self._cursor.fetchone()

    def put(self, key, val):
        self._cursor.execute("INSERT INTO secrets VALUES (?,?)", (key, val))
        self._conn.commit()

    def select(self, timestamps):
        """Selects all entries such that entry.timestamp >=
        timestamps[entry.client] - window_size

        Args:
            timestamps ({client id: timestamp})
        """
        pass


if __name__ == '__main__':
    # conn = sqlite3.connect('testdb')
    # c = conn.cursor()
    # c.execute('''CREATE TABLE secrets
    #             (key TEXT, val BLOB)''')

    db = SecretsDB('testdb')
    db.put("brendon", "eats food")
    print db.get("brendon")
    db.put("kenneth", 1234)
    print db.get("brendon")
    print db.get("kenneth")
    print db.get("not there")