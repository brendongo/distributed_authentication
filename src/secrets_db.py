class SecretsDB(object):
    def __init__(self, db_filename):
        """Writes to db_filename somehow."""
        pass

    def get(self, key):
        pass

    def put(self, key, val):
        pass

    def select(self, timestamps):
        """Selects all entries such that entry.timestamp >=
        timestamps[entry.client] - window_size

        Args:
            timestamps ({client id: timestamp})
        """
        pass
