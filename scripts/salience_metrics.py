import numpy.ma as ma


# TODO: This function doesn't check if maps are same size
# This function finds the normalized scanpath saliency between two different saliency maps as the mean value of the
# normalized saliency map at fixation locations
def nss(salmap, fixmap, threshold=0):

    # ASUMES BOTH MAPS ARE SAME SIZE! And also np.arrays
    # Z-score salmap and binarize fixmap
    salmap_scored = (salmap - salmap.mean())/salmap.std()
    fixmap_mask = fixmap <= threshold  # all these values are going to be eliminated

    # Take mean value of fixation locations in fixmap as your score
    intermap = ma.masked_array(salmap_scored, mask=fixmap_mask)
    return intermap.mean()


# Creates a ROC-curve by sweeping through threshold values determined by range of saliency map values at fixation
# locations; true-postive rate is the ratio of saliency map values above threshold at fixation locations...
# TODO: Complete this function
def auc_judd(salmap, fixmap, jitter):
    return salmap, fixmap, jitter, 'coming_soon'
