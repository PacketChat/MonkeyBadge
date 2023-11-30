import coredis
import json
import asyncio
from uuid import uuid4
from hrid import HRID
from time import sleep

TESTAPIKEY = "testapikey"
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
async def create_api_key(client, badge_id, api_key):
        print(f"{badge_id} {api_key}")
        apikeys = await client.lrange("badge_apikeys", 0, -1)

        # search l for badge_id in bytes format
        for i in apikeys:
            if i.decode() == api_key:
                return

        # if api_key isn't in apikeys - then add it
        await client.rpush("badge_apikeys", api_key.split())

async def main():
    client = coredis.Redis(host='127.0.0.1', port='6379')
    """
    # create 100 rando badges
    for i in range(1, 100):
        uuid = uuid4()
        j = json.loads(templateJSON)
        hruuid = HRID(hridfmt=('adjective', 'noun'))
        handle = hruuid.generate()
        j['badgeHandle'] = handle # create random handle
        j['token'] = TESTAPIKEY
        await client.json.set(f"{uuid}", ".", j)
        await create_api_key(client, uuid, TESTAPIKEY)
    """

    # create top 5 badges
    # only Intro
    uuid = uuid4()
    j = json.loads(templateJSON)
    hruuid = HRID(hridfmt=('adjective', 'noun'))
    handle = hruuid.generate()
    j['badgeHandle'] = handle # create random handle
    j['token'] = TESTAPIKEY
    j['intro']['complete'] = 1
    await client.json.set(f"{uuid}", ".", j)
    await create_api_key(client, uuid, TESTAPIKEY)

    # Intro and Challenge 1
    uuid = uuid4()
    j = json.loads(templateJSON)
    hruuid = HRID(hridfmt=('adjective', 'noun'))
    handle = hruuid.generate()
    j['badgeHandle'] = handle # create random handle
    j['token'] = TESTAPIKEY
    j['intro']['complete'] = 1
    j['challenge1']['complete'] = 1
    await client.json.set(f"{uuid}", ".", j)
    await create_api_key(client, uuid, TESTAPIKEY)


    # Intro and Challenge 1 and Challenge 2
    uuid = uuid4()
    j = json.loads(templateJSON)
    hruuid = HRID(hridfmt=('adjective', 'noun'))
    handle = hruuid.generate()
    j['badgeHandle'] = handle # create random handle
    j['token'] = TESTAPIKEY
    j['intro']['complete'] = 1
    j['challenge1']['complete'] = 1
    j['challenge2']['complete'] = 1
    j['challenge1']['matches'] = ['1', '2', '3', '4', '5']
    await client.json.set(f"{uuid}", ".", j)
    await create_api_key(client, uuid, TESTAPIKEY)

    # Intro and Challenge 1 and Challenge 2 and matches
    uuid = uuid4()
    j = json.loads(templateJSON)
    hruuid = HRID(hridfmt=('adjective', 'noun'))
    handle = hruuid.generate()
    j['badgeHandle'] = handle # create random handle
    j['token'] = TESTAPIKEY
    j['intro']['complete'] = 1
    j['challenge1']['complete'] = 1
    j['challenge2']['complete'] = 1
    j['challenge1']['matches'] = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    await client.json.set(f"{uuid}", ".", j)
    await create_api_key(client, uuid, TESTAPIKEY)

    uuid = uuid4()
    j = json.loads(templateJSON)
    hruuid = HRID(hridfmt=('adjective', 'noun'))
    handle = hruuid.generate()
    j['badgeHandle'] = handle # create random handle
    j['token'] = TESTAPIKEY
    j['intro']['complete'] = 1
    j['challenge1']['complete'] = 1
    j['challenge2']['complete'] = 1
    j['challenge3']['complete'] = 1
    j['challenge1']['matches'] = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
    await client.json.set(f"{uuid}", ".", j)
    await create_api_key(client, uuid, TESTAPIKEY)

asyncio.run(main())