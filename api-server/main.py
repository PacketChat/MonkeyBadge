import json
import os
import random
import secrets

from fastapi import FastAPI, HTTPException, Security, Request, status, Header
from fastapi.security import APIKeyHeader
from hrid import HRID
from keystore import ApiKeyStore
from pydantic import BaseModel
import coredis
import uvicorn

app = FastAPI()

# Generate a python UUID
import uuid
from uuid import UUID

myUUID = uuid.uuid4()

redishost = os.environ.get('MB_REDIS_HOST', '127.0.0.1')
redisport = os.environ.get('MB_REDIS_PORT', '6379')

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
        "interact_uber1": "",
        "interact_uber2": "",
        "interact_uber3": "",
        "interact_uber4": "",
        "interact_uber5": ""
    },
    "challenge3": {
        "complete": 0,
        "interact_cans": "",
        "interact_mic": "",
        "interact_shades": ""
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
    Check if the intro challenge has been started by looking for the existance of a drop file
    """
    if os.path.exists("intro_started"):
        return True
    else:
        return False

api_key_header = APIKeyHeader(name="X-API-Key")

client = coredis.Redis(host=redishost, port=redisport)

class Admin(BaseModel):
    key: str

class Handle(BaseModel):
    myUUID: str
    handle: str
    key: str

class Register(BaseModel):
    myUUID: str
    key: str
    handle: str

class UUID_IRID(BaseModel):
    myUUID: str
    remoteIRID: str

class OnlyUUID(BaseModel):
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

@app.post("/changehandle}")
async def changehandle(r: Handle, api_key: str = Security(get_api_key)):
    j = await client.json.get(r.myUUID, ".")

    if not j:
        raise HTTPException(status_code=404, detail="Badge not found")

    if j['token'] != api_key:
        raise HTTPException(status_code=404, detail="Badge not found")

    if not r.handle:
        raise HTTPException(status_code=400, detail="Request body missing")
    
    await updatefield(r.myUUID, "badgeHandle", r.handle)
    return str({ "badge_id": r.myUUID, "message": f"changed handle for {r.myUUID} to {r.handle}"})

@app.post("/introcomplete")
async def introcomplete(r: OnlyUUID, api_key: str = Security(get_api_key)):
    # use badge_id to lookup json from redis
    # if there's a result, return the json structure
    # check if badge_id exists in redis
    j = await client.json.get(r.myUUID, ".")

    if not j:
        raise HTTPException(status_code=404, detail="Badge not found")

    if j['token'] != api_key:
          raise HTTPException(status_code=404, detail="Badge not found")
    else:
        j['intro']['complete'] = 1
        await client.json.set(r.myUUID, ".", j)
    return j

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
async def checkIn(r: OnlyUUID, api_key: str = Security(get_api_key)):
    # use badge_id to lookup json from redis
    # if there's a result, return the json structure
    # check if badge_id exists in redis
    j = await client.json.get(r.myUUID, ".")

    if not j:
        raise HTTPException(status_code=404, detail="Badge not found")

    if j['token'] != api_key:
          raise HTTPException(status_code=400, detail="Badge not found")
    else:
        if check_intro_started() == True:
            j['intro']['enabled'] = 1
        return j

@app.post("/start_the_intro")
async def startintro(r: Admin):
    if r.key == "ADMINSONLY":
        f = open("intro_started", "w")
        f.write("intro started")
        f.close()
        return "intro started"
    pass

@app.post("/deletebadge")
async def deletebadge(r: Register, api_key: str = Security(get_api_key)):
    j = await client.json.get(r.myUUID, ".")

    if not j:
        raise HTTPException(status_code=404, detail="Badge not found")

    if j['token'] != api_key:
          raise HTTPException(status_code=404, detail="Badge not found")
    
    else:
        if r.key == "THISWILLDELETEBADGE":
            await client.delete(j['IR_ID'])
            await client.json.delete(r.myUUID)
            return "deleted"

@app.post("/getIRID")
async def getIRID(r: OnlyUUID, api_key: str = Security(get_api_key)):
    # use badge_id to lookup json from redis
    # if there's a result, return the json structure
    # check if badge_id exists in redis
    j = await client.json.get(r.myUUID, ".")

    if not j:
        raise HTTPException(status_code=404, detail="Badge not found")

    if j['token'] != api_key:
          raise HTTPException(status_code=404, detail="Badge not found")
    
    else:
        # does the badge have an IRID already?
        # if so, return it
        # if not, generate one and return it and save it to the redis key

        if not j['IR_ID']:
            # generate an IRID
            while True:
                irid = random.getrandbits(16)
                if not await client.json.get(irid, "."):
                    # update the player in redis with the IR_ID
                    await updatefield(r.myUUID, "IR_ID", irid)
                    # create a redis key/value pair of the IR_ID with the uuid as the value
                    await client.set(irid, r.myUUID)
                    break
        else:
            irid = j['IR_ID']
        # return the player's irid
        return j

@app.post("/friendrequest")
async def friendrequest(r: UUID_IRID, api_key: str = Security(get_api_key)):
    """
    process a friend request with another badge

    json request body: 
    {
        myUUID: "uuid",
        remoteIRID: "irid"
    }
    
    adds the match to the player's json['challenge1']['matches'] list as a string
    with the format of "handle:uuid".  this can be processed by client to
    display the handle.

    returns the remote uuid and handle if successful
    """
    myjson = await client.json.get(r.myUUID)

    if not myjson:
        raise HTTPException(status_code=404, detail="Badge not found")

    if myjson['token'] != api_key:
          raise HTTPException(status_code=404, detail="Badge not found")
    
    else:
        # does the irid exist in redis?
        if await client.get(r.remoteIRID):

            # get the uuid from the irid key
            if not await client.get(r.remoteIRID):
                raise HTTPException(status_code=404, detail="Remote Badge not found")

            remote_uuid = await client.get(r.remoteIRID)
            remote_uuid = remote_uuid.decode()

            # get the handle from the player's uuid json key
            remote_json = await client.json.get(remote_uuid, ".")

            if not remote_json:
                raise HTTPException(status_code=404, detail="Remote Badge not found")
            else:
                for item in myjson['challenge1']['matches']:
                    if item.split(":")[1] == remote_uuid:
                        raise HTTPException(status_code=400, detail="Already friends")
                else:
                    myjson['challenge1']['matches'].append(f"{remote_json['badgeHandle']}:{remote_uuid}")
                    await client.json.set(r.myUUID, ".", myjson)
                    return { "remote_uuid": remote_uuid, 
                            "remote_handle": remote_json['badgeHandle']}
        else:
            raise HTTPException(status_code=404, detail="IRID not found")
    
if __name__ == '__main__':
    uvicorn.run(app, port=8000, host='0.0.0.0')
