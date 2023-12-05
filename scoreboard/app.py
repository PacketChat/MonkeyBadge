import coredis
from flask import Flask, render_template
import random
import re

app = Flask(__name__)


def is_valid_uuid(mac):
    """
    Checks if the given string is a valid MAC address with dashes.

    Args:
    mac (str): The MAC address to check.

    Returns:
    bool: True if the MAC address is valid, False otherwise.
    """
    # Regular expression for matching a MAC address with dashes
    pattern = "^([0-9A-Fa-f]{2}-){5}([0-9A-Fa-f]{2})$"

    # Using re.match to check if the MAC address matches the pattern
    if re.match(pattern, mac):
        return True
    else:
        return False


async def get_redis_data():
    try:
        r = await coredis.Redis(host="127.0.0.1", port=6379)
        result = []
        keys = await r.keys("*")
        for key in keys:
            print(key)
            # if the key matches a mac address
            if is_valid_uuid(key.decode()):
                data = await r.json.get(key)
                if data["intro"]["complete"]:
                    try:
                        matches = len(data["challenge1"]["matches"])
                    except:
                        matches = 0
                    # compute the rank
                    score = 0
                    if data["challenge1"]["complete"]:
                        score += 1000
                    if data["challenge2"]["complete"]:
                        score += 2000
                    if data["challenge3"]["complete"]:
                        score += 3000
                    score += matches
                    d = {
                        "handle": data["badgeHandle"],
                        "score": score,
                        "challenge1": data["challenge1"]["complete"],
                        "challenge2": data["challenge2"]["complete"],
                        "challenge3": data["challenge3"]["complete"],
                        "matches": matches,
                    }
                    print(d)
                    result.append(d)
        sorted_list = sorted(result, key=lambda x: x["score"], reverse=True)
    except:
        sorted_list = []

    return sorted_list


def random_motd():
    messages = [
        "Customize your player handle via CLI with badgecli!",
        "hackers gonna hack",
        "I'm in ur badge, hacking ur stuff",
        "Monkey See, Monkey Hack",
        "Hack the Planet!",
        "Hushcon - Now with more /<-r4d!",
        "ir 1337 h4x0r",
    ]
    return random.choice(messages)


@app.route("/")
async def index():
    data_dict = await get_redis_data()
    motd = random_motd()
    return render_template("scoreboard.html", data=data_dict, motd=motd)


if __name__ == "__main__":
    app.run(debug=True, port=8080)
