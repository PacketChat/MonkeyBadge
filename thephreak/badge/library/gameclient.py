import config  # Import the config file
import urequests as requests
import ujson as json
import uasyncio as asyncio
import btree

class MonkeyBadge:
    def __init__(self, uuid):
        """
        Initalize the MonkeyBadge class - this class is used to interact with the MonkeyBadge server API
        :param uuid: The UUID of the badge
        """
        self.badge_uuid = uuid
        self.registration_key = config.REG_KEY
        # db initialize
        try:
            file = open("badgedb", "r+b")
        except OSError:
            file = open("badgedb", "w+b")
        self.db = btree.open(file)

        # check DB for an handle, IR ID, and an API token

        #if self.db[b'handle']: self.handle = self.db[b'handle'].decode() 
        #else: self.handle = ""
        self.handle = ""
        #if self.db[b'apitoken']: self.handle = self.db[b'apitoken'].decode() 
        #else: self.apitoken = ""
        self.apitoken = ""
        self.IR_ID = ""

    def _save_to_db(self, kvs):
        """
        Save key/value pairs to the btree database
        """
        for key in kvs:
            self.db[key] = kvs[key]
        self.db.flush()

    def register(self):
        """
        Register the badge with the MonkeyBadge server API
        """
        print("[Method]: checkin")
        baseurl = config.API_SERVER

        # get a handle from the server
        r = requests.get(baseurl + "/generate_handle")
        if r.status_code == 200:
            self.handle = r.text
        else:
            self.handle = "unnamed_monkey"
    
        print("Running Badge Registration")
        print("UUID: %s, handle: %s" %(self.badge_uuid, self.handle))
        print("connecting to %s" % (baseurl + "/register"))
        print("JSON Values: %s" %({"handle": self.handle, "key": self.registration_key, "myUUID": self.badge_uuid}))        

        r = requests.post(baseurl + "/register", json={"myUUID": self.badge_uuid, "handle": self.handle, "key": self.registration_key })
        json_data = json.loads(r.text)
        print(json_data)
        if 'UUID' in json_data and r.status_code == 200:
            print("badge registered")
            self.apitoken = json_data['token']
            # self._save_to_db("{\"token\": \"%s\"}" % (self.apitoken))
        else:
            print("badge not registered.")

    async def checkin(self):
        """
        Checkin with the MonkeyBadge server API
        """
        while True:
            try:
                print("[Method]: checkin")
                baseurl = config.API_SERVER

                print("connecting to %s" % (baseurl + "/checkin"))

                print("token: %s, uuid: %s" %(self.apitoken, self.badge_uuid))
                r = requests.post(baseurl + "/checkin", headers={'X-API-Key': self.apitoken }, json={"myUUID": self.badge_uuid})
                json_data = json.loads(r.text)
                print("server response: %s" % (json_data))
                if r.status_code == 200:
                    print("badge registered")
                    return True
                else:
                    print("badge not registered, attempting to register")    
                    self.register()
                    return False
            except Exception as e:
                print("Error making API call:", e)
            await asyncio.sleep(60)  # non-blocking wait for 1 minute