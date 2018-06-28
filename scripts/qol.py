# Quality of Life (qol) functions
import scipy.ndimage.filters as ft
import numpy as np


# A small function that gets item from kwargs else it sets a default, prevents using too many if-else statements
def kwarget(key, default, **kwargs):
    if key in kwargs:
        return kwargs[key]
    else:
        return default


# This function returns a heatmap with a gaussian filter on it
def make_heatmap(fixmap, sigma=30, **kwargs):
    normalize = kwarget('norm', False, **kwargs)
    if normalize == 'keep':  # we'll keep max peaks values after filtering
        max_fix = np.max(fixmap)
    else:
        max_fix = 0

    # Apply a gaussian filter over fixmap, be sure to pass a float for filtering
    heatmap = ft.gaussian_filter(fixmap.astype('float'), sigma=sigma)

    if normalize == 'sum':
        return heatmap/np.sum(heatmap)
    elif normalize == 'keep':
        return heatmap*max_fix/np.max(heatmap)
    elif normalize == 'norm':
        return heatmap/np.max(heatmap)
    else:
        return heatmap
