

from functools import partial
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QDesktopWidget, QFileDialog, QGridLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QRadioButton, QScrollArea,
    QVBoxLayout, QWidget
)
from spectra.dataobjects import OPUSLoader
from spectra.operations import DataOperations
from typing import Literal, Tuple
import matplotlib.pyplot as plt
import numpy as np
import os
import sys


class UI(QMainWindow):
    
    def __init__(self) -> None:
        """Initialize main UI window."""

        super().__init__()

        self.fringe_paths = {}

        self.setWindowTitle("Interference-Fringe-Removal")
        self.setFixedWidth(1500)
        self.setFixedHeight(750)
        
        self.layout = QGridLayout()
        self.layout.addWidget(self._SIFG_display(), 1, 1, 1, 1)
        self.layout.addWidget(self._SSC_display(), 1, 2, 1, 1)
        self.layout.addWidget(self._base_display(), 2, 1, 1, 3)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.layout)

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.show()

    def _SIFG_display(self) -> QWidget:
        """Return the SIFG display widget.

        Returns
        -------
        QWidget
            Widget containing the SIFG `matplotlib` canvas.
        """

        self.SIFG_figure = plt.figure()
        self.SIFG_canvas = FigureCanvas(self.SIFG_figure)
        self.SIFG_toolbar = NavigationToolbar(self.SIFG_canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.SIFG_toolbar)
        layout.addWidget(self.SIFG_canvas)

        self.SIFG_window = QWidget()
        self.SIFG_window.setLayout(layout)

        self.SIFG_plot = self.SIFG_figure.add_subplot(111)
        self.SIFG_plot.set_title("Interferogram")
        self.SIFG_plot.grid()
        self.SIFG_canvas.draw()

        return self.SIFG_window

    def _SSC_display(self) -> QWidget:
        """Return the SSC display widget.

        Returns
        -------
        QWidget
            Widget containing the SSC `matplotlib` canvas.
        """

        self.SSC_figure = plt.figure()
        self.SSC_canvas = FigureCanvas(self.SSC_figure)
        self.SSC_toolbar = NavigationToolbar(self.SSC_canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.SSC_toolbar)
        layout.addWidget(self.SSC_canvas)

        self.SSC_window = QWidget()
        self.SSC_window.setLayout(layout)

        self.SSC_plot = self.SSC_figure.add_subplot(111)
        self.SSC_plot.set_title("Spectrograph")
        self.SSC_plot.grid()
        self.SSC_canvas.draw()

        return self.SSC_window
    
    def _base_display(self) -> QWidget:
        """Return the base controls widget.

        Returns
        -------
        QWidget
            Widget containing the main data handling controls.
        """
        # Widget initialization.
        self.background_upload = QPushButton("Background File Upload")
        self.sample_upload = QPushButton("Sample File upload")
        self.save_data = QPushButton("Save Filtered Data")
        self.fringe_start = QLineEdit()
        self.fringe_end = QLineEdit()
        self.select_fringe = QPushButton("Select")
        self.mode_S = QRadioButton("Single Beam")
        self.mode_A = QRadioButton("Absorbance")
        self.mode_T = QRadioButton("Transmittance")
        self.update_plot = QPushButton("Update Plot")

        # Widgit styling.
        self.background_upload.setStyleSheet("background-color: lightgrey")
        self.sample_upload.setStyleSheet("background-color: lightgrey")
        self.save_data.setStyleSheet("background-color: lightgrey")
        self.select_fringe.setStyleSheet("background-color: lightgrey")
        self.update_plot.setStyleSheet("background-color: lightgrey")

        # Button grouping.
        self.mode_button_group = QButtonGroup(self.mode_S)
        self.mode_button_group.addButton(self.mode_S)
        self.mode_button_group.addButton(self.mode_A)
        self.mode_button_group.addButton(self.mode_T)
        self.mode_S.setChecked(True)
    
        # Widget organization.
        layout = QGridLayout()
        layout.addWidget(QLabel("<b>Data Uploading</b>"), 1, 1, 1, 1)
        layout.addWidget(self.background_upload, 2, 1, 1, 1)
        layout.addWidget(self.sample_upload, 3, 1, 1, 1)
        layout.addWidget(self.save_data, 4, 1, 1, 1)
        layout.addWidget(QLabel("<b>Fringe Localization</b>"), 1, 2, 1, 2)
        layout.addWidget(QLabel("Start:"), 2, 2, 1, 1)
        layout.addWidget(self.fringe_start, 2, 3, 1, 1)
        layout.addWidget(QLabel("End:"), 3, 2, 1, 1)
        layout.addWidget(self.fringe_end, 3, 3, 1, 1)
        layout.addWidget(self.select_fringe, 4, 2, 1, 2)
        layout.addWidget(QLabel("<b>Fringe Select</b>"), 1, 4, 1, 1)
        layout.addWidget(self._scrollable_area(), 2, 4, 3, 1)
        layout.addWidget(QLabel("<b>Data Mode</b>"), 1, 5, 1, 1)
        layout.addWidget(self.mode_S, 2, 5, 1, 1)
        layout.addWidget(self.mode_A, 3, 5, 1, 1)
        layout.addWidget(self.mode_T, 4, 5, 1, 1)
        layout.addWidget(QLabel("<b>Update Data</b>"), 1, 6, 1, 1)
        layout.addWidget(self.update_plot, 2, 6, 1, 1)

        baseWindow = QWidget()
        baseWindow.setLayout(layout)

        return baseWindow
    
    def _scrollable_area(self) -> QScrollArea:
        """Return a scrollable "Fringe Select" window.

        Returns
        -------
        QScrollArea
            Scrollable "Fringe Select" window.
        """

        self.scroll_window = QScrollArea()
        self.scroll_widget = QWidget()

        layout = QVBoxLayout()
        for key in self.fringe_paths.keys():
            layout.addWidget(QCheckBox(key))
        self.scroll_widget.setLayout(layout)

        self.scroll_window.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_window.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_window.setWidget(self.scroll_widget)

        return self.scroll_window


