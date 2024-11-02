#!/usr/bin/python
from apps import App

app = App()
mongo = app.mongo

f = open('food_data/calories.csv', 'r', encoding="ISO-8859-1")
var = f.readlines()

for i in range(1, len(var)):
    var[i] = var[i][1:len(var[i]) - 2]

for i in range(1, len(var)):
    temp = var[i].split(",")
    mongo.db.food.insert_one({'food': temp[0], 'calories': temp[1]})
