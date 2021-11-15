import pandas as pd
import numpy as np
import pickle

import xlrd
import xlwt

from sklearn.ensemble import IsolationForest
from random import randint, random
import time
        
        
def creat_outliers(d):
    """
    Искусственным образом создает выбросы в данных, заменяя значение одного из признаков случайной записи.
    
    Parameters
    ----------
    d: DataFrame
        Набор записей
    
    Returns
    -------
    outliers: list
        Набор данных, являющихся выбросами
    """
    outliers = []
    
    for j in range(2):
        for i in range(min(len(d.columns)-1, len(d)-1)):
            outlier = list(d.iloc[randint(0, len(d)-1), :]) # выбор случайной записи
            outlier[i] = int(max(list(d.iloc[i]))*(1 + random()))
            outliers.append(outlier)
    return outliers


def isolation_forest(X_train, user, X_outliers):
    """Функция обучает и возвращает обученный классификатор."""
    
    # Создаем target data (1 для нормальной записи, -1 - для выброса)
    y_train = [1 for i in range(X_train.shape[0])] + [-1 for i in range(len(X_outliers))]
    
    # Объединяем вместе train и outliers
    X_train = X_train.append(pd.DataFrame(X_outliers, columns=X_train.columns))
    
    # Обучаем классификатор
    clf = IsolationForest(max_samples=100, contamination = 0.02, random_state=42)
    clf.fit(X_train, y_train)

    return clf


def save_clf(user, clf):
    """Функция сохраняет обученный классификатор в папку models."""
    filename = 'models/' + str(user) + '.pkl'
    with open(filename, 'wb') as model_pkl:
        pickle.dump(clf, model_pkl)
        
        
def train_and_save_clf(user, df):
    """Функция обучает и сохраняет классификатор."""
    df_train = df.loc[df['User'] == user]
    IF = isolation_forest(df_train, user, creat_outliers(df_train))
    save_clf(user, IF)
    print("Classificator for user", user, "is saved")

    
def save_all_classifiers(df):
    """Функция для обучения и сохранения классификаторов для каждого пользователя из набора данных df."""
    users = df['User'].unique()
    for user in users:
        train_and_save_clf(user, df)