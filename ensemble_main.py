# -*- coding: utf-8 -*-
# import keywords from the namelist
from namelist import lib_path, prec_keys, flag_SE, flag_SS, prec_keys_SE, prec_keys_SS, TS_perfix, TS_path, tag_name, lonlim, latlim, lonlim_SE, latlim_SE, lonlim_SS, latlim_SS, fcst_keys_08Z, tssc_keys_08Z, ENS_path_08Z, OTS_path_08Z, output_name_08Z, output_name_SE_08Z, output_name_SS_08Z, fcst_keys_20Z, tssc_keys_20Z, ENS_path_20Z, OTS_path_20Z, output_name_20Z, output_name_SE_20Z, output_name_SS_20Z, flag_ens
from sys import path, argv
path.insert(0, lib_path)

# local scripts
import micpas_tool as mt
import ensemble_tool as et
from utility import ini_dicts, subtrack_precip_lev, subtrack_precip_lev_heavy

# other modules
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

# # forecast lead times of gridded objective analysis
# fcst_keys_20Z = ['036', '060', '084', '108', '132', '156', '180', '204', '228' ,'240']
# fcst_keys_08Z = ['024', '048', '072', '096', '120', '144', '168', '192', '216', '240']
# # forecast lead times of scores (weights)
# tssc_keys_20Z = ['024', '048', '072', '096', '120', '144', '168', '192', '216', '240']
# tssc_keys_08Z = ['024', '048', '072', '096', '120', '144', '168', '192', '216', '240']

def dummy_module(delta_day, day0):
    '''
    dummy module for opertional test
    '''
    date_ref = datetime.utcnow()+relativedelta(days=delta_day)
    print('The main routine runs at '+date_ref.strftime('%Y%m%d'))
    return date_ref.day

