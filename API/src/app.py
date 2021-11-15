# Вызываются уже обученные классификаторы
# Вывод на экран: [1] Время выгрузки и работы классификатора: 0.05509495735168457

import flask
from flask import request, jsonify

import pandas as pd
import xlrd
import xlwt
import numpy as np
from sklearn.ensemble import IsolationForest
from random import randint, random
import time
import pickle
import json

# Импортирую свой модуль с векторизацией
import vectorization

# Download and prepare test data
data = pd.read_excel('data.xls')
df = pd.DataFrame(data)

df = df.drop('Unnamed: 0', 1)


#_____________________________________________



app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Detecting Outliers</h1>
<p>Trying to implement a ML model</p>'''


@app.route('/app/data/users/all', methods=['GET'])
# http://127.0.0.1:5000/app/data/users/all
def api_all():
    dic = df.to_dict('records')
    return jsonify(dic)



@app.route('/app/data/users', methods=['GET'])
# http://127.0.0.1:5000/app/data/users?user=1454
def api_user():

    
    if 'user' in request.args:
        user = request.args['user']
        
        return user
    else:
        return "Error: No user field provided. Please specify a user."
    
    
    # данные пока просто для подсчета времени выполнения векторизации
    data_new = ['2021-01-17 20:52:14', 'вход',
        '[4212] Тамара Александровна Акентьева', '95.215.86.111',
        '/?login', '[4212] Тамара Александровна Акентьева', 'nan',
        'SECURITY', 'main',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        's1']
    data_new_vec = vectorization.vectorize(data_new)
    
    # Загружаем модель в память
    start_time = time.time()
    filename = 'models/' + str(user) + '.pkl'
    with open(filename, 'rb') as model_pkl:
        IF = pickle.load(model_pkl)
        
    result = IF.predict(data_new_vec)
    clf_time = str(time.time() - start_time)

    return str(result) + " Время выгрузки и работы классификатора: " + clf_time + " done app " + str(time.time())
    

app.run()