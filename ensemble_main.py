# -*- coding: utf-8 -*-
# import keywords from the namelist
from namelist import lib_path, prec_keys, TS_perfix, TS_path, tag_name, \
                     fcst_keys_08Z, tssc_keys_08Z, ENS_path_08Z, OTS_path_08Z, output_name_08Z, \
                     fcst_keys_20Z, tssc_keys_20Z, ENS_path_20Z, OTS_path_20Z, output_name_20Z
from sys import path, argv
path.insert(0, lib_path)
# local scripts
import ensemble_tool as et
import micpas_tool as mt
from utility import ini_dicts, subtrack_precip_lev
# other modules
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

def dummy_module(delta_day, day0):
    '''
    dummy module for opertional test
    '''
    date_ref = datetime.utcnow()+relativedelta(days=delta_day)
    print('The module is happy running '+date_ref.strftime('%Y%m%d'))
    return date_ref.day

def main(delta_day, day0, key):
    # extracting namelist content
    if key == 20:
        fcst_keys = fcst_keys_20Z
        tssc_keys = tssc_keys_20Z
        ENS_path  = ENS_path_20Z
        OTS_path  = OTS_path_20Z
        output_name = output_name_20Z
    else:
        fcst_keys = fcst_keys_08Z
        tssc_keys = tssc_keys_08Z
        ENS_path  = ENS_path_08Z
        OTS_path  = OTS_path_08Z
        output_name = output_name_08Z
    # UTC time corrections & filename creation
    date_ref = datetime.utcnow()+relativedelta(days=delta_day)
    date_ref_delay = date_ref-relativedelta(days=1) # use yesterday's forecast
    date_BJ = date_ref_delay+relativedelta(hours=8)
    print('Ensemble forecast starts at ['+date_ref.strftime('%Y%m%d-%H:%M%p')+'] UTC')
    name_today = []
    name_today.append(datetime.strftime(date_ref_delay, ENS_path))
    name_today.append(datetime.strftime(date_BJ, OTS_path))
    # =========== import gridded data =========== #
    print('Import all micaps files')
    lon, lat = mt.genrate_grid()
    ## Initializing dictionaries
    cmpt_keys = ['ENS', 'OTS']
    dict_var = {}; dict_interp = {}; dict_header = {}
    dict_var = ini_dicts(dict_var, cmpt_keys)
    dict_interp = ini_dicts(dict_interp, cmpt_keys)
    ## Fill dictionaries with data    
    for fcst_key in fcst_keys:
        for i, name in enumerate(name_today):
            temp_name = name+fcst_key
            temp = mt.micaps_import(temp_name)
            if temp == False:
                print(temp_name+' not found. Exit ...')
                return day0
            else:
                dict_var[cmpt_keys[i]][fcst_key] = temp[2]
        temp[3][0] = temp[3][0].replace("FZMOS", tag_name)
        dict_header[fcst_key] = temp[3]
    # Get latlon info
    dict_latlon = {}
    for i, name in enumerate(name_today):
        dict_latlon[cmpt_keys[i]] = {}
    for i, name in enumerate(name_today):
        for fcst_key in fcst_keys:
            dict_latlon[cmpt_keys[i]][fcst_key] = mt.micaps_import(name+fcst_key, export_data=False)
    lon, lat = mt.genrate_grid()
    print('Bilinear interpolation for grid transfer')
    for key, val in dict_var.items():
        for fcst_key in fcst_keys:
            dict_interp[key][fcst_key] = mt.grid_transfer(dict_latlon[key][fcst_key][0], 
                                                          dict_latlon[key][fcst_key][1], 
                                                          val[fcst_key], lon, lat)
    # =========================================== #
    # ========== Ensemble Caliberation ========== #
    ## calibrating rules:
    ##     0-25 mm - OTS only
    ##     25-50, 50-inf - ENS, OTS weighted average
    ##                     out = [a*ENS + b*OTS]/(a+b)
    print('Caliberating weights')
    # ---------- Extracting weights ---------- #
    # initialization
    # W[precip ranges][fcst horizon][source, e.g., OTS]
    W = {}; W = ini_dicts(W, prec_keys)
    for prec_key in prec_keys:
        W[prec_key] = ini_dicts(W[prec_key], tssc_keys)
    # TS weights + moving average
    for prec_key in prec_keys:
        for tssc_key in tssc_keys:
            # retreive ts files by the fcst delay
            date_temp = date_ref - relativedelta(days=int(tssc_key)/24) # from fcst horizon (i.e., hours) to days
            data_ma, flag_TS = et.norm_ensemble(date_temp.strftime(TS_perfix), 
                                                10, TS_path+prec_key+'/', period=tssc_key) # <---- moving window size: 10
            # saving weights to the dictionary
            # case: no TS files
            if np.logical_not(flag_TS):
                return day0 # <--- exit if no TS files
            # case: TS filled with NaNs (vals = 9999.0)
            elif np.isnan(data_ma.as_matrix()[-1, 1:].astype(np.float)).sum() >= 3:
                print('Warning: TS filled with NaNs, use average.')
                for cmpt_key in cmpt_keys:
                    W[prec_key][tssc_key][cmpt_key] = 0.5
            # case: regular (good quality) weights
            else:
                for cmpt_key in cmpt_keys:
                    temp = data_ma[cmpt_key][9:10].as_matrix()
                    if np.isnan(temp):
                        temp = 0.0
                    W[prec_key][tssc_key][cmpt_key] = temp
    # Calculate ensembles
    print('Preparing output')
    output = {}
    # get all the result at the current day
    print('Total: '+str(len(fcst_keys)))
    for i in range(len(fcst_keys)):
        # initialization (three sets of weights: [0, 25, 50])
        W0 = 0.0
        W25 = 0.0
        W50 = 0.0
        precip0  = np.zeros(lon.shape)
        precip25 = np.zeros(lon.shape)
        precip50 = np.zeros(lon.shape)
        for cmpt_key in cmpt_keys:
            data0, data25, data50 = subtrack_precip_lev(dict_interp[cmpt_key][fcst_keys[i]])
            if cmpt_key = 'OTS':
                precip0 += data0
                W0 += 1.0
            # precip. with multiplicative weights    
            precip25 += W['25'][tssc_keys[i]][cmpt_key] * data25 
            precip50 += W['50'][tssc_keys[i]][cmpt_key] * data50
            W25 += W['25'][tssc_keys[i]][cmpt_key]
            W50 += W['50'][tssc_keys[i]][cmpt_key]
        print('Calculating '+fcst_keys[i])
        output[fcst_keys[i]] = precip0/W0 + precip25/W25 + precip50/W50
        # =========================================== #
    # Preparing MICAPS file output
    for fcst_key in fcst_keys:
        metadata = mt.micaps_change_header(lon.shape, dict_header[fcst_key])
        mt.micaps_export(datetime.strftime(date_BJ, output_name)+fcst_key+'.txt', metadata, output[fcst_key])
    print('The ensemble system complete')
    return date_ref.day

day_out = main(int(argv[1]), int(argv[2]), int(argv[3]))
with open('shaG_history.log', 'w') as fp:
    fp.write(str(day_out).zfill(2)) # exporting the day of completion (and where to restart if fails)

