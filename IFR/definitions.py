"""Define cache directory paths for file imports."""


import os


ROOT_DIR = os.getcwd()

if ROOT_DIR.split("\\")[-1] == "dist":
    ROOT_DIR = ROOT_DIR[:-5]
else:
    ROOT_DIR += "/IFR"

FRINGE_CACHE_PATH = os.path.join(ROOT_DIR, 'cache/fringe_spectrographs')
SIFG_CACHE_PATH = os.path.join(ROOT_DIR, 'cache/SIFG_plot_data')
SSC_CACHE_PATH = os.path.join(ROOT_DIR, 'cache/SSC_plot_data')
