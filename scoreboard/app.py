import coredis
from flask import Flask, render_template

app = Flask(__name__)

# TODO: refactor out redis, only use coredis.

# Establish a connection to the Redis server
r = redis.StrictRedis(host='localhost', port=6379, db=0)

async def get_redis_data():

    try: 
        r = await coredis.Redis(host='127.0.0.1', port=6379)
        result = []
        keys = await r.keys("*")
        for key in keys:
            if not key == b"badge_apikeys":
                data = await r.json.get(key)
                if data['intro']['complete'] == 1:
                    try:
                        matches = len(data['challenge1']['matches'])
                    except:
                        matches = 0
                    # compute the rank
                    score = 0
                    if data['challenge1']['complete'] == 1:
                        score += 1000
                    if data['challenge2']['complete'] == 1:
                        score += 2000
                    if data['challenge3']['complete'] == 1:
                        score += 3000
                    score += matches
                    d = {
                        "handle": data['badgeHandle'],
                        "score": score,
                        "challenge1": data['challenge1']['complete'],
                        "challenge2": data['challenge2']['complete'],
                        "challenge3": data['challenge3']['complete'],
                        "matches": matches
                    }
                    print(d)
                    result.append(d)
        sorted_list = sorted(result, key=lambda x: x['score'], reverse=True)
    except:
        sorted_list = []

    return sorted_list

@app.route('/')
async def index():
    data_dict = await get_redis_data()

    return render_template('scoreboard.html', data=data_dict)

if __name__ == '__main__':
    app.run(debug=False)
