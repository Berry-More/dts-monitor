import psycopg2
import numpy as np
import pandas as pd

from psycopg2 import sql
from datetime import datetime
from psycopg2.extras import DictCursor


dbname = 'holedb'
user = 's_ponasenko'
password = 'Vdycm-8w3uZ'
host = '84.237.52.212'
tab = 'holedb_schema.dts'


# Convert time stamps to date time objects
def nums_to_datetime(array):
    date_array = []
    for i in array:
        date_array.append(datetime.fromtimestamp(i).strftime('%d.%m.20%y %H-%M-%S'))
    return date_array


# Get all times which involved to time interval
def get_all_times(minutes, place):
    with psycopg2.connect(dbname=dbname, user=user, password=password, host=host) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            select = """
            SELECT DISTINCT time
            FROM {0}
            WHERE time > {1} AND place = '{2}';
            """.format(tab, datetime.now().timestamp() - minutes * 60, place)
            cursor.execute(select)
            result = cursor.fetchall()

    if len(result) == 0:
        raise ValueError('Нет данных за данный промежуток времени')  # No data in times
    else:
        return np.array(result).T[0]


# Get last time in our data
def get_last_time(place):
    with psycopg2.connect(dbname=dbname, user=user, password=password, host=host) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            select = """
            SELECT MAX(time)
            FROM {0}
            WHERE place = '{1}';
            """.format(tab, place)
            cursor.execute(select)
            result = cursor.fetchall()[0][0]
    if result is None:
        return 0
    else:
        return result


# Get all existing in DB places
def get_all_places():
    with psycopg2.connect(dbname=dbname, user=user, password=password, host=host) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            select = """
            SELECT DISTINCT place
            FROM {0}
            """.format(tab)
            cursor.execute(select)
            result = cursor.fetchall()

    if len(result) == 0:
        raise ValueError('Нет доступных скважин')  # No data in places
    else:
        return np.array(result).T[0]


# Get full depth interval at the current time interval
def get_full_depth(minutes, place):
    with psycopg2.connect(dbname=dbname, user=user, password=password, host=host) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            select = """
            SELECT DISTINCT depth
            FROM {0}
            WHERE time > {1} AND place = '{2}';
            """.format(tab, datetime.now().timestamp() - minutes * 60, place)
            cursor.execute(select)
            result = cursor.fetchall()

    if len(result) == 0:
        raise ValueError('Нет данных о глубинах для текущих скважины и времени')  # No data in range of depth
    else:
        minimum = float(min(np.array(result).T[0]))
        maximum = get_lengths_array(minutes, place)
        return [minimum, maximum]


# Get max valid depth value
def get_lengths_array(minutes, place):
    with psycopg2.connect(dbname=dbname, user=user, password=password, host=host) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            conn.autocommit = True
            select = """
            SELECT MAX(depth)
            FROM {0}
            WHERE place = '{1}' and time > {2}
            GROUP BY time;
            """.format(tab, place, datetime.now().timestamp() - minutes * 60)

            cursor.execute(select)
            records = cursor.fetchall()

    if len(records) == 0:
        result = None
    else:
        result = min(np.array(records).T[0])
    return result


# Get data
def get_data(minutes, place, depth_min, depth_max):
    with psycopg2.connect(dbname=dbname, user=user, password=password, host=host) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            select = """
            SELECT DISTINCT time, depth, temp
            FROM {0}
            WHERE time > {1} AND place = '{2}' """.format(tab, datetime.now().timestamp() - minutes * 60, place)

            if depth_min == 0.0 and depth_max == 0.0:
                length = get_lengths_array(minutes, place)
                if length is None:
                    length = 0
                select = select + """AND depth >= {0} AND depth <= {1};
                                """.format(depth_min, length)
            else:
                select = select + """AND depth >= {0} AND depth <= {1};
                """.format(depth_min, depth_max)

            cursor.execute(select)
            current_data = np.array(cursor.fetchall())
    
    times = get_all_times(minutes, place)
    raw_data = {'time': current_data.T[0], 'depth': current_data.T[1], 'temp': current_data.T[2]}
    df = pd.DataFrame(raw_data)
    df = df.sort_values(['time', 'depth'])
    current_data = df.to_numpy()

    # bad response
    if len(current_data) == 0:
        raise ValueError('Нет данных')  # No data

    # different len
    if len(current_data) % len(times) != 0:
        raise ValueError('Проблемы с отрисовкой матрицы (дубликаты)')  # Bad matrix length

    out = np.reshape(current_data.T, (3, len(times), int(len(current_data) / len(times))))
    return nums_to_datetime(out[0].T[0]), list(out[1][0]), out[2].T


# Post data to PostgresDB
def post_data(data):
    if len(data['depth']) > 0:
        values = []
        for i in range(len(data['depth'])):
            values.append(
                (data['time'], data['depth'][i],
                 data['temp'][i], data['place'])
            )
        with psycopg2.connect(dbname=dbname, user=user, password=password, host=host) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                insert = sql.SQL("""
                INSERT INTO holedb_schema.dts (time, depth, temp, place)
                VALUES {}
                """).format(sql.SQL(',').join(map(sql.Literal, values)))
                cursor.execute(insert)
