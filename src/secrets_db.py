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
        key, pi_0_U, pi_0_V, c_U, c_V = self._cursor.fetchone()

        pi_0_U = deserialize1(pi_0_U)
        c_U = deserialize1(c_U)

        return ((pi_0_U, pi_0_V, None), (c_U, c_V, None))

    def put(self, key, threshold_secret):
        pi_0_U, pi_0_V, _ = threshold_secret[0]
        c_U, c_V, _ = threshold_secret[1]

        pi_0_U = serialize(pi_0_U)
        c_U = serialize(c_U)

        self._cursor.execute("INSERT INTO secrets VALUES (?,?,?,?,?)", (key, pi_0_U, pi_0_V, c_U, c_V))
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
                    (key TEXT, pi_0_U BLOB, pi_0_V BLOB, c_U BLOB, c_V BLOB)''')

    # db = SecretsDB('testdb')
    # db.put("brendon", "eats food")
    # print db.get("brendon")
    # db.put("kenneth", 1234)
    # print db.get("brendon")
    # print db.get("kenneth")
    # print db.get("not there")