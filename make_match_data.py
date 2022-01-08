# %%
import numpy as np
import pandas as pd
import yaml

# %%
def flatten(iterable, key = "", result = {}):
    """ Recursive Function which systematicallt Flattens nested lists and/or dictionaries"""
    if type(iterable) == dict:
        for i in iterable:
            data_type = type(iterable[i])
            if data_type in [int, str, float]:
                result[key + i] = iterable[i]
            elif data_type == list:
                flatten(iterable[i], key = key + i + "_", result = result)
            elif data_type == dict:
                flatten(iterable[i], key = key + i + "_", result = result)
    elif type(iterable) == list:
        length = len(iterable)
        for i in range(length):
            data_type = type(iterable[i])
            if data_type in [int, str, float]:
                result[key + str(i)] = iterable[i]
            elif data_type == list:
                flatten(iterable[i], key = key + str(i) + "_", result = result)
            elif data_type == dict:
                flatten(iterable[i], key = key + str(i) + "_", result = result)

    else:
        Error("An unidentified type {} has been passed in as an iterable!".format(type(iterable)))
    return result

# %%
with open("bbl_json/README.txt", "r") as file:
    strings = file.readlines()
    data = strings[24::]
    data = [i.split(" - ") for i in data]
    data = [i[0:5] + [i[5][:-1].split(" vs ")[0]] + [i[5][:-1].split(" vs ")[1]] for i in data]
    data = pd.DataFrame(
        {i[0]:i[1::] for i in data}, 
        index=["Club", "Game", "Gender", "Id", "Team_1", "Team_2"]
        ).transpose()
    data = data[["Team_1", "Team_2", "Id"]]

data["Date"] = data.index

# %%
result = pd.DataFrame()

# %%
for i in range(data.shape[0]):
    index = data.iloc[i]["Id"]
    with open("bbl_json/{}.json".format(index), "r") as file:
        match_data = yaml.safe_load(file)
        file.close()
    info = match_data['info']
    dictionary = flatten(info)
    dictionary["game_id"] = index
    for team_num in range(2):
        for player_num in range(11):
            player_name = dictionary.pop("players_{}_{}".format(dictionary["teams_{}".format(team_num)], player_num))
            registry_number = dictionary.pop("registry_people_{}".format(player_name))
            dictionary["players_team{}_player_{}".format(team_num, player_num)] = player_name
            dictionary["registry_team{}_player_{}".format(team_num, player_num)] = registry_number

    supersub_keys = [k for k in dictionary.keys() if "supersubs" in k]
    drop_keys = [k for k in dictionary.keys() if "registry_people_" in k]
    player_keys = [k for k in dictionary.keys() if "players_" in k and "players_team" not in k]

    for k in supersub_keys:
        team = k.split("_")[1]
        team_num = 0 if team == dictionary["teams_0"] else 1
        dictionary["supersubs_team_{}".format(team_num)] = dictionary.pop(k)

    for k in drop_keys:
        del dictionary[k]

    for k in player_keys:
        team = k.split("_")[1]
        team_num = 0 if team == dictionary["teams_0"] else 1
        # print(team, dictionary["teams_0"])
        dictionary["extra_players_team_{}".format(team_num)] = dictionary.pop(k)

    for key in dictionary.keys():
        result.loc[index, key] = dictionary[key]

    # print(dictionary.keys())
    # [print(i) for i in dictionary.keys()]
    # break
    print(i, "/", data.shape[0], end = '\r')


# %%
result.to_csv("match_data.csv")


