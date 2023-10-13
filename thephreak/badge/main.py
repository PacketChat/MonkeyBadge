import network
import config
import urequests as requests
import urandom
import btree
import json

from time import sleep

def uuid4():
    # Generate 32 random bits at a time, 4 times, and concatenate them, because
    # our MicroPython supports only 32 bits of random bits:
    uuid_bytes = bytes()
    for _ in range(4):
        uuid_bytes += urandom.getrandbits(32).to_bytes(4, 'big')

    # Format the bytes as a UUID:
    uuid_str = '-'.join(
        [uuid_bytes[:4].hex(), uuid_bytes[4:6].hex(), uuid_bytes[6:8].hex(),
        uuid_bytes[8:10].hex(), uuid_bytes[10:].hex()])

    return uuid_str


class NetworkMGR:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

    def connect_wifi(self, SSID, SSID_PASSWORD):
        self.wlan.active(True)
        if not self.wlan.isconnected():
            self.wlan.connect(SSID, SSID_PASSWORD)
            while not self.wlan.isconnected():
                pass
    def get_status(self):
        return self.wlan.ifconfig()
    
    def isWifiConnected(self):
        if not self.wlan.isconnected():
            return False
        else:
            return True

class MonkeyBadge:
    def __init__(self, uuid):
        self.badge_uuid = uuid
        self.registration_key = config.REG_KEY
        self.handle = ""
        self.apitoken

    def register(self):
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
        else:
            print("badge not registered.")

    def checkin(self):
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
            print("badge not registered.")    
            return False    

def main():

    # db initialize
    try:
        file = open("badgedb", "r+b")
    except OSError:
        file = open("badgedb", "w+b")
    
    db = btree.open(file)

    badge = ""
    # do I have a valid uuid already generated?
    if not b"UUID" in db:
        db[b'UUID'] = uuid4()
        db.flush()
        print("Setting my UUID to %s" %(db[b'UUID']))
        badge = MonkeyBadge(db[b'UUID'].decode)
    else:
        print("Getting my UUID to %s" %(db[b'UUID']))
        badge = MonkeyBadge(db[b'UUID'].decode)

    net = NetworkMGR()


    print("Starting main program loop")
    while True:
        #sleep(60)
        # check if wifi is connected
        print("Checking Wifi Connectivity")
        if not net.isWifiConnected():
            print("not connected, trying to connect.")
            net.connect_wifi(config.SSID, config.SSID_PASSWORD)
            #sleep(10)
        else:
            print("Network Connected:")
            print(net.get_status())
            print("checking if badge is registered")

            if not b"token" in db:
                # we need to register
                print("badge not registered, contacting registration server")
                badge.register()
            else:

                badge.apitoken = db[b'token'].decode()
                
            if badge.checkin() == True:
                print("badge check-in success.")


if __name__ == "__main__":
    main()

