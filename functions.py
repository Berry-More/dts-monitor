import os
import lasio
import numpy as np


def load_las(path):
    data = []
    file_names = os.listdir(path)
    if len(file_names) != 0:
        for i in range(len(file_names)):
            file = lasio.read(os.path.join(path, file_names[i]))
            date = file.well['DATE'].value
            data.append((date, file))
        data = np.array(data)
        return data[data[:, 0].argsort()]
    else:
        raise OSError('Files not exists!')


def get_data(las_files):
    depth = list(las_files[0][1][0])
    times = []
    data = []
    for i in range(len(las_files)):
        if len(las_files[i][1][0]) != len(depth):
            raise ValueError('Different len in data')
        else:
            times.append(las_files[i][0])
            data.append(las_files[i][1][1])
    return times, depth, np.array(data).T
