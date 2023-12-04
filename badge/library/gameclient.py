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

        # return the server's reponse or error message
        r.close()
        print(f"Error registering badge: {r.text}")

    def checkin(self, apitoken, uuid):
        """
        Checkin with the MonkeyBadge server API
        """

        request_url = self.baseurl + "/checkin"

        request_body = {"myUUID": uuid}

        try:
            sc, j = self.secure_api_request(request_url, apitoken, request_body)
        except Exception as err:
            print(f"Error reaching {self.baseurl}/checkin: {err}")
            return None

        if sc == 200:
            return j

        return None

    def konami_complete(self, token, uuid):
        request_url = self.baseurl + "/introcomplete"

        request_body = {"myUUID": uuid}

        sc, j = self.secure_api_request(request_url, token, request_body)

        if sc == 200:
            return j

        return None

    def friendrequest(self, token, uuid, IRID):
        request_url = self.baseurl + "/friendrequest"
        request_body = {"myUUID": uuid, "remoteIRID": str(IRID)}

        sc, j = self.secure_api_request(request_url, token, request_body)
        print(sc, j)
        if sc == 200:
            return j
        elif sc == 400:
            print("Already Friends")

        return None

    def secure_api_request(self, url, token, json):
        """
        Send a request to the MonkeyBadge server API
        """

        header = self.headers | {"X-API-Key": token}
        print(f"API Call to {url}")
        print(f"header: {header}\n body: {json}")

        r = requests.post(url, headers=header, json=json)
        if r.status_code == 200:
            j = r.json()
            r.close()
            return 200, j

        r.close()
        return r.status_code(), None
