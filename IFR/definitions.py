"""Define cache directory paths for file imports.

This script defines the paths for each of the folders that make up the cache
file system.
"""


import os


# Get root directory of the current working directory.
# When compiled as an executable, this will be located within the programs
# dynamic memory which will automatically be deleted after the program closes.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Get paths to each cache file directory.
FRINGE_CACHE_PATH = os.path.join(ROOT_DIR, 'cache/fringe_spectrographs')
SIFG_CACHE_PATH = os.path.join(ROOT_DIR, 'cache/SIFG_plot_data')
SSC_CACHE_PATH = os.path.join(ROOT_DIR, 'cache/SSC_plot_data')
