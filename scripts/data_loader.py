import csv
from PIL import Image
import numpy as np
import scipy.ndimage.filters as ft
import sklearn.preprocessing as sk


# Make a function that loads csv's and image from dataset
def csv_fixmap(subject_list, page, number, **kwargs):

    # Get parameters from kwargs
    if 'ignore' in kwargs:
        ignore = kwargs['ignore']
    else:
        ignore = 0
    if 'norm' in kwargs:
        normalize = kwargs['norm']
    else:
        normalize = False
    if 'db' in kwargs:
        database = kwargs['db']
    else:
        database = 'local'
    if 'map' in kwargs:
        map_type = kwargs['map']
    else:
        map_type = 'time'

    # Get image and dimensions
    image_id = "{page} {num}.jpg".format(page=page, num=number)
    if database == 'local':
        im = Image.open("pages/{page}/{image}".format(page=page, image=image_id))
    else:
        # In the future we can load image from a NoSQL online
        im = None

    im_width, im_height = im.size

    # Start fixmap with zeroes
    total_fixmap = np.zeros([im_height, im_width], dtype=float)

    # Read fix lines: |'fix'| t_on| t_off| x_on| y_on| 'image_id'| 'object_id'| for each subject
    for subject in subject_list:

        fix_counter = 0
        fixmap = np.zeros([im_height, im_width], dtype=float)

        if database == 'local':
            file_path = "{path}/{subject}".format(path='dataset', subject=subject)
        else:
            file_path = None  # in the future can be loaded from NoSQL database

        with open(file_path, 'r', newline='\n') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='\'')
            for row in spamreader:  # save dt in y-x fixmap
                # NOTE: If a subject looks outside the image we include it on the border
                if row[0] == 'fix' and row[5] == image_id:
                    fix_counter += 1
                    if fix_counter > ignore:  # ignore first n-fixations
                        x = min(int(float(row[3])), im_width - 1)  # Border of image if out
                        y = min(int(float(row[4])), im_height - 1)
                        if map_type == 'priority':
                            fixmap[y][x] = 1/(fix_counter - ignore)  # 1, 1/2, 1/3, etc.
                        else:
                            fixmap[y][x] = int(row[2]) - int(row[1])  # dt

        if normalize:
            total_fixmap += sk.normalize(fixmap, 'l2')  # normalize each fixmap to sum=1
        else:
            total_fixmap += fixmap

    if normalize:
        return sk.normalize(total_fixmap, 'l2'), im
    else:
        return total_fixmap, im


# This function returns a heatmap with a gaussian filter on it
def make_heatmap(fixmap, sigma=30):
    # Apply a gaussian filter over fixmap, be sure to pass a float for filtering
    return ft.gaussian_filter(fixmap.astype('float'), sigma=sigma)
