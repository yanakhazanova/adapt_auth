import pandas as pd
import numpy as np
import xlrd
import xlwt
import json

import datetime

data = pd.read_excel('data.xls', index_col=0)
df = pd.DataFrame(data)


def vectorize(record):
    """
    Функция для векторизации одной записи о пользователе (стандартный лог системы Битрикс).
    
    Parameters
    ----------
    record: list
        Запись о пользователе
    
    Returns
    -------
    record_vec: DataFrame
        Векторизованная запись о пользователе
    """
    
    ip = ip_vectorization(record[3])
    url = url_vectorization(record[4])
    platform, browser = user_agent_vectorization(record[9])
    date, time = date_time_vectorization(record[0])
    user, admin = user_vectorization(record[5])
    event = event_vectorization(record[1])
    
    record_vec = [[ip, url, platform, browser, date, time, user, admin, event]]
    record_vec = pd.DataFrame(record_vec, columns=list(df.columns))
    
    return record_vec


def saveList(myList, filename):
    """Сохраняет список myList в файл с названием filename."""
    # Файл должен иметь расширение 'npy'
    np.save(filename,myList)

    
def loadList(filename):
    """Считывает содержимое файла с названием filename и возвращает список."""
    # Файл должен иметь расширение 'npy'
    tempNumpyArray=np.load(filename)
    return tempNumpyArray.tolist()


def ip_vectorization(item):
    """
    Функция для векторизации IP.
    
    Parameters
    ----------
    item: string
        IP пользователя
    
    Returns
    -------
    ip: int
        Векторизованное значение IP
    """
    
    lst = str(item).split('.')
    if len(lst) < 4:
            ip = 0
    else:
        # Переводим каждый из октетов в двоичное число, соединяем первые три вместе, 
        # а затем полученное двоичное число переводим обратно в десятичное
        lst = list(map(lambda x: "%08d" % int((bin(int(x)))[2:]), lst))
        item = int(''.join(lst[:3]),2)
        ip = item

    return ip


def url_vectorization(item):
    """
    Функция для векторизации URL.
    
    Parameters
    ----------
    item: string
        URL
    
    Returns
    -------
    url: int
        Векторизованное значение URL
    """
    with open('url_dict.json') as f:
        url_dict = json.load(f)
    
    url_patterns = loadList('url_patterns.npy')

    url = False
    for u in url_patterns:
        # Смотрим, соответствует ли начало данного url одному из найденных ранее шаблонов
        if str(item).startswith(u):
            url = url_dict[u]
            break
        
    if ~url:
        url_dict[item]= max(list(url_dict.values())) + 1
        url_patterns.append(item)
        url = url_dict[item]
        with open('url_dict.json', 'w') as f:
            json.dump(url_dict, f)
        saveList(url_patterns, 'url_patterns.npy')
            
    return url


def user_agent_vectorization(item):
    """
    Функция для векторизации User Agent.
    
    Parameters
    ----------
    item: string
        User Agent
    
    Returns
    -------
    platform: int
        Векторизованное значение операционной системы
    
    browser: int
        Векторизованное значение браузера
    """
    s = str(item)
    
    i_comp = s.find('compatible')
    if i_comp > -1:
        pl = 0
        br = 0
    else:
        
        # Выделяем информацию о платформе
        ob = s.find('(')
        cb = s.find(')',ob)
        sep = s.find(';',ob,cb)
        if sep == -1:
            p = s[(ob+1):cb]
            if p == 'na' or p == '':
                pl = 0
            else:
                pl = p
        else:
            pl = s[(ob+1):sep]
        
        # Выделяем информацию о браузере
        sl = s.rfind('/')
        space = s.rfind(' ')
        b = s[space+1:sl]
        if b == 'na' or b == '' or b == 'an':
            br = 0
        else:
            br = b

    with open('platform_dict.json') as f:
        platform_dict = json.load(f)
        
    with open('browser_dict.json') as f:
        browser_dict = json.load(f)
    
    platform = platform_dict.get(pl, False)
    if ~platform and not platform==0:
        platform_dict[pl]= max(list(platform_dict.values())) + 1
        platform = platform_dict[pl]
        with open('platform_dict.json', 'w') as f:
            json.dump(platform_dict, f)
    
    browser = browser_dict.get(br, False)
    if ~browser and not browser==0:
        browser_dict[br]= max(list(browser_dict.values())) + 1
        browser = browser_dict[br]
        with open('browser_dict.json', 'w') as f:
            json.dump(browser_dict, f)
    
    return platform, browser


def date_time_vectorization(item):
    """
    Функция для векторизации даты и времени.
    
    Parameters
    ----------
    item: string
        Время
    
    Returns
    -------
    date: int
        Векторизованное значение даты (день недели)
    
    time: int
        Векторизованное значение времени (час)
    """
    if item==item:
        
        lst = str(item).replace('.','-').split(' ')
        date_lst = lst[0].split('-')
        date = datetime.date(int(date_lst[0]), int(date_lst[1]), int(date_lst[2])).weekday()
        
        time_lst = lst[1].split(':')
        time = int(time_lst[0])
        
    else:
        dt = datetime.datetime.today()
        date = dt.weekday()
        time = dt.hour
        
    return date, time


def user_vectorization(item):
    """
    Функция для векторизации признака "Пользователь" уникальным номером пользователя.
    
    Parameters
    ----------
    item: string
        Пользователь (номер и имя)
    
    Returns
    -------
    user: int
        Векторизованное значение признака "Пользователь"
    
    admin: int
        1, если пользователь является администратором и 0 в противном случае
    """
    admin_list = loadList('admin_list.npy')
    
    # Выделяем номер пользователя
    id_start = str(item).find('[')
    id_end = str(item).find(']', id_start)
    
    if id_start == -1 or id_end == -1:
        user = 0
        admin = 0
    else:
        name = item[id_end+2:]
        i = item[id_start+1:id_end]
        if not i.isdigit():
            user = 0
        else:
            user = int(i)
        if name in admin_list:
            # Выделяем информацию, явялется ли данный пользователь - администратором
            admin = 1
        else:
            admin = 0
    
    return user, admin


def event_vectorization(item):
    """
    Функция для векторизации события.
    
    Parameters
    ----------
    item: string
        событие
    
    Returns
    -------
    url: int
        Векторизованное значение URL
    """
    with open('event_dict.json') as f:
        event_dict = json.load(f)
    
    event = event_dict.get(item, False)
    if ~event:
        event_dict[item]= max(list(event_dict.values())) + 1
        event = event_dict[item]
        with open('event_dict.json', 'w') as f:
            json.dump(event_dict, f)
    
    return event


