import coredis
import json
import asyncio
from uuid import uuid4
from hrid import HRID


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

async def main():
    client = coredis.Redis(host='127.0.0.1', port='6379')

    # create 100 rando badges
    for i in range(1, 100):
        uuid = uuid4()
        j = json.loads(templateJSON)
        hruuid=HRID(hridfmt=('adjective', 'noun'))
        handle = hruuid.generate()
        j['badgeHandle'] = handle # create random handle
        await client.json.set(f"{uuid}", ".", j)

    # create top 5 badges

    # only Intro
    uuid = uuid4()
    j = json.loads(templateJSON)
    hruuid=HRID(hridfmt=('adjective', 'noun'))
    handle = hruuid.generate()
    j['badgeHandle'] = handle # create random handle
    j['intro']['complete'] = 1
    await client.json.set(f"{uuid}", ".", j)

    # Intro and Challenge 1
    uuid = uuid4()
    j = json.loads(templateJSON)
    hruuid=HRID(hridfmt=('adjective', 'noun'))
    handle = hruuid.generate()
    j['badgeHandle'] = handle # create random handle
    j['intro']['complete'] = 1
    j['challenge1']['complete'] = 1
    await client.json.set(f"{uuid}", ".", j)

    # Intro and Challenge 1 and Challenge 2
    uuid = uuid4()
    j = json.loads(templateJSON)
    hruuid=HRID(hridfmt=('adjective', 'noun'))
    handle = hruuid.generate()
    j['badgeHandle'] = handle # create random handle
    j['intro']['complete'] = 1
    j['challenge1']['complete'] = 1
    j['challenge2']['complete'] = 1
    j['challenge1']['matches'] = ['1', '2', '3', '4', '5']
    await client.json.set(f"{uuid}", ".", j)

    # Intro and Challenge 1 and Challenge 2 and matches
    uuid = uuid4()
    j = json.loads(templateJSON)
    hruuid=HRID(hridfmt=('adjective', 'noun'))
    handle = hruuid.generate()
    j['badgeHandle'] = handle # create random handle
    j['intro']['complete'] = 1
    j['challenge1']['complete'] = 1
    j['challenge2']['complete'] = 1
    j['challenge1']['matches'] = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    await client.json.set(f"{uuid}", ".", j)

    uuid = uuid4()
    j = json.loads(templateJSON)
    hruuid=HRID(hridfmt=('adjective', 'noun'))
    handle = hruuid.generate()
    j['badgeHandle'] = handle # create random handle
    j['intro']['complete'] = 1
    j['challenge1']['complete'] = 1
    j['challenge2']['complete'] = 1
    j['challenge3']['complete'] = 1
    j['challenge1']['matches'] = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
    await client.json.set(f"{uuid}", ".", j)

asyncio.run(main())