import urequests as requests
import config
import gc


class GameClient:
    def __init__(self, version):
        self.baseurl = config.API_SERVER
        self.headers = {
            "content-type": "application/json",
            "User-Agent": f"MonkeyBadge/{version}",
        }

    def reg_request(self, request_body):
        """
        Register the badge with the MonkeyBadge server API
        """
        # do some garbage collections
        gc.collect()

        print("Registering Badge with MonkeyBadge Server")

        request_url = self.baseurl + "/register"

        # get a handle from the server
        try:
            r = requests.get(self.baseurl + "/generate_handle")
        except Exception as err:
            print(f"Error reaching {self.baseurl}/generate_handle: {err}")
            return None

        if r.status_code == 200:
            request_body["handle"] = r.text.strip('"')
        else:
            request_body["handle"] = "unnamed_monkey"

        r.close()

        print(f"connecting to {request_url}")
        print(f"Sending JSON Values: {request_body}")

        try:
            r = requests.post(request_url, headers=self.headers, json=request_body)
        except Exception as err:
            print(f"Error reaching {self.baseurl}/register: {err}")
            return None

        if r.status_code == 200:
            j = r.json()
            r.close()
            return j
        else:
            print(f"Error Registering badge: {r.text}")
            r.close()
            return None

    def checkin(self, apitoken, uuid):
        """
        Checkin with the MonkeyBadge server API
        """

        request_url = self.baseurl + "/checkin"

        request_body = {"myUUID": uuid}

        sc, j = self.secure_api_request(request_url, apitoken, request_body)

        print(f"Checkin returned {sc}, {j}")
        if sc == 404:
            return 404, None
        elif sc == 200:
            return 200, j

        print(f"Error reaching {self.baseurl}/checkin.")
        return 500, None

    def konami_complete(self, token, uuid):
        request_url = self.baseurl + "/introcomplete"

        request_body = {"myUUID": uuid}

        sc, j = self.secure_api_request(request_url, token, request_body)

        if sc == 200:
            return j

        return None

    def change_handle(self, token, uuid, name):
        request_url = self.baseurl + "/changehandle"

        request_body = {"myUUID": uuid, "handle": name}

        r = self.secure_api_request(request_url, token, request_body)

        if r.status_code == 200:
            return r.json()
        else:
            return None

    def friendrequest(self, token, uuid, IRID):
        request_url = self.baseurl + "/friendrequest"
        request_body = {"myUUID": uuid, "remoteIRID": str(IRID)}

        sc, j = self.secure_api_request(request_url, token, request_body)
        print(f"Friend Request returned {sc}, {j}")
        if sc == 200:
            return j
        elif sc == 208:
            print("Already Friends")

        return None

    def hiddenobject(self, token, uuid, objectid):
        request_url = self.baseurl + "/hiddenobject"
        request_body = {"myUUID": uuid, "objectid": objectid}

        sc, j = self.secure_api_request(request_url, token, request_body)
        print(f"hiddenobject returned: {sc}, {j}")
        if sc == 200:
            return sc, j
        elif sc == 208:
            print(f"already interacted with {objectid}")
        return sc, None

    def monkeysee(self, token, uuid, monkeyid):
        request_url = self.baseurl + "/monkeysee"
        request_body = {"myUUID": uuid, "objectid": monkeyid}

        sc, j = self.secure_api_request(request_url, token, request_body)
        print(f"monkeysee returned {sc}, {j}")
        if sc == 200:
            return sc, j
        elif sc == 208:
            print(f"error already interacted with {monkeyid}")
        return sc, None

    def secure_api_request(self, url, token, json):
        """
        Send a request to the MonkeyBadge server API
        """

        header = self.headers | {"X-API-Key": token}
        print(f"API Call to {url}")
        print(f"header: {header}\n body: {json}")

        try:
            r = requests.post(url, headers=header, json=json)
        except Exception:
            return 500, None

        sc = r.status_code
        if sc == 200:
            j = r.json()
            r.close()
            return sc, j

        r.close()
        return sc, None
