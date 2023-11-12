import btree

class dbtree:
    def __init__(self):
        try:
            self.file = open("badgedb", "r+b")
        except OSError:
            self.file = open("badgedb", "w+b")
        self.btree = btree.open(self.file)

    def set(self, key, value):
        """
        Save key/value pairs to the btree database
        """
        try:
            self.btree[key] = value
            self.btree.flush()
        except: 
            print(f"dbtree.set KeyError: {key} not found")


    def get(self, key):
        """
        Get key/value pairs to the btree database

        will always return a string, not bytes
        """
        try: 
            result = self.btree[key]
            self.btree.flush()
            return result.decode()
        except:
            print(f"dbtree.get KeyError: {key} not found")
            return False

    def close(self):
        """
        Close the btree database
        """
        self.btree.close()
        self.file.close()