"""User interface file for the Interference-Fringe-Removal program.

This script initializes the `UI` and `Controller` classes to create thhe user
interface and its functionality. It also sets plotting style and parameters.
Functions for setting up and deleting the cache file system are defined.
"""


from controller import Controller
from definitions import FRINGE_CACHE_PATH, ROOT_DIR, SIFG_CACHE_PATH, SSC_CACHE_PATH
from matplotlib import cycler
from PyQt5.QtWidgets import QApplication
from ui import UI
import matplotlib.pyplot as plt
import os
import sys


# Style plot colors.
color_list = ['#EE6666', '#3388BB', '#9988DD', '#EECC55', '#88BB44', '#FFBBBB']
colors = cycler('color', color_list)
plt.style.use('seaborn-dark')
plt.rc('axes', facecolor='#E6E6E6', edgecolor='none', axisbelow=True, prop_cycle=colors)


# Increase plotting chunksize parameter.
# This prevents errors arising from trying to plot too many data points.
plt.rcParams['agg.path.chunksize'] = 10000


def cache_setup(root_dir: str) -> None:
    """Setup the cache file system.

    This function initializes the directories of the program's cache file
    system.

    Parameters
    ----------
    root_dir : str
        String representing the program's root directory.
    """

    os.makedirs(root_dir + "/cache/fringe_spectrographs")
    os.makedirs(root_dir + "/cache/SIFG_plot_data")
    os.makedirs(root_dir + "/cache/SSC_plot_data")


def program_exit() -> None:
    """Exit the UI program.

    This function closes the UI after deleting all program cache files and the
    cache directories.
    """

    app.exec()

    paths = [
        FRINGE_CACHE_PATH + "/",
        SIFG_CACHE_PATH + "/",
        SSC_CACHE_PATH + "/"
    ]

    # Delete each cache file.
    for path in paths:
        files = os.listdir(path)
        for file in files:
            if file[-4:] == ".npy":
                os.remove(path + file)

    # Delete each cahce directory.
    os.rmdir(FRINGE_CACHE_PATH)
    os.rmdir(SIFG_CACHE_PATH)
    os.rmdir(SSC_CACHE_PATH)
    os.rmdir(os.path.join(ROOT_DIR, "cache"))


# Initialize the user interface.
cache_setup(ROOT_DIR)
app = QApplication([])
app.setStyle("Windows")
ui = UI()
Controller(ui=ui)
sys.exit(program_exit())
