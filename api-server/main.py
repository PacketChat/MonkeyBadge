import json
import os
import random
import secrets
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from hrid import HRID
from pydantic import BaseModel
import coredis
import uvicorn
import re

app = FastAPI()

redishost = os.environ.get("MB_REDIS_HOST", "127.0.0.1")
redisport = os.environ.get("MB_REDIS_PORT", "6379")

registration_key = "7bc78281-2036-41b2-8d98-fc23ec504e9a"

uber1uuid = 12341
uber2uuid = 42342
uber3uuid = 52321
uber4uuid = 65001
uber5uuid = 38913

cansuuid = 37634
micuuid = 31583
shadesuuid = 51799


templateJSON = """
{
    "badgeHandle": "",
    "current_challenge": "intro",
    "IR_ID": "",
    "token": "",
    "intro": {
        "enabled": 0,
        "complete": 0
    },
    "challenge1": {
        "complete": 0,
        "matches": []
    },
    "challenge2": {
        "complete": 0,
        "status": [0,0,0,0,0]
    },
    "challenge3": {
        "complete": 0,
        "interact_cans": 0,
        "interact_mic": 0,
        "interact_shades": 0
    },
    "antisocial_monkey_club": 0,
    "battles": {
        "won": 0,
        "lost": 0,
        "level": 1
    }
}
"""


def check_intro_started():
    """
    Check if the intro challenge has been started by looking for the
    existance of a drop file
    """
    if os.path.exists("intro_started"):
        return True
    else:
        return False


api_key_header = APIKeyHeader(name="X-API-Key")

client = coredis.Redis(host=redishost, port=int(redisport))


class Admin(BaseModel):
    key: str


class Handle(BaseModel):
    myUUID: str
    handle: str


class Register(BaseModel):
    myUUID: str
    key: str
    handle: str


class UUID_ObjectID(BaseModel):
    myUUID: str
    objectid: int


class UUID_IRID(BaseModel):
    myUUID: str
    remoteIRID: str


class OnlyUUID(BaseModel):
    myUUID: str


async def does_api_key_exist(client, api_key: str) -> bool:
    apikeys = await client.lrange("badge_apikeys", 0, -1)
    if not apikeys:
        return False
    else:
        for i in apikeys:
            if i.decode() == api_key:
                print("found api key")
                return True
        return False


async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if await does_api_key_exist(client, api_key_header):
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )


async def validBadge(badge_id):
    # check if badge_id is valid
    # return true if valid
    # return false if not valid

    j = await client.json.get(badge_id, ".")
    if not j:
        return False
    else:
        return True


async def validateKey(badge_id, key):
    # check if the key is valid for the badge_id
    # if valid, return true
    # if invalid, return false
    j = await client.json.get(badge_id, ".")
    if not j:
        return False
    else:
        if isinstance(j, dict) and "token" in j and j["token"] == key:
            return True
        else:
            return False


@app.get("/generate_handle")
def generate_handle():
    """
    Generates a non-deterministic random handle

    GET request with no body
    returns a handle
    """

    hruuid = HRID(hridfmt=("adjective", "noun"))
    handle = hruuid.generate()
    return handle


@app.post("/changehandle")
async def changehandle(r: Handle, api_key: str = Security(get_api_key)):
    """
    Changes the handle for the badge to the new handle

    POST request with json body: {"myUUID": "uuid", "handle": "handle"}
    returns full json structure for player
    """
    j = await client.json.get(r.myUUID, ".")

    if not j:
        raise HTTPException(status_code=404, detail="Badge not found")

    if not r.handle:
        raise HTTPException(status_code=400, detail="New handle missing")
    elif not re.match("^[a-zA-Z0-9_-]*$", r.handle):
        # validate the handle only contains letters, numbers underscores and dashes
        raise HTTPException(
            status_code=400,
            detail="Invalid handle, only letters, numbers and dashes allowed",
        )
    elif len(r.handle) > 20:
        raise HTTPException(
            status_code=400, detail="Handle too long, max 20 characters"
        )

    if isinstance(j, dict) and "token" in j and "badgeHandle" in j:
        if not j["token"] == api_key:
            raise HTTPException(status_code=404, detail="Badge not found")

        j["badgeHandle"] = r.handle
        await client.json.set(r.myUUID, ".", j)
        return j
    else:
        raise HTTPException(status_code=500, detail="changehandle - Data error")


