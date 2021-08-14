from numpy import nan
import pandas as pd
from glob import glob
from datetime import datetime
from dateutil.relativedelta import relativedelta

def norm_ensemble(date, num, data_path, lead='96', backward=True):
    '''
    Moving average and normalize TS files.
    -----------------------------------------------------
    The function is operated in the following order:
        1. Identify a range of initialization times
        2. Import TS
        3. TS value cleaning
        4. Moving window averaging and normalization
        
    -----------------------------------------------------
    Input
        date: the currently forecast initialization date
        num: number of neighbourred days considered
        data_path: the file path of ALL the TS files
        lead: forecast lead time as hours and in string fmt.
        backward: "num" days backward; False for forward (historical runs only)
        
    Output
        data_ma: a pandas dataframe that contains all the TS; 
                 it has four columns of 'Date', 'lead', 'OTS', 'ENS', 'FRE'.
        flag: True for success; False for no files found.
    '''
    
    print(' - Checking TS at '+date)
    
    base = datetime.strptime(date, '%y%m%d%H') # <------------- The starting date of files
    
    if backward:
        # <-- how many days backward
        date_list = [base - relativedelta(days=x) for x in range(num)] 
    else:
        # <-- how many days forward (historical re-run only)
        date_list = [base + relativedelta(days=x) for x in range(num)] 
        
    # The output dataframe
    data = pd.DataFrame()
    data = data.reindex(columns=['Date'])
    data['Date'] = date_list[::-1]
    
    # loop over raw files
    # Example filename: 21072108.96 for 2021-07-21 08Z 96H forecast lead time
    # the line below searches multi-day files by matching: data_path/*08.96
    names = glob(data_path+'*'+date[-2:]+'.'+lead)
    
    # Handle no file cases
    if len(names) == 0:
        print('No files found in '+data_path+'. Exit ...')
        return 0, False
    
    # The dataframe that contains all the valid TS
    data_local = pd.DataFrame()
    for filename in names:
        
        # temp_data: the dataframe of a single file/lead time
        # encoding='windows-1252' for windows
        temp_data = pd.read_csv(filename, delim_whitespace=True, encoding='windows-1252')
        
        # Exceping at least five columns for non-empty files
        ## Skip this file is columns miss matched
        if len(temp_data.columns) < 5:
            continue
        
        ## Import TS
        ## File head sequence: Date, Lead, tsRR, tsEc, tsT639, tsNcep, tsJap, tsOts, tsEns, tsFre, etc.
        ## <----- !!! Note: The file head must have the order above
        else:
            # Discard column 2-7 (tsRR-tsJap)
            temp_data = temp_data.drop(temp_data.columns[2:7], axis=1)
            # Discard anything after tsFre
            temp_data = temp_data.drop(temp_data.columns[5:], axis=1)
            
            # Rename the pandas dataframe
            temp_data.columns = ['Date', 'lead', 'OTS', 'ENS', 'FRE']
            
            # Convert str date to datetime format
            temp_data['Date'] = datetime.strptime(temp_data['Date'][0].astype(str), '%Y%m%d%H')
            
            # append the current lead time to the overall dataframe
            data_local = data_local.append(temp_data)
    
    # Replace fill-value with NaN
    data_local = data_local.replace(9999.0, nan)
    
    # Merge data_local (valid TS values) to data (all the needed TS values)
    data = pd.merge(data, data_local, how='left')
    
    # Drop forecast lead time column
    keys = ['OTS', 'ENS', 'FRE']
    data_ma = data.copy()
    data_ma = data_ma.drop('lead', 1)
    
    # Moving average each TS group
    for key in keys:
        # pandas moving window method
        data_ma[key] = data[key].rolling(min_periods=1, window=10, center=False).mean()
        
    # TS normalization
    SUM = data_ma.sum(axis=1)
    for key in keys:
        data_ma[key] = data_ma[key].div(SUM)
    
    # data_ma: TS as a pandas frame, flag of success
    return data_ma, True

def get_weighted_ensemble(cmpt1, W1, cmpt2, W2, cmpt3, W3):
    '''
    Get ensemble results from obj analysis and TS (currently not used)
    '''
    return (cmpt1*W1+cmpt2*W2+cmpt3*W3)/(W1+W2+W3)

