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

def run_single_day(date_ref, day0, key):
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
    date_ref_delay = date_ref-relativedelta(days=1) # use yesterday's forecast
    date_BJ = date_ref_delay+relativedelta(hours=8)
    print('Calculating ['+date_ref.strftime('%Y%m%d')+']')
    name_today = []
    name_today.append(datetime.strftime(date_ref_delay, ENS_path))
    #name_today.append(datetime.strftime(date_ref_delay, FRE_path))
    name_today.append(datetime.strftime(date_ref_delay+relativedelta(hours=8), OTS_path))
    print('Import all micaps files')
    lon, lat = mt.genrate_grid()
    # Initializing dictionaries
    cmpt_keys = ['ENS', 'OTS']
    dict_var = {}; dict_interp = {}; dict_header = {}
    dict_var = ini_dicts(dict_var, cmpt_keys)
    dict_interp = ini_dicts(dict_interp, cmpt_keys)
    # Fill dictionaries with data
    for fcst_key in fcst_keys:
        for i, name in enumerate(name_today):
            temp_name = name+fcst_key
            temp = mt.micaps_import(temp_name)
            if temp == False:
                print(temp_name+' not found. Exit ...')
                return 
            else:
                dict_var[cmpt_keys[i]][fcst_key] = temp[2]
        temp[3][0] = temp[3][0].replace("FZMOS", "MPI")
        dict_header[fcst_key] = temp[3]
    # Get latlon info
    dict_latlon = {}
    for i, name in enumerate(name_today):
        dict_latlon[cmpt_keys[i]] = mt.micaps_import(name+fcst_keys[0], export_data=False)
    lon, lat = mt.genrate_grid()
    print('Bilinear interpolation for grid transfer')
    for key, val in dict_var.items():
        for fcst_key in fcst_keys:
            x = dict_latlon[key][0]
            y = dict_latlon[key][1]
            z = val[fcst_key]
            if x.shape == z.shape:
                dict_interp[key][fcst_key] = mt.grid_transfer(dict_latlon[key][0], dict_latlon[key][1], val[fcst_key], lon, lat)
            else:
                print('\t Error: '+key+' file coord and val does not match, skip ...')
                return
    # Caliberating weights
    print('Caliberating weights')
    W = {}; W = ini_dicts(W, prec_keys)
    for prec_key in prec_keys:
        W[prec_key] = ini_dicts(W[prec_key], tssc_keys)
    # Get weights from moving averaging
    for prec_key in prec_keys:
        for tssc_key in tssc_keys:
            # retreive ts files by the fcst delay
            date_temp = date_ref - relativedelta(days=int(tssc_key)/24)
            data_ma, flag_TS = et.norm_ensemble(date_temp.strftime(TS_perfix), 10, TS_path+prec_key+'/', period=tssc_key)
            if np.logical_not(flag_TS) or np.isnan(data_ma.as_matrix()[-1, 1:].astype(np.float)).sum() >= 3:
                print('\t Warning: TS not exist or filled with NaNs, use average.')
                for cmpt_key in cmpt_keys:
                    W[prec_key][tssc_key][cmpt_key] = 0.5
            else:
                for cmpt_key in cmpt_keys:
                    temp = data_ma[cmpt_key][9:10].as_matrix()
                    if np.isnan(temp):
                        temp = 0.0
                    W[prec_key][tssc_key][cmpt_key] = temp
    # Calculate ensembles
    output = {}
    # get all the result at the current day
    for i in xrange(len(fcst_keys)):
        # initialization
        W0 = 0.0
        W25 = 0.0
        W50 = 0.0
        precip0  = np.zeros(lon.shape)
        precip25 = np.zeros(lon.shape)
        precip50 = np.zeros(lon.shape)
        #
        for cmpt_key in cmpt_keys:
            data0, data25, data50 = subtrack_precip_lev(dict_interp[cmpt_key][fcst_keys[i]])
            precip0 += data0
            precip25 += W['25'][tssc_keys[i]][cmpt_key] * data25
            precip50 += W['50'][tssc_keys[i]][cmpt_key] * data50
            W0 += 1.0
            W25 += W['25'][tssc_keys[i]][cmpt_key]
            W50 += W['50'][tssc_keys[i]][cmpt_key]
        output[fcst_keys[i]] = precip0/W0 + precip25/W25 + precip50/W50
    # Preparing MICAPS file output
    for fcst_key in fcst_keys:
        metadata = mt.micaps_change_header(lon.shape, dict_header[fcst_key])
        mt.micaps_export(datetime.strftime(date_BJ, output_name)+fcst_key+'.txt', metadata, output[fcst_key])
    print('The ensemble system complete')
    return


i = 0
date_ref = datetime(2018, 3, 1, 0)
while i < 61:
    run_single_day(date_ref, 0)
    date_ref = date_ref+relativedelta(days=1)
    #print(date_ref)
    i += 1