def main(delta_day, day0, key, flag_ens=flag_ens):
    '''
    The main routine of ensemble precipitation post-porcessing. 
    '''
    
    # extracting namelist content
    if key == 20:
        fcst_keys = fcst_keys_20Z
        tssc_keys = tssc_keys_20Z
        OTS_path  = OTS_path_20Z
        output_name = output_name_20Z
        output_name_SE = output_name_SE_20Z
        output_name_SS = output_name_SS_20Z
        
        if flag_ens:
            ENS_path  = ENS_path_20Z
    else:
        fcst_keys = fcst_keys_08Z
        tssc_keys = tssc_keys_08Z
        OTS_path  = OTS_path_08Z
        output_name = output_name_08Z
        output_name_SE = output_name_SE_08Z
        output_name_SS = output_name_SS_08Z
        
        if flag_ens:
            ENS_path  = ENS_path_08Z
            
    # UTC time corrections & filename creation
    date_ref = datetime.utcnow()+relativedelta(days=delta_day)
    date_ref_delay = date_ref-relativedelta(days=1) # use yesterday's forecast
    date_BJ = date_ref_delay+relativedelta(hours=8)
    
    print('Ensemble forecast starts at ['+date_ref.strftime('%Y%m%d-%H:%M%p')+'] UTC (ENS={})'.format(flag_ens))
    name_today = []
    if flag_ens:
        name_today.append(datetime.strftime(date_ref_delay, ENS_path))
    name_today.append(datetime.strftime(date_BJ, OTS_path))
    
    # =========== import gridded data =========== #
    print('Import all micaps files')
    
    lon, lat = mt.genrate_grid(lonlim=lonlim, latlim=latlim)
    prec_keys = ['25', '50'] # <--- !! testing only
    if flag_SE:
        prec_keys += prec_keys_SE
        flag_heavy = True
        # Jiang-nan subsets
        indx_SE, indy_SE = mt.grid_search(lon, lat, lonlim_SE, latlim_SE)
        lon_SE = lon[indx_SE[0]:indx_SE[1]+1, indy_SE[0]:indy_SE[1]+1]
        lat_SE = lat[indx_SE[0]:indx_SE[1]+1, indy_SE[0]:indy_SE[1]+1]
        grid_shape_SE = lon_SE.shape
        
    if flag_SS:
        prec_keys += prec_keys_SS
        flag_heavy = True
        # Hua-nan subsets
        indx_SS, indy_SS = mt.grid_search(lon, lat, lonlim_SS, latlim_SS)
        lon_SS = lon[indx_SS[0]:indx_SS[1]+1, indy_SS[0]:indy_SS[1]+1]
        lat_SS = lat[indx_SS[0]:indx_SS[1]+1, indy_SS[0]:indy_SS[1]+1]
        grid_shape_SS = lon_SS.shape
    
    ## Initializing dictionaries
    if flag_ens:
        cmpt_keys = ['ENS', 'OTS']
    else:
        cmpt_keys = ['OTS']
        
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
            
    #lon, lat = mt.genrate_grid(lonlim=lonlim, latlim=latlim)
    
    print('Bilinear interpolation for grid transfer')
    for key, val in dict_var.items():
        for fcst_key in fcst_keys:
            dict_interp[key][fcst_key] = mt.grid_transfer(dict_latlon[key][fcst_key][0], 
                                                          dict_latlon[key][fcst_key][1], 
                                                          val[fcst_key], lon, lat)
    # =========================================== #
    # ========== Ensemble Caliberation ========== #
    ## Setup:
    ##     0-25 mm - OTS only
    ##     25-50, 50-inf - ENS, OTS weighted average
    ##                     out = [a*ENS + b*OTS]/(a+b)
    ##     current and historical (last year) weights are equal.
    # ---------------------------------------- #
    
    # ---------- Extracting weights ---------- #
    # initialization
    # W[precip ranges][fcst horizon][source, e.g., OTS]
    
    print('Estimating calibration weights')
    
    W = {}; W = ini_dicts(W, prec_keys)
    
    for prec_key in prec_keys:
        W[prec_key] = ini_dicts(W[prec_key], tssc_keys)
        
    # TS weights + moving average
    for prec_key in prec_keys:
        for tssc_key in tssc_keys:
            
            # retreive ts files by the fcst delay
            date_temp = date_ref - relativedelta(days=int(tssc_key)/24) # from fcst horizon (i.e., hours) to days
            
            # reading TS from selected files + TS moving average
            ## The moving averaging considers 10 days backward 
            data_ma, flag_TS = et.norm_ensemble(date_temp.strftime(TS_perfix), 10, TS_path+prec_key+'/', lead=tssc_key)
            
            # saving weights to the dictionary
            # case: no TS files (flag_TS=False)
            if np.logical_not(flag_TS):
                return day0 # <--- exit if no TS files
            
            # case: TS filled with NaNs (vals = 9999.0)
            ## Use TS=0.5
            elif np.isnan(data_ma.values[-1, 1:].astype(np.float)).sum() >= 3:
                print('Warning: TS filled with NaNs, use average.')
                for cmpt_key in cmpt_keys:
                    W[prec_key][tssc_key][cmpt_key] = 0.5
                flag_heavy = False
                    
            # case: regular (good quality) weights
            else:
                for cmpt_key in cmpt_keys:
                    temp = data_ma[cmpt_key][9:10].values
                    if np.isnan(temp):
                        temp = 0.0
                    W[prec_key][tssc_key][cmpt_key] = temp
                    
    # ---------- Extracting historical weights ---------- #
    # Obtaining TS from last year the same initialization date
    
    print('Caliberating historical weights')
    W_h = {}; W_h = ini_dicts(W_h, prec_keys)
    
    for prec_key in prec_keys:
        W_h[prec_key] = ini_dicts(W_h[prec_key], tssc_keys)
        
    # TS weights + moving average
    for prec_key in prec_keys:
        for tssc_key in tssc_keys:
            
            # the case of last year
            hist_ref = date_ref - relativedelta(years=1)
            date_temp = hist_ref + relativedelta(days=int(tssc_key)/24)
            
            # backward=False for historical TS
            data_ma, flag_TS = et.norm_ensemble(date_temp.strftime(TS_perfix), 10, TS_path+prec_key+'/', lead=tssc_key, backward=False)
            
            # saving weights to the dictionary
            # case: no TS files (skip)
            if (np.logical_not(flag_TS)) or (np.isnan(data_ma.values[-1, 1:].astype(np.float)).sum() >= 3):
                print('Warning: historical TS no found/filled with NaNs. Now ignoring')
                
                for cmpt_key in cmpt_keys:
                    W_h[prec_key][tssc_key][cmpt_key] = W[prec_key][tssc_key][cmpt_key]
                    
            # case: regular (good quality) weights
            else:
                for cmpt_key in cmpt_keys:
                    temp = data_ma[cmpt_key][9:10].values
                    if np.isnan(temp):
                        temp = 0.0
                    W_h[prec_key][tssc_key][cmpt_key] = temp
                    
    # Calculate ensembles
    print('Preparing output')
    output = {}
    output_SE = {}
    output_SS = {}
    
    # get all the result at the current day
    print('Total: '+str(len(fcst_keys)))
    
    for i in range(len(fcst_keys)):
        
        # --------------------------------------------------- #
        # 0, 25, 50 mm cases
        # initialization (three sets of weights: [0, 25, 50])
        W0 = 0.0; W25 = 0.0; W50 = 0.0
        precip0  = np.zeros(lon.shape)
        precip25 = np.zeros(lon.shape)
        precip50 = np.zeros(lon.shape)
        
        for cmpt_key in cmpt_keys:
                        
            data0, data25, data50 = subtrack_precip_lev(dict_interp[cmpt_key][fcst_keys[i]])
            
            if cmpt_key == 'OTS':
                precip0 += data0
                W0 += 1.0
                
            # precip. with multiplicative weights    
            precip25 += W['25'][tssc_keys[i]][cmpt_key] * data25 # + W_h['25'][tssc_keys[i]][cmpt_key] * data25 
            precip50 += W['50'][tssc_keys[i]][cmpt_key] * data50 # + W_h['50'][tssc_keys[i]][cmpt_key] * data50
            W25 += W['25'][tssc_keys[i]][cmpt_key] # + W_h['25'][tssc_keys[i]][cmpt_key]
            W50 += W['50'][tssc_keys[i]][cmpt_key] # + W_h['50'][tssc_keys[i]][cmpt_key]
            
        print('Calculating '+fcst_keys[i])
        output[fcst_keys[i]] = precip0/W0 + precip25/W25 + precip50/W50
        
        if flag_SE:
            
            W0 = 0.0; W25 = 0.0; W50 = 0.0; W_heavy = 0.0
            precip0_SE  = np.zeros(grid_shape_SE)
            precip25_SE = np.zeros(grid_shape_SE)
            precip50_SE = np.zeros(grid_shape_SE)
            precip_heavy_SE = np.zeros(grid_shape_SE)
            
            for cmpt_key in cmpt_keys:
                
                temp_SE = dict_interp[cmpt_key][fcst_keys[i]][indx_SE[0]:indx_SE[1]+1, indy_SE[0]:indy_SE[1]+1]
                data0, data25, data50, data_heavy = subtrack_precip_lev_heavy(temp_SE, np.float(prec_keys_SE[0]))
                
                if cmpt_key == 'OTS':
                    precip0 += data0
                    W0 += 1.0
                    
                # precip. with multiplicative weights    
                precip25_SE += W['25'][tssc_keys[i]][cmpt_key] * data25
                precip50_SE += W['50'][tssc_keys[i]][cmpt_key] * data50
                precip_heavy_SE += W[prec_keys_SE[0]][tssc_keys[i]][cmpt_key] * data_heavy
                
                W25 += W['25'][tssc_keys[i]][cmpt_key]
                W50 += W['50'][tssc_keys[i]][cmpt_key]
                W_heavy += W[prec_keys_SE[0]][tssc_keys[i]][cmpt_key]
                
        print('Calculating {} Jiang-nan'.format(fcst_keys[i]))
        output_SE[fcst_keys[i]] = precip0/W0 + precip25/W25 + precip50/W50 + precip_heavy_SE/W_heavy

        if flag_SS:
            
            W0 = 0.0; W25 = 0.0; W50 = 0.0; W_heavy = 0.0
            precip0_SS  = np.zeros(grid_shape_SS)
            precip25_SS = np.zeros(grid_shape_SS)
            precip50_SS = np.zeros(grid_shape_SS)
            precip_heavy_SS = np.zeros(grid_shape_SS)
            
            for cmpt_key in cmpt_keys:
                
                temp_SS = dict_interp[cmpt_key][fcst_keys[i]][indx_SS[0]:indx_SS[1]+1, indy_SS[0]:indy_SS[1]+1]
                data0, data25, data50, data_heavy = subtrack_precip_lev_heavy(temp_SS, np.float(prec_keys_SS[0]))
                
                if cmpt_key == 'OTS':
                    precip0 += data0
                    W0 += 1.0
                    
                # precip. with multiplicative weights    
                precip25_SS += W['25'][tssc_keys[i]][cmpt_key] * data25
                precip50_SS += W['50'][tssc_keys[i]][cmpt_key] * data50
                precip_heavy_SS += W[prec_keys_SS[0]][tssc_keys[i]][cmpt_key] * data_heavy
                
                W25 += W['25'][tssc_keys[i]][cmpt_key]
                W50 += W['50'][tssc_keys[i]][cmpt_key]
                W_heavy += W[prec_keys_SS[0]][tssc_keys[i]][cmpt_key]
                
        print('Calculating {} Hua-nan'.format(fcst_keys[i]))
        output_SS[fcst_keys[i]] = precip0/W0 + precip25/W25 + precip50/W50 + precip_heavy_SS/W_heavy
        # =========================================== #
        
    # Preparing MICAPS file output
    for fcst_key in fcst_keys:
        metadata = mt.micaps_change_header(lon.shape, dict_header[fcst_key])
        mt.micaps_export(datetime.strftime(date_BJ, output_name)+fcst_key+'.txt', metadata, output[fcst_key])
        
        if flag_SE:
            metadata_SE = mt.micaps_change_header(lon_SE.shape, dict_header[fcst_key])
            mt.micaps_export(datetime.strftime(date_BJ, output_name_SE)+fcst_key+'.txt', metadata_SE, output_SE[fcst_key])
            
        if flag_SS:
            metadata_SS = mt.micaps_change_header(lon_SS.shape, dict_header[fcst_key])
            mt.micaps_export(datetime.strftime(date_BJ, output_name_SS)+fcst_key+'.txt', metadata_SS, output_SS[fcst_key])
                             
    print('Ensemble post-processing complete')
    
    return date_ref.day

day_out = main(int(argv[1]), int(argv[2]), int(argv[3]))
with open('shaG_history.log', 'w') as fp:
    fp.write(str(day_out).zfill(2)) # exporting the day of completion (and where to restart if fails)

