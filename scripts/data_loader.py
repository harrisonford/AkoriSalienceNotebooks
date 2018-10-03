from PIL import Image
import numpy as np
import requests
from io import BytesIO
from scripts.qol import kwarget
from google.cloud import storage
# TODO: resolve google cloud not appearing in requirements with pip freeze


# Make a function that loads jsons and image from dataset
def fixmap(subject_list, page, number, **kwargs):

    # Get parameters from kwargs('key', default_val, **kwargs)
    ignore = kwarget('ignore', 0, **kwargs)
    normalize = kwarget('norm', False, **kwargs)
    grand = kwarget('grand', False, **kwargs)
    map_type = kwarget('map', 'time', **kwargs)
    talkative = kwarget('verbose', False, **kwargs)

    # Get image
    # TODO: Include other methods to get database
    page_name = "{page} {num}.jpg".format(page=page, num=number)
    image_path = "{page}/{name}".format(page=page, name=page_name)
    bucket = "akoriweb_pages"
    if talkative:
        print("Requesting "+page_name+" from bucket "+bucket)
    request = request_from_bucket(bucket, image_path)
    im = Image.open(BytesIO(request.content))  # transform request content to image
    im_width, im_height = im.size

    # Add fixmaps of subjects
    bucket = "akori_dataset_json"
    total_fixmap = np.zeros([im_height, im_width], dtype=float)
    for subject in subject_list:

        subject_fixmap = np.zeros([im_height, im_width], dtype=float)

        # get json file of subject
        if talkative:
            print("Requesting "+subject+" from bucket "+bucket)
        request = request_from_bucket(bucket, subject)
        subject_data = request.json()

        # Take fixations and if inside page add them to map
        fixations = subject_data['fixations']
        # dinamically using header info to know what each row contains, in case database changes in the future
        fixation_header = subject_data['fixation_header']
        image_index = fixation_header.index("image")
        x_index = fixation_header.index("x_on")
        y_index = fixation_header.index("y_on")
        t_on_index = fixation_header.index("t_on")
        t_off_index = fixation_header.index("t_off")

        fix_counter = 0
        for a_fixation in fixations:
            if a_fixation[image_index] == page_name:  # a fixation of desired page
                fix_counter += 1
                if fix_counter > ignore:  # because we're ignoring first n-fixations
                    x = min(int(a_fixation[x_index]), im_width - 1)  # if fixout-border we put on border
                    y = min(int(a_fixation[y_index]), im_height - 1)
                    if map_type == 'priority':
                        subject_fixmap[y][x] += 1/(fix_counter - ignore)  # 1, 1/2, 1/3, etc.
                    else:  # make a fixtime map
                        subject_fixmap[y][x] += a_fixation[t_off_index] - a_fixation[t_on_index]

        if normalize == 'sum' and fix_counter - ignore > 0:
            total_fixmap += subject_fixmap/np.sum(subject_fixmap)
        elif normalize == 'norm' and fix_counter - ignore > 0:
            total_fixmap += subject_fixmap/np.max(subject_fixmap)
        else:
            total_fixmap += subject_fixmap

    if grand == 'avg':
        return total_fixmap/len(subject_list), im
    elif grand == 'sum':
        return total_fixmap/np.sum(total_fixmap), im
    elif grand == 'norm':
        return total_fixmap/np.max(total_fixmap), im
    else:
        return total_fixmap, im


# The following functions get stuff from a public google cloud bucket using urllib3
def request_from_bucket(bucketname, filepath, api='http://storage.googleapis.com'):
    g_url = "{api}/{bucket}/{file}".format(api=api, bucket=bucketname, file=filepath)
    return requests.get(g_url)


# List "blobs" from a bucket, from: https://cloud.google.com/storage/docs/listing-objects#storage-list-objects-python
def list_blobs(bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    return bucket.list_blobs()
