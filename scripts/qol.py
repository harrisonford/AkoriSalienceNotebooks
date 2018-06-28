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
        return heatmap / np.sum(heatmap)
    elif normalize == 'keep':
        return heatmap * max_fix / np.max(heatmap)
    elif normalize == 'norm':
        return heatmap / np.max(heatmap)
    else:
        return heatmap


# taken from https://github.com/alexanderkuk/log-progress
# noinspection PyTypeChecker
def log_progress(sequence, every=None, size=None, name='Items'):
    from ipywidgets import IntProgress, HTML, VBox
    from IPython.display import display

    is_iterator = False
    if size is None:
        try:
            size = len(sequence)
        except TypeError:
            is_iterator = True
    if size is not None:
        if every is None:
            if size <= 200:
                every = 1
            else:
                every = int(size / 200)  # every 0.5%
    else:
        assert every is not None, 'sequence is iterator, set every'

    if is_iterator:
        progress = IntProgress(min=0, max=1, value=1)
        progress.bar_style = 'info'
    else:
        progress = IntProgress(min=0, max=size, value=0)
    label = HTML()
    box = VBox(children=[label, progress])
    display(box)

    index = 0
    try:
        for index, record in enumerate(sequence, 1):
            if index == 1 or index % every == 0:
                if is_iterator:
                    label.value = '{name}: {index} / ?'.format(
                        name=name,
                        index=index
                    )
                else:
                    progress.value = index
                    label.value = u'{name}: {index} / {size}'.format(
                        name=name,
                        index=index,
                        size=size
                    )
            yield record
    except ValueError:  # TODO: except should be bare by PEP8 standards added ValueError for now
        progress.bar_style = 'danger'
        raise
    else:
        progress.bar_style = 'success'
        progress.value = index
        label.value = "{name}: {index}".format(
            name=name,
            index=str(index or '?')
        )
