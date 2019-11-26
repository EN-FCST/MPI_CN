lib_path = 'libs/'
# =============== Domain settings =============== #
resy      = 0.5        # output latitude grid spacing
resx      = 0.5        # output longitude grid spacing
latlim    = [1, 59]    # the latitude range of the domain
lonlim    = [71, 139]  # the longitude range of the domain
# =========== Ensemble forecast keys ============ #
prec_keys = ['25', '50']                 # Keys of precipitation ranges
fcst_keys_20Z = ['036', '060', '084', '108', '132', '156', '180', '204', '228', '240'] # Keys of objective analysis
fcst_keys_08Z = ['024', '048', '072', '096', '120', '144', '168', '192', '216', '240'] # Keys of objective analysis
tssc_keys_20Z = ['024', '048', '072', '096', '120', '144', '168', '192', '216', '240'] # Keys of forecast scores
tssc_keys_08Z = ['024', '048', '072', '096', '120', '144', '168', '192', '216', '240'] # Keys of forecast scores
# ================== File path ================== #
TS_perfix = '%y%m%d08' # The perfix of TS
TS_path   = 'U:/'
ENS_path_20Z = 'Z:/data/qpf_cal/ensemble/ecmf_24h_optimal_quantile/%Y%m%d12.'
ENS_path_08Z = 'Z:/data/qpf_cal/ensemble/ecmf_24h_optimal_quantile/%Y%m%d00.'
OTS_path_20Z = 'V:/output/FZMOS/%y%m%d20.'
OTS_path_08Z = 'V:/output/FZMOS/%y%m%d08.'
# Output filename
tag_name = 'MPI' # the name appears in the micaps file header
output_name_20Z = 'T:/TEST/%Y%m%d20_'
output_name_08Z = 'T:/TEST/%Y%m%d08_'


