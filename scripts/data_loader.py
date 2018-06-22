import csv
from PIL import Image
import numpy as np
import scipy.ndimage.filters as ft
import sklearn.preprocessing as sk
import urllib3


# Make a function that loads csv's and image from dataset
def csv_fixmap(subject_list, page, number, **kwargs):

    # Get parameters from kwargs('key', default_val, **kwargs)
    ignore = kwarget('ignore', 0, **kwargs)
    normalize = kwarget('norm', False, **kwargs)
    database = kwarget('db', 'local', **kwargs)
    map_type = kwarget('map', 'time', **kwargs)

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
        elif database == 'Drive':
            file_path = None  # in the future can be loaded from Drive database
        else:
            raise ValueError("Wrong parameter chosen as database="+database)

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


# This is how age-gender histogram was made
def age_gender(database='gcloud'):
    # Start by loading subjectInfo.csv
    if database == 'gcloud':
        # load using public api link from my google cloud
        api = 'http://storage.googleapis.com'
        bucket = 'akoriweb_misc'
        file = 'subjectInfo.csv'
        google_url = "{api}/{bucket}/{file}".format(api=api, bucket=bucket, file=file)

        # create a pool manager
        http = urllib3.PoolManager()
        # use it to request a file
        request = http.request('GET', google_url)
        data = request.data.decode('utf-8')

        # data is actually a stream of bytes, we'll append gender and age from this stream
        ismale = []
        age = []

        # scan by finding \n in chunks
        chunk = 10
        last_line = data.find('\n', 0, chunk)
        while last_line != -1:
            whitespace = data.find('\t', last_line+1, last_line+chunk)  # find middle whitespace
            if whitespace == -1:
                break
            age.append(int(data[last_line+1:whitespace]))
            last_line = data.find('\n', last_line+1, last_line+chunk)  # update last-line read
            ismale.append(int(data[whitespace+1:last_line]))

    else:
        # for now database exists only in google cloud (good enough)
        raise ValueError("Wrong parameter chosen as database="+database)

    return age, ismale


# A small function that gets item from kwargs else it sets a default, prevents using too many if-else statements
def kwarget(key, default, **kwargs):
    if key in kwargs:
        return kwargs[key]
    else:
        return default


# This function returns a heatmap with a gaussian filter on it
def make_heatmap(fixmap, sigma=30):
    # Apply a gaussian filter over fixmap, be sure to pass a float for filtering
    return ft.gaussian_filter(fixmap.astype('float'), sigma=sigma)
