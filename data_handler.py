import json
from collections import namedtuple
import discord

def get_users():
    with open("database/users.json", "r") as f:
        data = json.load(f)
        out = dict()
        UserInfo = namedtuple("UserInfo", [
            "num_jams",
            "date_joined"
        ])

        for uid, info in data["users"].items():
            num_jams, date_joined = None, None
            if "num_jams"    in info: num_jams    = int(info["num_jams"])
            if "date_joined" in info: date_joined =   info["date_joined"]
            out[uid] = UserInfo(num_jams, date_joined)
        return out
def user_dict():
    with open("database/users.json", "r") as f:
        return json.load(f)
    
def add_or_config_user(uid, info):
    data = {}
    with open("database/users.json", "r") as f:
        data = json.load(f)
    data["users"][uid] = info
    with open("database/users.json", "w") as f:
        f.write(json.dumps(data, indent=4))
def remove_user(uid):
    data = {}
    with open("database/users.json", "r") as f:
        data = json.load(f)
    try:
        del data["users"][uid]
    except KeyError:pass
    with open("database/users.json", "w") as f:
        f.write(json.dumps(data, indent=4))

def get_jam_embed():
    data = {}
    with open("database/jam_info.json", "r") as f:
        data = json.load(f)
    if data == {}: return None

    title = data["name"]
    theme = data["topic"]
    embed = discord.Embed(title=theme, description=f"""This is {title}.{" Here's some more info:" if len(data["info"]) > 0 else  "Wow no info, have fun!"}""", color=0xFF0000)
    for inf in data["info"]:
        embed.add_field(name=list(inf.keys())[0], value=inf[list(inf.keys())[0]], inline=False)
    return (title, embed)

def get_jaminfo():
    data = {}
    with open("database/jam_info.json", "r") as f:
        data = json.load(f)
    return data

def test():
    add_or_config_user("Test2", {
        "num_jams": 1,
        "date_joined": "5-5-2023"
    })

if __name__ == "__main__":
    test()