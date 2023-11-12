from fastapi import FastAPI, HTTPException, Security, Request, status, Header
from fastapi.security import APIKeyHeader 
from hrid import HRID
import secrets
from keystore import ApiKeyStore
from pydantic import BaseModel
import coredis
import json

import uvicorn

app = FastAPI()

# Generate a python UUID
import uuid
from uuid import UUID

myUUID = uuid.uuid4()

registration_key = "7bc78281-2036-41b2-8d98-fc23ec504e9a"

uber1uuid = "bb4a84dc-cf4b-4d04-84fd-1c1cc8799e0d"
uber2uuid = "4ec2d946-05fa-4f34-a033-278a6d1ac222"
uber3uuid = "7bc78281-2036-41b2-8d98-fc23ec504e9a"
uber4uuid = "0bd0d58f-fb52-4859-9bd2-435f0af39e62"
uber5uuid = "a4860c69-4e4d-4c30-bf30-9f7c982df55d"

cansuuid = "c71ec72e-c063-48c0-a3f9-ce5af406445f"
micuuid = "7f19e4b1-b6b2-49be-8b27-6061fdaf5ef0"
shadesuuid = "aa0b8824-53d0-4c46-8c08-ad75baf9d1d5"


templateJSON = """
{
    "badgeHandle": "thephreak",
    "current_challenge": "intro",
    "last_seen": "2014-06-25T00:00:00.000Z",
    "match_mode": false,
    "token": "",
    "intro": {
        "intro_enabled": false,
        "intro_complete": false
    },
    "challenge1": {
        "complete": false,
        "matches": []
    },
    "challenge2": {
        "complete": "false",
        "interact_uber1": "",
        "interact_uber2": "",
        "interact_uber3": "",
        "interact_uber4": "",
        "interact_uber5": ""
    },
    "challenge3": {
        "complete": false,
        "interact_cans": "",
        "interact_mic": "",
        "interact_shades": ""
    },
    "antisocial_monkey_club": "false",
    "battles": {
        "won": "0",
        "lost": "0",
        "level": "1"
    }
}
"""
api_key_header = APIKeyHeader(name="X-API-Key")

client = coredis.Redis(host='127.0.0.1', port=6379)

class Match(BaseModel):
    targetUUID: str
    key: str

class Handle(BaseModel):
    handle: str
    key: str

class Register(BaseModel):
    myUUID: str
    key: str
    handle: str

class Checkin(BaseModel):
    myUUID: str

async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if await ApiKeyStore.does_api_key_exist(client, api_key_header):
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )

def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test

async def isValidBadge(badge_id):
    # check if badge_id is valid
    # return true if valid
    # return false if not valid

    j = await client.json.get(badge_id, ".")
    print(j)
    if not j:
        return False
    else:
        return True

async def isBadgeInParingMode(badge_id):
    # check if badge_id is in pairing mode
    # if badge_id is in pairing mode, return true
    # if badge_id is not in pairing mode, return false
    
    badgelist = await client.lrange("matchmodebadges", 0, -1)

    # if the badge is in the list - return true
    for i in badgelist:
        if i.decode() == badge_id:
            return True
    # otherwise return false
    return False

async def validateKey(badge_id, key):
    # check if the key is valid for the badge_id
    # if valid, return true
    # if invalid, return false
    j = await client.json.get(badge_id, ".")
    if not j:
        return False
    else:
        if j['token'] == key:
            return True
        else:
            return False

async def updatefield(badge_id, key, value):
    # change the handle of a badge
    j = await client.json.get(badge_id, ".")
    j[key] = value
    await client.json.set(badge_id, ".", j)
    return True

@app.get("/generate_handle")
def generate_handle():
    hruuid=HRID(hridfmt=('adjective', 'noun'))
    handle = hruuid.generate()
    return handle

@app.post("/changehandle/{badge_id}")
async def changehandle(badge_id, r: Handle):

    if not r.handle:
        raise HTTPException(status_code=400, detail="Request body missing")

    # change the handle of a badge
    if not await isValidBadge(badge_id):
        raise HTTPException(status_code=404, detail="Badge not found")
    else:
        await updatefield(badge_id, "badgeHandle", r.handle)
        return str({ "badge_id": badge_id, "message": f"changed handle for {badge_id} to {r.handle}"})

