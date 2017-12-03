import sqlite3
from tpke import serialize, deserialize1


class SecretsDB(object):
    def __init__(self, db_filename):
        """Writes to db_filename somehow."""
        self._conn = sqlite3.connect(db_filename)
        self._conn.text_factory = str
        self._cursor = self._conn.cursor()

    def get(self, key):
        self._cursor.execute("SELECT * FROM secrets WHERE key=?", (key,))
        key, U, V = self._cursor.fetchone()

        U = deserialize1(U)

        threshold_secret = (U, V, None)
        return threshold_secret

    def put(self, key, threshold_secret):
        U, V, W = threshold_secret

        U = serialize(U)

        self._cursor.execute("INSERT INTO secrets VALUES (?,?,?)", (key, U, V))
        self._conn.commit()

    def select(self, timestamps):
        """Selects all entries such that entry.timestamp >=
        timestamps[entry.client] - window_size

        Args:
            timestamps ({client id: timestamp})
        """
        pass


if __name__ == '__main__':
    for i in xrange(7):
        conn = sqlite3.connect('databases/secrets' + str(i) + 'db')
        c = conn.cursor()
        c.execute('''CREATE TABLE secrets
                    (key TEXT, U BLOB, V BLOB)''')

    # db = SecretsDB('testdb')
    # db.put("brendon", "eats food")
    # print db.get("brendon")
    # db.put("kenneth", 1234)
    # print db.get("brendon")
    # print db.get("kenneth")
    # print db.get("not there")