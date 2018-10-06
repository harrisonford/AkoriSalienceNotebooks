from PIL import Image
import numpy as np
import requests
from io import BytesIO
from scripts.qol import kwarget


# Make a function that loads jsons and image from dataset to make a fixmap
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


# Turn subject data into |t_on|t_off|image|object|
def fixtimes(subject, bucket):
    # TODO: This code repeats a lot internally, it should be refactored into it's own function (get_event)
    # get json data of subject
    request = request_from_bucket(bucket, subject)
    subject_data = request.json()

    # dinamically using header info to know what each row contains, in case database changes in the future
    fixation_header = subject_data['fixation_header']
    image_index = fixation_header.index("image")
    object_index = fixation_header.index("object")
    t_on_index = fixation_header.index("t_on")
    t_off_index = fixation_header.index("t_off")

    # iterate over fixations and store desired data
    fixations = subject_data['fixations']
    fix_data = np.zeros((len(fixations), 4), dtype=int)
    for i_fix, a_fix in enumerate(fixations):
        # transform image name into a number
        # use image name without mosaico and .png later
        im_name = a_fix[image_index]
        image_numbers = [int(s) for s in im_name[7:-4].split() if s.isdigit()]
        object_numbers = [int(s) for s in a_fix[object_index].split() if s.isdigit()]
        if any(image_numbers):
            image = image_numbers[0]
        else:
            image = -1
        if any(object_numbers):
            obj = object_numbers[0]
        else:
            obj = -1
        fix_data[i_fix, :] = [a_fix[t_on_index], a_fix[t_off_index], image, obj]

    return fix_data


# The following functions get stuff from a public google cloud bucket using urllib3
def request_from_bucket(bucketname, filepath, api='http://storage.googleapis.com'):
    g_url = "{api}/{bucket}/{file}".format(api=api, bucket=bucketname, file=filepath)
    return requests.get(g_url)


# make a list of subjects: "pup01.json", "pup02.json", ..., "pup28.json"
bucket = "processed_mosaic_experimental_data"
dataset_dir = ["pup" + str(num + 1).zfill(2) + ".json" for num in range(28)]

# for every image we calculate in a time window how many times subject travels to a mosaic
mosaic_time = 12000  # 12 seconds
window = 2000
images = 84
steps = range(0, mosaic_time, window)

object_rate = np.zeros((len(dataset_dir), len(steps)), dtype=int)
for i_subject, subject in enumerate(dataset_dir):
    subject_fixations = fixtimes(subject, bucket)  # loads |t_on|t_off|image|object|

    subject_object_rate = np.zeros(len(steps))
    # TODO: for now we use t0 == t_on(0) but it's not exact
    for image in range(images):  # we make (t_on-t0, object) array f/e image

        subfix = []
        for a_fix in subject_fixations:
            if a_fix[2] == image:
                subfix.append([a_fix[0], a_fix[3]])
        subfix = np.array(subfix)
        # make first fixation start at t0
        for i in range(len(subfix)):
            subfix[i, 0] = subfix[i, 0] - subfix[0, 0]


# make a list of subjects: "pup01.json", "pup02.json", ..., "pup28.json"
bucket = "processed_mosaic_experimental_data"
dataset_dir = ["pup" + str(num + 1).zfill(2) + ".json" for num in range(28)]

# for every image we calculate in a time window how many times subject travels to a mosaic
mosaic_time = 12000  # 12 seconds
window = 2000
images = 84
steps = range(0, mosaic_time, window)

object_rate = np.zeros((len(dataset_dir), len(steps)), dtype=int)
for i_subject, subject in enumerate(dataset_dir):
    subject_fixations = fixtimes(subject, bucket)  # loads |t_on|t_off|image|object|

    subject_object_rate = np.zeros(len(steps))
    # TODO: for now we use t0 == t_on(0) but it's not exact
    for image in range(images):  # we make (t_on-t0, object) array f/e image

        subfix = []
        for a_fix in subject_fixations:
            if a_fix[2] == image+1:
                subfix.append([a_fix[0], a_fix[3]])
        subfix = np.array(subfix)
        # make first fixation start at 0
        t0 = subfix[0, 0]
        for i in range(len(subfix)):
            subfix[i, 0] = subfix[i, 0] - t0

        # now calculate "transition rate"
        image_object_rate = np.zeros(len(steps))