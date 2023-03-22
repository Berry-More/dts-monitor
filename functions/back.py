import numpy as np
import sqlite3 as sl

from datetime import datetime


def get_all_times(minutes):
    with sl.connect('dts.db') as con:
        cur = con.cursor()
        request = """
        SELECT time
        FROM dts 
        WHERE time > {} AND depth = 0;
        """.format(datetime.now().timestamp() - minutes * 60)
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


def get_data(minutes):
    with sl.connect('dts.db') as con:
        cur = con.cursor()
        times = np.sort(get_all_times(minutes))  # по возрастанию
        depth = []
        temp = []

        for i in times:
            request = """
            SELECT depth, temp
            FROM dts
            WHERE time == {};
            """.format(i)

            current_data = np.array(list(cur.execute(request))).T
            temp.append(current_data[1])
            if len(current_data[0]) > len(depth):
                depth = current_data[0]

        return nums_to_datetime(times), list(depth), np.array(temp).T


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
