import btree
import machine


class dbtree:
    def __init__(self):
        try:
            self.file = open("badgedb", "r+b")
        except OSError:
            self.file = open("badgedb", "w+b")

        try:
            self.db = btree.open(self.file)
        except Exception as err:
            print(f"failed to open btree, err: {err}. trying to recover")
            machine.reset()

    def set(self, key, value):
        """
        Save key/value pairs to the btree database
        """
        try:
            self.db[key] = value
            self.db.flush()  # type: ignore
            return True
        except Exception as err:
            print(f"dbtree.set: type {type(err)}: {err}")
            return False

    def get(self, key):
        """
        Get key/value pairs to the btree database

        will always return a string, not bytes
        """
        try:
            result = self.db[key]
            self.db.flush()  # type: ignore
            return result.decode()
        except Exception as err:
            print(f"dbtree.get: type {type(err)}: {err}")
            return None

    def close(self):
        """
        Close the btree database
        """
        self.file.close()
