import json

var1 = "this is number 1"
var2 = 2
var3 = ['list', 3]
var4 = {
    'test': "eeee",
    'l': 4,
    'ooga': 5
}

with open('game_save_data.txt', 'w') as saveGame:
    json.dump(var4, saveGame)

with open('game_save_data.txt') as test_file:
    data = json.load(test_file)
    for e in data:
        print(e)