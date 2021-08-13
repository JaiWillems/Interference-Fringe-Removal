"""Define cache directory paths for file imports."""


import os


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

FRINGE_CACHE_PATH = os.path.join(ROOT_DIR, 'cache/fringe_spectrographs')
SIFG_CACHE_PATH = os.path.join(ROOT_DIR, 'cache/SIFG_plot_data')
SSC_CACHE_PATH = os.path.join(ROOT_DIR, 'cache/SSC_plot_data')
