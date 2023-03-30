import numpy as np
import sqlite3 as sl

from datetime import datetime


def get_all_times(minutes, place):
    with sl.connect('dts.db') as con:
        cur = con.cursor()
        request = """
        SELECT time
        FROM dts 
        WHERE time > {} AND depth = 0 AND place == "{}";
        """.format(datetime.now().timestamp() - minutes * 60, place)
        result = list(cur.execute(request))
        if len(result) == 0:
            raise ValueError
        else:
            return np.array(result).T[0]


def nums_to_datetime(array):
    date_array = []
    for i in array:
        date_array.append(datetime.fromtimestamp(i).strftime('%d.%m.20%y %H-%M-%S'))
    return date_array


def get_data(minutes, place):
    with sl.connect('dts.db') as con:
        cur = con.cursor()
        times = np.sort(get_all_times(minutes, place))  # по возрастанию
        depth = []
        temp = []

        for i in times:
            request = """
            SELECT depth, temp
            FROM dts
            WHERE time == {} AND place == "{}";
            """.format(i, place)

            current_data = np.array(list(cur.execute(request))).T
            temp.append(current_data[1])
            if len(current_data[0]) > len(depth):
                depth = current_data[0]

        return nums_to_datetime(times), list(depth), np.array(temp).T


def get_all_places():
    with sl.connect('dts.db') as con:
        cur = con.cursor()
        request = """
        SELECT DISTINCT place
        FROM dts
        """
        result = list(cur.execute(request))
        if len(result) == 0:
            raise ValueError
        else:
            return np.array(result).T[0]


def post_date(data_dict):
    data = []
    if len(data_dict['depth']) > 0:
        for i in range(len(data_dict['depth'])):
            data.append((data_dict['time'], data_dict['depth'][i], data_dict['temp'][i], data_dict['place']))

        request = """
        INSERT INTO dts (time, depth, temp, place)
        VALUES(?, ?, ?, ?);
        """

        with sl.connect('dts.db') as con:
            con.executemany(request, data)
