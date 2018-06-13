import csv
from PIL import Image
import numpy as np
import scipy.ndimage.filters as ft


# Make a function that loads csv and image from dataset
def load_csv_fixmap(subject, page, number, ignore=0):
    # Get image and dimensions
    image_id = "{page} {num}.jpg".format(page=page, num=number)
    im = Image.open("pages/{page}/{image}".format(page=page, image=image_id))
    im_width, im_height = im.size

    # Start fixmap with zeroes
    fixmap = np.zeros([im_height, im_width], dtype=int)

    # Read fix lines: |'fix'| t_on| t_off| x_on| y_on| 'image_id'| 'object_id'|
    file_path = "{path}/{subject}.csv".format(path='dataset', subject=subject)
    with open(file_path, 'r', newline='\n') as csvfile:
        fix_counter = 0
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='\'')
        for row in spamreader:  # save dt in y-x fixmap
            # NOTE: If a subject looks outside the image we include it on the border
            if row[0] == 'fix' and row[5] == image_id:
                fix_counter += 1
                if fix_counter > ignore:  # ignore first n-fixations
                    x = min(int(float(row[3])), im_width - 1)  # Border of image if out
                    y = min(int(float(row[4])), im_height - 1)
                    fixmap[y][x] = int(row[2]) - int(row[1])  # dt

    return fixmap, im


# We load fixation order, note that we use 1/order to show that more is more priority
def load_csv_prioritymap(subject, page, number, ignore=0):
    # Get image dimensions
    im = Image.open("pages/{page}/{page} {number}.jpg".format(page=page, number=number))
    im_width, im_height = im.size

    # Make zeros numpy 2d array of image dimensions
    priority_map = np.zeros([im_height, im_width]).astype('float')

    # Read fix lines: 'fix', t_on, t_off, x_on, y_on, 'image_id', 'object_id'
    file_path = "{path}/{subject}.csv".format(path='dataset', subject=subject)
    with open(file_path, 'r', newline='\n') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='\'')
        fixcounter = 0
        for row in spamreader:  # save dt in y-x map
            # NOTE: If a subject looks outside the image we include it on the border of the image
            if fixcounter >= ignore and row[0] == 'fix' and row[5] == "{page} {num}.jpg".format(page=page, num=number):
                x = min(int(float(row[3])), im_width - 1)
                y = min(int(float(row[4])), im_height - 1)
                priority_map[y][x] = 1 / (fixcounter+1)
            fixcounter += 1
    return priority_map, im


# This function returns a heatmap with a gaussian filter on it
def make_heatmap(fixmap, sigma=30):
    # Apply a gaussian filter over fixmap, be sure to pass a float for filtering
    return ft.gaussian_filter(fixmap.astype('float'), sigma=sigma)
