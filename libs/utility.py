from numpy import copy

def ini_dicts(dictionary, keys):
    for key in keys:
        dictionary[key] = {}
    return dictionary

def subtrack_precip_lev(data):
    data1 = copy(data)
    data1[data1<25]=0.0
    data1[data1>50]=0.0
    data2 = copy(data)
    data2[data2<50]=0.0
    data3 = copy(data)
    data3[data3>25]=0.0
    return data3, data1, data2
