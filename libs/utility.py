from numpy import copy

def ini_dicts(dictionary, keys):
    # expanding dictionary with given keys
    ## keys should support python looping, i.e., list
    for key in keys:
        dictionary[key] = {}
    return dictionary

def subtrack_precip_lev(data):
    # discretizing precipitation by thresholds:
    ##    [0, 25)
    ##    [25, 50)
    ##    [50, 60)
    ##    [60, 75)
    
    data1 = copy(data)
    data1[data1>=25] = 0.0

    data2 = copy(data)
    data2[data2<25] = 0.0
    data2[data2>=50] = 0.0
    
    data3 = copy(data)
    data3[data3<50] = 0.0
    data3[data3>=60] = 0.0
    
    data4 = copy(data)
    data4[data4<60] = 0.0
    data4[data3>=75] = 0.0  
    
    data5 = copy(data)
    data5[data5<75] = 0.0
    
    return data1, data2, data3, data4, data5

def subtrack_precip_lev_heavy(data, heavy_thres):
    # discretizing precipitation by thresholds:

    data1 = copy(data)
    data1[data1<25] = 0.0
    data1[data1>=50] = 0.0
    
    data2 = copy(data)
    data2[data2<50] = 0.0
    data2[data1>=heavy_thres] = 0.0
    
    data3 = copy(data)
    data3[data3>=25] = 0.0
    
    data4 = copy(data)
    data4[data4<heavy_thres]=0.0
    
    return data3, data1, data2, data4
