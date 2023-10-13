from pydantic import BaseModel
import coredis

import base64
import json

class ApiKeyStore:
    async def create_api_key(client, badge_id, api_key):
        j = await client.json.get(badge_id, ".")
        j['token'] = api_key
        await client.json.set(badge_id, ".", j)
        apikeys = await client.lrange("badge_apikeys", 0, -1)

        # search l for badge_id in bytes format
        for i in apikeys:
            if i.decode() == api_key:
                return
        
        # if api_key isn't in apikeys - then add it
        await client.rpush("badge_apikeys", api_key.split())

    #@cached(cache=TTLCache(maxsize=1024, ttl=300)) # 5 minutes
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