@app.post("/introcomplete")
async def introcomplete(r: OnlyUUID, api_key: str = Security(get_api_key)):
    """
    POST Request with json body: {"myUUID": "uuid"}
    returns full json structure for player.
    """
    # use badge_id to lookup json from redis
    # if there's a result, return the json structure
    # check if badge_id exists in redis
    j = await client.json.get(r.myUUID, ".")

    if not j:
        raise HTTPException(status_code=404, detail="Badge not found")

    if isinstance(j, dict) and "token" in j:
        if not j["token"] == api_key:
            raise HTTPException(status_code=404, detail="Badge not found")

    if isinstance(j, dict) and "intro" in j:
        j["intro"]["complete"] = 1
    else:
        raise HTTPException(status_code=500, detail="introcomplete - Data error")

    if isinstance(j, dict) and "current_challenge" in j:
        j["current_challenge"] = "challenge1"
    else:
        raise HTTPException(status_code=500, detail="introcomplete - Data error")

    await client.json.set(r.myUUID, ".", j)
    return j


@app.post("/register")
async def register(r: Register):
    """
    POST request with json body: {"myUUID": "uuid", "key": "key", "handle": "handle"}
    returns full json structure for player
    """

    # create a new badge in redis from the templateJSON string

    if r.key != registration_key:
        print(f"Invalid Registration key: {r.key}")
        raise HTTPException(status_code=400, detail="Invalid registration key")

    # see if the badge_id exists in redis already
    if not await validBadge(r.myUUID):
        new_token = secrets.token_urlsafe(16)

        j = json.loads(templateJSON)

        if check_intro_started():
            j["intro"]["enabled"] = 1

        # get a new IRID
        irid = ""
        while True:
            irid = random.getrandbits(16)
            # if the irid doesn't exist in redis, then use it
            if not await client.json.get(f"{irid}", "."):
                # update the player in redis with the IR_ID
                j["IR_ID"] = irid
                # create a redis key IR_ID with the value: uuid
                await client.set(f"{irid}", r.myUUID)
                break
        if irid == "":
            raise HTTPException(status_code=500, detail="Unable to create IRID")

        j["token"] = new_token
        j["badgeHandle"] = r.handle
        j["IR_ID"] = irid
        apikeys = await client.lrange("badge_apikeys", 0, -1)

        # search for badge_id in bytes format
        for i in apikeys:
            if i.decode() is new_token:
                raise HTTPException(status_code=500, detail="Duplicate token error")

        # if api_key isn't in apikeys - then add it
        await client.rpush("badge_apikeys", [new_token])
        await client.json.set(f"{r.myUUID}", ".", j)

        return j

    else:
        print(f"Badge {r.myUUID} already exists.")
        raise HTTPException(status_code=400, detail="Badge already exists")


@app.post("/checkin")
async def checkIn(r: OnlyUUID, api_key: str = Security(get_api_key)):
    """
    POST request with json body: {"myUUID": "uuid"}
    returns full json structure for player
    """
    # use badge_id to lookup json from redis
    # if there's a result, return the json structure
    # check if badge_id exists in redis
    j = await client.json.get(r.myUUID, ".")

    if not j:
        raise HTTPException(status_code=404, detail="Badge not found")

    if isinstance(j, dict) and "token" in j:
        if not j["token"] == api_key:
            raise HTTPException(status_code=404, detail="Badge not found")
        else:
            if check_intro_started():
                if isinstance(j, dict) and "intro" in j:
                    j["intro"]["enabled"] = 1
                    return j
                else:
                    raise HTTPException(
                        status_code=500, detail="Unable to checkin - Data error"
                    )
            else:
                return j


@app.post("/start_the_intro")
async def startintro(r: Admin):
    """
    POST request with key = "ADMINSONLY"
    returns "intro started" if successful
    returns 404 if key is invalid
    """
    if r.key == "ADMINSONLY":
        f = open("intro_started", "w")
        f.write("intro started")
        f.close()
        return "intro started"
    else:
        raise HTTPException(status_code=404)


@app.post("/deletebadge")
async def deletebadge(r: Register, api_key: str = Security(get_api_key)):
    """
    POST request with json body: {"myUUID": "uuid", "key": "key"}
    returns "deleted" if successful
    """
    j = await client.json.get(r.myUUID, ".")

    if not j:
        raise HTTPException(status_code=404, detail="Badge not found")

    if isinstance(j, dict) and "token" in j:
        if not j["token"] == api_key:
            raise HTTPException(status_code=404, detail="Badge not found")

        else:
            if r.key == "THISWILLDELETEBADGE":
                if isinstance(j, dict) and "IR_ID" in j:
                    await client.delete(j["IR_ID"])
                    await client.json.delete(r.myUUID)
                    return "deleted"
                else:
                    raise HTTPException(
                        status_code=500, detail="Unable to delete badge - Data error"
                    )
    else:
        raise HTTPException(
            status_code=500, detail="Unable to delete badge - Data error"
        )


