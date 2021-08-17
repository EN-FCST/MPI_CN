lib_path = 'libs/'
# =============== Domain settings =============== #
resy      = 0.5        # output latitude grid spacing
resx      = 0.5        # output longitude grid spacing

latlim    = [1, 59]    # the latitude range of the domain
latlim_SE = [26, 32]   # Jiang-nan
latlim_SS = [20, 26]   # Hua-nan

lonlim    = [71, 139]  # the longitude range of the domain
lonlim_SE = [108, 123] # Jiang-nan
lonlim_SS = [105, 120] # Hua-nan

flag_ens  = False      # False: OTS only; True: OTS and ENS

# =========== calibration settings ============ #

flag_SE = True # Heavy precip calibration for Jiang-nan
flag_SS = True # Heavy precip calibration for Hua-nan

prec_keys_SE = ['70'] # heavy precipitation threshold for Jiang-nan
prec_keys_SS = ['77'] # ... Hua-nan

prec_keys = ['25', '50'] # Keys of precipitation ranges, < 25 mm is not weighted.


# forecast lead times of gridded objective analysis
fcst_keys_20Z = ['036', '060', '084', '108', '132', '156', '180', '204', '228' ,'240']
fcst_keys_08Z = ['024', '048', '072', '096', '120', '144', '168', '192', '216', '240']

# forecast lead times of scores (weights)
tssc_keys_20Z = ['024', '048', '072', '096', '120', '144', '168', '192', '216', '240']
tssc_keys_08Z = ['024', '048', '072', '096', '120', '144', '168', '192', '216', '240']

# ================== File path ================== #
TS_perfix = '%y%m%d08' # The perfix of TS
TS_path   = 'U:/' #'data/25/17011808.096'
ENS_path_20Z = 'X:/%Y%m%d12.' #'data/ENS/2018052712.'
ENS_path_08Z = 'X:/%Y%m%d00.' #'data/ENS/2018052700.'
OTS_path_20Z = 'V:/output/FZMOS/%y%m%d20.' #'data/OTS/18052720.'
OTS_path_08Z = 'V:/output/FZMOS/%y%m%d08.' #'data/OTS/18052708.'

# Output filename
tag_name = 'MPI' # the name appears in the micaps file header
output_name_20Z = 'T:/%Y%m%d20_' #'%Y%m%d20_'
output_name_SE_20Z = 'T:/%Y%m%d20_SE_' #'%Y%m%d20_'
output_name_SS_20Z = 'T:/%Y%m%d20_SS_' #'%Y%m%d20_'

output_name_08Z = 'T:/%Y%m%d08_' #'%Y%m%d08_'
output_name_SE_08Z = 'T:/%Y%m%d08_SE_' #'%Y%m%d20_'
output_name_SS_08Z = 'T:/%Y%m%d08_SS_' #'%Y%m%d20_'
