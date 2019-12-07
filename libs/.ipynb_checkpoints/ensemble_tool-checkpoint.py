from numpy import nan
import pandas as pd
from glob import glob
from datetime import datetime
from dateutil.relativedelta import relativedelta

def norm_ensemble(date, num, data_path, period='096', backward=True):
    '''
    Moving average and normalize TS files
    '''
    print(' - Checking TS at '+date)
    base = datetime.strptime(date, '%y%m%d%H') # <------------- The starting date of files
    if backward:
        date_list = [base - relativedelta(days=x) for x in range(num)] # <-- how many days
    else:
        date_list = [base + relativedelta(days=x) for x in range(num)] # <-- how many days
    # create empty dataframe
    data = pd.DataFrame()
    data = data.reindex(columns=['Date'])
    data['Date'] = date_list[::-1]
    # loop over raw files
    names = glob(data_path+'*'+date[-2:]+'.'+period)
    if len(names) == 0:
        print('No files found in '+data_path+'. Exit ...')
        return 0, False
    data_local = pd.DataFrame()
    for filename in names:
        temp_data = pd.read_csv(filename, delim_whitespace=True, encoding='windows-1252')
        if len(temp_data.columns) < 5:
            continue
        else:
            #print(temp_data)
            temp_data = temp_data.drop(temp_data.columns[2:7], axis=1)
            temp_data = temp_data.drop(temp_data.columns[5:], axis=1)
            #print(temp_data)
            temp_data.columns = ['Date', 'period', 'OTS', 'ENS', 'FRE']
            temp_data['Date'] = datetime.strptime(temp_data['Date'][0].astype(str), '%Y%m%d%H')
            data_local = data_local.append(temp_data)
    data_local = data_local.replace(9999.0, nan)
    data = pd.merge(data, data_local, how='left')
    # moving average
    keys = ['OTS', 'ENS', 'FRE']
    data_ma = data.copy()
    data_ma = data_ma.drop('period', 1)
    for key in keys:
        data_ma[key] = data[key].rolling(min_periods=1, window=10, center=False).mean() # pandas moving window method
    # Normalization
    SUM = data_ma.sum(axis=1)
    for key in keys:
        data_ma[key] = data_ma[key].div(SUM)
    return data_ma, True

def get_weighted_ensemble(cmpt1, W1, cmpt2, W2, cmpt3, W3):
    '''
    Get ensemble results from obj analysis and TS (currently not used)
    '''
    return (cmpt1*W1+cmpt2*W2+cmpt3*W3)/(W1+W2+W3)