@app.post("/hiddenobject")
async def hiddenobject(r: UUID_ObjectID, api_key: str = Security(get_api_key)):
    j = await client.json.get(r.myUUID)

    if not j:
        raise HTTPException(status_code=404, detail="Badge not found")

    if isinstance(j, dict) and "token" in j:
        if not j["token"] == api_key:
            raise HTTPException(status_code=404, detail="Badge not found")

        if r.objectid:
            if r.objectid == uber1uuid:
                j["challenge2"]["status"][0] = 1
            elif r.objectid == uber2uuid:
                j["challenge2"]["status"][1] = 1
            elif r.objectid == uber3uuid:
                j["challenge2"]["status"][2] = 1
            elif r.objectid == uber4uuid:
                j["challenge2"]["status"][3] = 1
            elif r.objectid == uber5uuid:
                j["challenge2"]["status"][4] = 1
            else:
                raise HTTPException(status_code=404, detail="Object not found")

        # is challenge 2 complete?
        if j["current_challenge"] == "challenge2":
            if j["challenge2"]["status"] == [1, 1, 1, 1, 1]:
                j["challenge2"]["complete"] = 1
                j["current_challenge"] = "challenge3"
        else:
            raise HTTPException(status_code=400, detail="Challenge not started")

    await client.json.set(r.myUUID, ".", j)
    return j


@app.post("/monkeysee")
async def monkeysee(r: UUID_ObjectID, api_key: str = Security(get_api_key)):
    j = await client.json.get(r.myUUID)

    if not j:
        raise HTTPException(status_code=404, detail="Badge not found")

    if isinstance(j, dict) and "token" in j:
        if not j["token"] == api_key:
            raise HTTPException(status_code=404, detail="Badge not found")

        if r.objectid:
            if r.objectid == cansuuid:
                j["challenge3"]["interact_cans"] = 1
            elif r.objectid == micuuid:
                j["challenge3"]["interact_mic"] = 1
            elif r.objectid == shadesuuid:
                j["challenge3"]["interact_shades"] = 1
            else:
                raise HTTPException(status_code=404, detail="Unknown Monkey")

        # is challenge 3 complete?
        if j["current_challenge"] == "challenge3":
            # have I seen all the monkeys?
            if (
                j["challenge3"]["interact_cans"] == 1
                and j["challenge3"]["interact_mic"] == 1
                and j["challenge3"]["interact_shades"] == 1
            ):
                j["challenge3"]["complete"] = 1
                j["current_challenge"] = "winner"

    await client.json.set(r.myUUID, ".", j)
    return j


@app.post("/friendrequest")
async def friendrequest(r: UUID_IRID, api_key: str = Security(get_api_key)):
    """
    Creates a match with another badge
    Adds the match to the player's json['challenge1']['matches'] list as a string
    with the format of "handle:uuid".  this can be processed by client to
    display the handle.

    POST request with json body:{ myUUID: "uuid", remoteIRID: "irid" }
    returns full json structure for player
    """
    myjson = await client.json.get(r.myUUID)

    if not myjson:
        raise HTTPException(status_code=404, detail="Badge not found")

    if isinstance(myjson, dict) and "token" in myjson and "IR_ID" in myjson:
        if not myjson["token"] == api_key:
            raise HTTPException(status_code=404, detail="Badge not found")

        if str(myjson["IR_ID"]) == r.remoteIRID:
            raise HTTPException(status_code=400, detail="Cannot pair with yourself")
    else:
        raise HTTPException(status_code=500, detail="Data error")

    # does the irid exist in redis?
    if await client.get(r.remoteIRID):
        # get the uuid from the irid
        remote_uuid = await client.get(r.remoteIRID)
        if isinstance(remote_uuid, bytes):
            remote_uuid = remote_uuid.decode()
        else:
            raise HTTPException(status_code=500, detail="Error decoding IRID")

        # get the handle from the player's uuid json key
        remote_json = await client.json.get(remote_uuid, ".")

        if remote_json:
            if isinstance(myjson, dict) and "challenge1" in myjson:
                for item in myjson["challenge1"]["matches"]:
                    if ":" in item and item.split(":")[1] == remote_uuid:
                        raise HTTPException(status_code=400, detail="Already friends")
                else:
                    if isinstance(remote_json, dict) and "badgeHandle" in remote_json:
                        myjson["challenge1"]["matches"].append(
                            f"{remote_json['badgeHandle']}:{remote_uuid}"
                        )
                        # is Challenge 1 complete? if so, set current_challenge to challenge2
                        # and set challenge1 complete to 1
                        if myjson["current_challenge"] == "challenge1":
                            if len(myjson["challenge1"]["matches"]) >= 5:
                                myjson["challenge1"]["complete"] = 1
                                myjson["current_challenge"] = "challenge2"

                        await client.json.set(r.myUUID, ".", myjson)
                        return myjson
                    else:
                        raise HTTPException(status_code=500, detail="Data error")
            else:
                raise HTTPException(status_code=500, detail="Data error")
        else:
            raise HTTPException(status_code=404, detail="Remote Badge not found")
    else:
        raise HTTPException(status_code=404, detail="Remote IRID not found")


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")
