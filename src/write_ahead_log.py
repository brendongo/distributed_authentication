class WriteAheadLog(object):
    def __init__(self, log_filename):
        """
        Args:
            logfile (string): filename of log
        """
        pass

    def log(self, msg):
        """Append message to log

        Args:
            msg (Message)
        """
        pass

    def truncate(self):
        """Runs periodically in the background. Deletes any completed
        transactions.
        """
        pass

    @property
    def messages(self):
        """Yields messages in the log."""
        pass
