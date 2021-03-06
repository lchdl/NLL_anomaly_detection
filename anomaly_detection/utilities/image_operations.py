import numpy as np
import scipy.ndimage
from scipy.stats import cumfreq


def min_max_norm(data):
    return (data-data.min())/(data.max()-data.min()+0.00001) # normalize to [0,1)

def z_score_norm(data, mask):
    # z-score normlization method, 
    # ensure image in mask has zero mean and unit variance
    mask = (mask>0.5).astype('float32')
    data_masked = np.ma.masked_array(data,mask=1-mask)
    masked_mean = data_masked.mean()
    masked_std = data_masked.std()
    return (data - masked_mean)/masked_std

def median_filter(data, kernel_size):
    data = scipy.ndimage.median_filter(data, size=kernel_size, mode='constant', cval=0)
    return data

def mean_filter(data, kernel_size):
    data = scipy.ndimage.uniform_filter(data, size=kernel_size, mode='constant', cval=0)
    return data

def group_std(data_list, normlization='min_max', masks=None):
    assert normlization in ['none', 'min_max', 'z_score'], 'unknown normlization method "%s".' % normlization
    if normlization == 'zscore':
        assert masks is not None, 'must specify image masks when using "%s" normlization method.' % normlization
        assert len(masks) == len(data_list), 'the number of masks and data is not equal.'
    if masks is None:
        masks = [None] * len(data_list)

    dshape_runtime = None
    all_data = []
    for data,mask in zip(data_list,masks):
        if normlization == 'none': pass
        elif normlization == 'min_max':
            data = min_max_norm(data)
        elif normlization == 'z_score':
            data = z_score_norm(data,mask)

        dshape_runtime = data.shape
        data=np.reshape(data,[-1])
        all_data.append(data)
    data_std = np.reshape(np.std(np.vstack(all_data),axis=0),dshape_runtime)
    return data_std

def group_mean(data_list, normlization='min_max', masks=None):
    assert normlization in ['none', 'min_max', 'z_score'], 'unknown normlization method "%s".' % normlization
    if normlization == 'zscore':
        assert masks is not None, 'must specify image masks when using "%s" normlization method.' % normlization
        assert len(masks) == len(data_list), 'the number of masks and data is not equal.'
    if masks is None:
        masks = [None] * len(data_list)

    dshape_runtime = None
    all_data = []
    for data,mask in zip(data_list,masks):
        if normlization == 'none': pass
        elif normlization == 'min_max':
            data = min_max_norm(data)
        elif normlization == 'z_score':
            data = z_score_norm(data,mask)

        dshape_runtime = data.shape
        data=np.reshape(data,[-1])
        all_data.append(data)
    data_std = np.reshape(np.mean(np.vstack(all_data),axis=0),dshape_runtime)
    return data_std

def cutoff(data,percentage):
    assert percentage > 0.0 and percentage < 1.0, 'invalid percentage setting.'
    numbins = 32
    bins = cumfreq(data,numbins=numbins)
    total_voxels = bins.cumcount[-1]
    voxel_lo, voxel_hi, voxel_thresh = 0, 0, total_voxels*percentage
    value_lo, value_hi, value_thresh = bins.lowerlimit, bins.lowerlimit, None
    for bin_id in range(numbins):
        voxel_hi = bins.cumcount[bin_id]
        value_hi += bins.binsize
        if voxel_lo <= voxel_thresh and voxel_thresh <= voxel_hi:
            ratio = (voxel_thresh - voxel_lo) / (voxel_hi - voxel_lo)
            value_thresh = (1-ratio)*value_lo + ratio*value_hi
            return value_thresh
        voxel_lo = voxel_hi
        value_lo = value_hi
    return None
