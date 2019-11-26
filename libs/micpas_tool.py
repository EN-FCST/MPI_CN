'''
Functions for grid manipulation and MICPAS file I/O
Yingkai Sha <yingkai@eoas.ubc.ca>
'''
import numpy as np
from sys import exit
from os.path import exists
from scipy.interpolate import griddata
from namelist import lonlim, latlim, resx, resy

def grid_transfer(raw_x, raw_y, raw_data, nav_lon, nav_lat, method='linear'):
    '''
    2D bilinear interpolation
    '''
    LatLonPair=(raw_x.flatten(), raw_y.flatten())
    data_interp = griddata(LatLonPair, raw_data.flatten(), (nav_lon, nav_lat), method=method)
    return data_interp

def genrate_grid(lonlim=lonlim, latlim=latlim, resx=resx, resy=resy):
    '''
    Create lat/lon reference from the namelist
    '''
    gridx, gridy = np.meshgrid(np.arange(lonlim[0], lonlim[1]+resx, resx), \
                               np.arange(latlim[0], latlim[1]+resy, resy))
    return gridx, gridy

def micaps_import(filename, export_data=True):
    '''
    Read MICAPS type IV grided data, export lon, lat.
    If export_data=True, also returns the field and filehead.
    '''
    #print(filename)
    # read raw txt file
    if np.logical_not(exists(filename)):
        return False 
    with open(filename, encoding='windows-1252') as f:
        content = f.readlines()
    content = [x.strip('\n') for x in content]
    content = [x.strip('\r') for x in content] 
    # get header info
    keys = content[1].split()
    #print(keys)
    dlon = np.array(keys[6]).astype(np.float)
    dlat = np.array(keys[7]).astype(np.float)
    lon0 = np.array(keys[8]).astype(np.float)
    lon1 = np.array(keys[9]).astype(np.float)
    lat0 = np.array(keys[10]).astype(np.float)
    lat1 = np.array(keys[11]).astype(np.float)
    # create lat/lon reference
    gridx, gridy = genrate_grid(lonlim=[lon0, lon1], latlim=[lat0, lat1], resx=dlon, resy=dlat)
    if export_data:
        # reshape variables
        num = []
        for line in content[2:]:
            num += line.split()
        var = np.array(num).astype(np.float).reshape(gridx.shape)
        # return
        return gridx, gridy, var, content[:2]
    else:
        return gridx, gridy

def micaps_change_header(shape, header):
    metadata = header
    dinfo = header[1].split()
    dinfo[6] = str(resx)
    dinfo[7] = str(resy)
    dinfo[8] = str(lonlim[0])
    dinfo[9] = str(lonlim[1])
    dinfo[10] = str(latlim[0])
    dinfo[11] = str(latlim[1])
    dinfo[12] = str(shape[1])
    dinfo[13] = str(shape[0])
    dinfo = ' '.join(dinfo)
    header[1] = dinfo
    return header
    

def micaps_export(filename, header, data):
    '''
    Export 2D array as MICPAS type IV file.
    Requires output filename and filehead.
    Filehead can be taken from micaps_import(...)
    '''
    print(' - Exporting '+filename)
    with open(filename, "w") as text_file:
        text_file.write(str(header[0]))
        text_file.write('\r\n')
        text_file.write(str(header[1]))
        text_file.write('\r\n')
        text_file.write('\t'.join(str(i) for i in list(data.flatten())))


