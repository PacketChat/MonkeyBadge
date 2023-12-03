import requests
import json
from hrid import HRID
import uuid
import secrets
import coredis
import os

redishost = os.environ.get("MB_REDIS_HOST", "127.0.0.1")
redisport = os.environ.get("MB_REDIS_PORT", "6379")

uberbadges = {
    "uber1": "bb4a84dc-cf4b-4d04-84fd-1c1cc8799e0d",
    "uber2": "4ec2d946-05fa-4f34-a033-278a6d1ac222",
    "uber3": "7bc78281-2036-41b2-8d98-fc23ec504e9a",
    "uber4": "0bd0d58f-fb52-4859-9bd2-435f0af39e62",
    "uber5": "a4860c69-4e4d-4c30-bf30-9f7c982df55d",
}

monkeybadges = {
    "cansuuid": "c71ec72e-c063-48c0-a3f9-ce5af406445f",
    "micuuid": "7f19e4b1-b6b2-49be-8b27-6061fdaf5ef0",
    "shadesuuid": "aa0b8824-53d0-4c46-8c08-ad75baf9d1d5",
}


def generate_uuid():
    myuuid = uuid.uuid4()
    return str(myuuid)


def generate_handle():
    hruuid = HRID(hridfmt=("adjective", "noun"))
    handle = hruuid.generate()
    return handle


client = coredis.Redis(host=redishost, port=redisport)

registration_key = "7bc78281-2036-41b2-8d98-fc23ec504e9a"
handle = generate_handle()
thisbadge = generate_uuid()
token = secrets.token_urlsafe(16)


# Test Registration
def test_register_success():
    r = requests.post(
        "http://localhost:8000/register",
        json={"handle": handle, "key": registration_key, "myUUID": thisbadge},
    )
    json_data = json.loads(r.text)
    assert json_data["UUID"] == thisbadge, "UUIDs do not match"


def test_register_bad_key():
    r = requests.post(
        "http://localhost:8000/register",
        json={"handle": handle, "key": "badkey", "myUUID": thisbadge},
    )
    assert r.status_code == 400, "Status code is not 400"


def test_register_duplicate():
    r = requests.post(
        "http://localhost:8000/register",
        json={"handle": handle, "key": registration_key, "myUUID": thisbadge},
    )
    assert r.status_code == 400, "Status code is not 400"


def test_register_bad_uuid():
    r = requests.post(
        "http://localhost:8000/register",
        json={"handle": handle, "key": registration_key, "myUUID": "baduuid"},
    )
    assert r.status_code == 400, "Status code is not 400"


# Set the API token for future requests
async def update_api_key():
    j = await client.json.get(thisbadge, ".")
    j["token"] = token
    await client.json.set(thisbadge, ".", j)

    apikeys = await client.lrange("badge_apikeys", 0, -1)

    for i in apikeys:
        if i.decode() == token:
            return

    # if api_key isn't in apikeys - then add it
    await client.rpush("badge_apikeys", token.split())


# Test Match Mode
def test_matchmode_enable():
    r = requests.post(f"http://localhost:8000/enablematchmode/{thisbadge}")
    assert r.status_code == 200, "Status code is not 200"


def test_matchmode_enable_apikey():
    r = requests.post(f"http://localhost:8000/enablematchmode/{thisbadge}")
    assert r.status_code == 200, "Status code is not 200"


def test_matchmode_enable_badge_not_found():
    r = requests.post("http://localhost:8000/enablematchmode/thisbadge")
    assert r.status_code == 405, "Status code is not 200"


def test_matchmode_disable():
    r = requests.post(f"http://localhost:8000/disablematchmode/{thisbadge}")
    assert r.status_code == 200, "Status code is not 200"


def test_matchmode_disable_apikey():
    r = requests.post(f"http://localhost:8000/enablematchmode/{thisbadge}")
    assert r.status_code == 200, "Status code is not 200"


def test_matchmode_disable_badge_not_found():
    r = requests.post("http://localhost:8000/disablematchmode/thisbadge")
    assert r.status_code == 405, "Status code is not 200"


# Cleanup
async def cleanup():
    await client.delete(["badge_apikeys"])
    await client.json.delete(thisbadge, ".")