class Controller(object):

    def __init__(self, ui):
        """Initialize `Controller` class."""

        self.ui = ui
        self.fringes = {}
        
        self._connect_signals()
    
    def _connect_signals(self) -> None:
        """Add widget functionality."""
        
        self.ui.background_upload.clicked.connect(partial(self.upload_data, False))
        self.ui.sample_upload.clicked.connect(partial(self.upload_data, True))
        self.ui.select_fringe.clicked.connect(self.fringe_localization)
        self.ui.mode_S.clicked.connect(partial(self.mode_change, "S"))
        self.ui.mode_A.clicked.connect(partial(self.mode_change, "A"))
        self.ui.mode_T.clicked.connect(partial(self.mode_change, "T"))
        self.ui.update_plot.clicked.connect(self.update_plot)

    def SIFG_plot(self, *args: Tuple) -> None:
        """Plot interferogram data.

        Parameters
        ----------
        args : tuple
            Tuple of length three with format `(x, y, label)` where `x` is the
            x data, `y` is the y-data, and `label` is the plot label.
        """

        self.ui.SIFG_plot.clear()
        self.ui.SIFG_plot.set_title("Interferogram")

        files = os.listdir(os.getcwd() + "/IFR/cache/SIFG_plot_data")
        for file in files:
            path, label = os.getcwd() + "/IFR/cache/SIFG_plot_data/", file[:-4]
            x, y = self._cache_file_load(path, label)
            self.ui.SIFG_plot.plot(x, y, label=label)

        for tup in args:
            x, y, label = tup[0], tup[1], tup[2]
            path = os.getcwd() + "/IFR/cache/SIFG_plot_data/"
            self._cache_file_save(path, label, x, y)

            self.ui.SIFG_plot.plot(x, y, label=label)

        self.ui.SIFG_plot.legend()
        self.ui.SIFG_plot.grid()
        self.ui.SIFG_canvas.draw()
    
    def SSC_plot(self, *args):
        """Plot spectrograph data.

        Parameters
        ----------
        args : tuple
            Tuple of length three with format `(x, y, label)` where `x` is the
            x data, `y` is the y-data, and `label` is the plot label.
        """

        self.ui.SSC_plot.clear()
        self.ui.SSC_plot.set_title("Spectrograph")

        files = os.listdir(os.getcwd() + "/IFR/cache/SSC_plot_data")
        for file in files:
            path, label = os.getcwd() + "/IFR/cache/SSC_plot_data/", file[:-4]
            x, y = self._cache_file_load(path, label)
            self.ui.SSC_plot.plot(x, y, label=label)

        for tup in args:
            x, y, label = tup[0], tup[1], tup[2]
            path = os.getcwd() + "/IFR/cache/SSC_plot_data/"
            self._cache_file_save(path, label, x, y)

            self.ui.SSC_plot.plot(x, y, label=label)

        self.ui.SSC_plot.legend()
        self.ui.SSC_plot.grid()
        self.ui.SSC_canvas.draw()
    
    def upload_data(self, sample: bool) -> None:
        """Upload OPUS data.

        Parameters
        ----------
        sample : bool
            If `sample=True`, the selected file upload will initialize the
            sample data, else it will initialize the background data.
        """

        path, _ = QFileDialog.getOpenFileName(caption="Open File", filter="OPUS files (*.0)")
        
        if sample:
            self.sample_data = OPUSLoader(path)

            x = self.sample_data.data["SIFG"].x[::10]
            y = self.sample_data.data["SIFG"].y[::10]
            label = "Sample SIFG"
            self.SIFG_plot((x, y, label))

            x = self.sample_data.data["SSC"].x[::10]
            y = self.sample_data.data["SSC"].y[::10]
            label = "Sample SSC"
            self.SSC_plot((x, y, label))

        else:
            self.background_data = OPUSLoader(path)

            x = self.background_data.data["SIFG"].x
            y = self.background_data.data["SIFG"].y
            label = "Background SIFG"
            self.SIFG_plot((x, y, label))

            x = self.background_data.data["SSC"].x
            y = self.background_data.data["SSC"].y
            label = "Background SSC"
            self.SSC_plot((x, y, label))

    def fringe_localization(self) -> None:
        """Calculate fringe spectrograph component.

        This method uses the user defined fringe bounds to localize the fringe
        and calculate the spectrograph component due to the fringe.
        Additionally it will save the resulting fringe spectrograph components
        to `.npy` binary files.
        """

        start = int(self.ui.fringe_start.text())
        end = int(self.ui.fringe_end.text())

        background_data = self.background_data.data["SIFG"]
        background_label = "fringe_" + str(np.max(background_data.y[np.where((start < background_data.x) & (background_data.x < end))])) + "b"

        fringe_spectrograph = DataOperations().fringe_spectrograph(background_data, start, end)
        background_x, background_y = fringe_spectrograph.x, fringe_spectrograph.y

        sample_data = self.sample_data.data["SIFG"]
        sample_label = "fringe_" + str(np.max(sample_data.y[np.where((start < sample_data.x) & (sample_data.x < end))])) + "s"

        fringe_spectrograph = DataOperations().fringe_spectrograph(sample_data, start, end)
        sample_x, sample_y = fringe_spectrograph.x, fringe_spectrograph.y

        path = os.getcwd() + "/IFR/cache/fringe_spectrographs/"
        self._cache_file_save(path, background_label, background_x, background_y)
        self._cache_file_save(path, sample_label, sample_x, sample_y)

        self._update_fringe_list(background_label)
        self._update_fringe_list(sample_label)

        self.fringes[background_label] = start, end
        self.fringes[sample_label] = start, end
    
    def _cache_file_save(self, path: str, label: str, x: np.array, y: np.array) -> None:
        """Save file to cache system as a `.npy` format.

        Parameters
        ----------
        path : str
            Path to the cache file of interest. The path must end with a
            forward slash.
        label : str
            Label identifier used for file naming.
        x, y : np.array
            Arrays of shape (n,) containing data to be saved.
        """
    
        file_name = path + label
        x, y = x.reshape((-1, 1)), y.reshape((-1, 1))
        data = np.concatenate((x, y), axis=1)
        np.save(file_name, data)
    
    def _cache_file_load(self, path: str, label: str) -> Tuple:
        """Load file from cache system.

        Parameters
        ----------
        path : str
            Path to the cache file of interest. The path must end with a
            forward slash.
        label : str
            Label identifier used for file naming.
        
        Returns
        -------
        x, y : np.array
            Arrays of shape (n,) containing data to be saved.
        """
    
        file_name = path + label + ".npy"
        data = np.load(file_name)
        x, y = data[:, 0], data[:, 1]

        return x, y

    def _update_fringe_list(self, label):
        pass

    def mode_change(self, type: Literal["S", "A", "T"]) -> None:
        print("Changing Mode")

    def update_plot(self):
        print("Updating Plot")


def program_exit():
    """Exit the UI program.

    This function closes the UI after deleting all program cache files.
    """

    app.exec()

    cwd = os.getcwd()

    paths = [
        cwd + "/IFR/cache/SIFG_plot_data/",
        cwd + "/IFR/cache/SSC_plot_data/",
        cwd + "/IFR/cache/fringe_spectrographs/"
    ]

    for path in paths:
        files = os.listdir(path)
        for file in files:
            os.remove(path + file)


app = QApplication([])
app.setStyle("Windows")
ui = UI()
Controller(ui=ui)
sys.exit(program_exit())