@app.post("/register")
async def register(r: Register):
    # create a new badge in redis from the templateJSON string
    
    #if not is_valid_uuid(r.myUUID): 
    #    print(f"UUID: {r.myUUID} invalid.")
    #    raise HTTPException(status_code=400, detail="Invalid UUID")

    if r.key != registration_key:
        print(f"Invalid Registration key: {r.key}")
        raise HTTPException(status_code=400, detail="Invalid registration key")

    # see if the badge_id exists in redis already
    if not await isValidBadge(r.myUUID):
        j = json.loads(templateJSON)
        #j['token'] = r.key
        j['badgeHandle'] = r.handle

        await client.json.set(f"{r.myUUID}", ".", j)
        generated_key = secrets.token_urlsafe(16)
        await ApiKeyStore.create_api_key(client, r.myUUID, generated_key)

        return { "UUID": r.myUUID, "token": generated_key }

    else:
        print("Badge {r.myUUID} already exists.")
        raise HTTPException(status_code=400, detail="Badge already exists")


@app.post("/checkin")
async def checkIn(r: Checkin, api_key: str = Security(get_api_key)):
    # use badge_id to lookup json from redis
    # if there's a result, return the json structure
    # check if badge_id exists in redis
    j = await client.json.get(r.myUUID, ".")

    if not j:
        raise HTTPException(status_code=404, detail="Badge not found")
    
    if j['token'] != api_key:
          raise HTTPException(status_code=400, detail="API Key mismatch")
    else:
        return j


@app.get("/disablematchmode/{badge_id}")
async def disablematchmode(badge_id):
    # match mode will set the match_mode flag to false in the badge json

    # check if badge_id exists in redis
    j = await client.json.get(badge_id, ".")
    if not j:
        raise HTTPException(status_code=404, detail="Badge not found")
    else:
        if await client.lrem("matchmodebadges", 1, badge_id):
            return str({ "badge_id": badge_id, "message": "matchmode disabled." })
        else:
            return str({ "badge_id": badge_id, "message": "matchmode already disabled." })

@app.get("/enablematchmode/{badge_id}")
async def enablematchmode(badge_id):
    # match mode will set the match_mode flag to true in the badge json
    # todo: disable match_mode after 5 minutes - this might be a job that runs.

    # check if badge_id exists in redis
    j = await client.json.get(badge_id, ".")
    if not j:
        raise HTTPException(status_code=404, detail="Badge not found")
    else:
        badgelist = await client.lrange("matchmodebadges", 0, -1)
        print(badgelist)

        # search l for badge_id in bytes format
        for i in badgelist:
            if i.decode() == badge_id:
                return str({ "badge_id": badge_id, "message": "matchmode already enabled" })
        
        await client.rpush("matchmodebadges", badge_id.split())
        return str({ "badge_id": badge_id, "message": "matchmode enabled" })

@app.post("submit_challenge/{challenge_id}")
def submit_challenge(challenge_id):
    pass

@app.get("/listpairingmodebadges/{badge_id}")
async def getpairingmodebadges(badge_id):
    # this call will return a list of badges that are currently in match mode
    # reads a redis key list called matchmodebadges

    if await isBadgeInParingMode(badge_id):
        l = await client.lrange("matchmodebadges", 0, -1)
        print(l)
        return l
    else:
        raise HTTPException(status_code=400, detail="Matchmode not enabled")

@app.post("/match/{badge_id}")
async def match(badge_id, r: Match):
    # this call will be used to match badges, the request body will contain the target badge id and a key
    # the key will be used to validate the request
    # if the key is valid, the target badge id will be added to the matches array in the badge json
    # if the key is invalid, the request will be rejected
    # only the requesting badge will be updated.    


    # todo: badges shouldnt match unless BOTH are in matching mode.

    if not r:
        raise HTTPException(status_code=400, detail="Request body missing")
    
    targetBadge = await client.json.get(r.targetUUID, ".")
    if not targetBadge:
        raise HTTPException(status_code=404, detail="Target badge not found")
    else:  
        j = await client.json.get(badge_id, ".")

        if not j:
            raise HTTPException(status_code=404, detail="Badge not found")
        else:
            badgelist = await client.lrange("matchmodebadges", 0, -1)
            
            # both badges must be in pairing mode for this to work.
            if await isBadgeInParingMode(badge_id):
                if await isBadgeInParingMode(r.targetUUID):
                    if r.key != "abcdefg":
                        return "invalid key"
                    else:
                        if not r.targetUUID in j['challenge1']['matches']:
                            j['challenge1']['matches'].append(r.targetUUID)
                            await client.json.set(badge_id, ".", j)
                            return "match made"
                        else:
                            return "match already made"
                else:
                    return f"{targetBadge} not in match mode"
            else:
                return f"{badge_id} not in match mode"

@app.post("/deletebadge")
async def deletebadge(r: Register):
    if r.key == "THISWILLDELETEBADGE":
        await client.json.delete(r.myUUID)
        return "deleted"
    pass

if __name__ == '__main__':
    uvicorn.run(app, port=8000, host='0.0.0.0')