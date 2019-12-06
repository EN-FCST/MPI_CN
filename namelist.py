lib_path = 'libs/'
# =============== Domain settings =============== #
resy      = 0.5        # output latitude grid spacing
resx      = 0.5        # output longitude grid spacing
latlim    = [1, 59]    # the latitude range of the domain
lonlim    = [71, 139]  # the longitude range of the domain
# =========== Ensemble forecast keys ============ #
prec_keys = ['25', '50'] # Keys of precipitation ranges, < 25 mm is not weighted.
 # Keys of objective analysis (i.e., gridded fiels) 
fcst_keys_20Z = ['036', '060', '084', '108', '132', '156', '180', '204', '228' ,'240']
fcst_keys_08Z = ['024', '048', '072', '096', '120', '144', '168', '192', '216', '240']
# Keys of forecast scores (i.e., weights)
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
output_name_08Z = 'T:/%Y%m%d08_' #'%Y%m%d08_'
