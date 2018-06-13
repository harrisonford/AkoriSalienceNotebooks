import numpy as np
from PIL import Image


# TODO: This function needs to check both maps are normalized and transformed to 0-255 range correctly
# TODO: This function should resize salmap only if it's not the same size
# TODO: This function should check if values are logical before np.logical is used
# This function finds the normalized scanpath saliency between two different saliency maps as the mean value of the
# normalized saliency map at fixation locations
def nss(salmap, fixmap):

    # First we may need to resize salience map to fixmap size
    # Import fixmap and salmap to PIL.Image
    fixmap_im = Image.fromarray(fixmap)  # This has to be reescaled to 0-255 range
    salmap_im = Image.fromarray(salmap)

    im_width, im_height = fixmap_im.size
    salmap_im_resized = salmap_im.resize((im_width, im_height), Image.BICUBIC)

    # Now transform saliency map back to np.array
    salmap_resized = np.array(salmap_im_resized)

    # Make a logical count between salience map and fixmap
    intermap = np.logical_and(salmap_resized, fixmap)
    return np.sum(intermap)


# Creates a ROC-curve by sweeping through threshold values determined by range of saliency map values at fixation
# locations; true-postive rate is the ratio of saliency map values above threshold at fixation locations...
# TODO: Complete this function
def auc_judd(salmap, fixmap, jitter):
    return salmap, fixmap, jitter, 'coming_soon'
