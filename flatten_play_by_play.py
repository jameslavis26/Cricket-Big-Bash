# %%
import numpy as np
import pandas as pd
import mysql.connector
from mysql.connector import Error
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
def add_match_data(data, result, index):
    teams = [i['team'] for i in data]
    for i in range(len(data)):
        if i >= 2:
            Error("More than 2 innings!!")
        batting_team = teams[i]
        bowling_team = teams[i % 1]
        inning = i
        for over in data[i]["overs"]:
            over_num = over["over"]
            for ball_num in range(len(over['deliveries'])):
                ball = over['deliveries'][ball_num]
                ball_id = index + str(inning) + str(over_num) + str(ball_num)
                dictionary = flatten(ball)

                result.loc[ball_id, "id"] = ball_id
                result.loc[ball_id, "game_id"] = index
                result.loc[ball_id, "inning"] = inning + 1
                result.loc[ball_id, "over"] = over_num + 1
                result.loc[ball_id, "ball_num"] = ball_num + 1
                result.loc[ball_id, "batting_team"] = batting_team
                result.loc[ball_id, "bowling_team"] = bowling_team
                for i in dictionary:
                    result.loc[ball_id, i] = dictionary[i]
                
                # break
            # break
        # break

    return result

# %%
result = pd.DataFrame()
for i in range(data.shape[0]):
    index = data.iloc[i]["Id"]
    with open("bbl_json/{}.json".format(index), "r") as file:
        match_data = yaml.safe_load(file)
        file.close()

    result = add_match_data( match_data["innings"], result, index)
    print("Progress {}/{}".format(i, data.shape[0]), end = '\r')
    


# %%
result.to_csv("play_by_play.csv")

# %%



