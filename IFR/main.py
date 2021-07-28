

from functools import partial
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QDesktopWidget, QFileDialog, QGridLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QRadioButton, QScrollArea,
    QVBoxLayout, QWidget
)
from spectra.dataobjects import DataBlock, OPUSLoader
from spectra.operations import DataOperations
from typing import List, Literal, Tuple
import matplotlib.pyplot as plt
import numpy as np
import os
import sys


class UI(QMainWindow):

    def __init__(self) -> None:
        """Initialize main UI window."""

        super().__init__()

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
        self.SIFG_plot.set_xlabel("Steps")
        self.SIFG_plot.set_ylabel("Intensity")
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
        self.SSC_plot.set_xlabel("Frequency")
        self.SSC_plot.set_ylabel("Intensity")
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
        self.fringe_start = QLineEdit("0")
        self.fringe_end = QLineEdit("0")
        self.select_fringe = QPushButton("Select")
        self.mode_S = QRadioButton("Single Beam")
        self.mode_A = QRadioButton("Absorbance")
        self.mode_T = QRadioButton("Transmittance")
        self.background_plot = QCheckBox("Background")
        self.sample_plot = QCheckBox("Sample")
        self.original_plot = QCheckBox("Original")
        self.processed_plot = QCheckBox("Processed")
        self.select_fringe_plot = QCheckBox("Selected Fringes")
        self.update_plot = QPushButton("Update Plot")

        # Widgit styling.
        self.background_upload.setStyleSheet("background-color: lightgrey")
        self.sample_upload.setStyleSheet("background-color: lightgrey")
        self.save_data.setStyleSheet("background-color: lightgrey")
        self.select_fringe.setStyleSheet("background-color: lightgrey")
        self.update_plot.setStyleSheet("background-color: lightgrey")

        # Setting QCheckBox check preference.
        self.background_plot.setChecked(True)
        self.sample_plot.setChecked(True)
        self.original_plot.setChecked(True)
        self.processed_plot.setChecked(True)

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
        layout.addWidget(self._scrollable_area(), 2, 4, 5, 1)
        layout.addWidget(QLabel("<b>Data Mode</b>"), 1, 6, 1, 1)
        layout.addWidget(self.mode_S, 2, 6, 1, 1)
        layout.addWidget(self.mode_A, 3, 6, 1, 1)
        layout.addWidget(self.mode_T, 4, 6, 1, 1)
        layout.addWidget(QLabel("<b>Included Plots</b>"), 1, 5, 1, 1)
        layout.addWidget(self.background_plot, 2, 5, 1, 1)
        layout.addWidget(self.sample_plot, 3, 5, 1, 1)
        layout.addWidget(self.original_plot, 4, 5, 1, 1)
        layout.addWidget(self.processed_plot, 5, 5, 1, 1)
        layout.addWidget(self.select_fringe_plot, 6, 5, 1, 1)
        layout.addWidget(QLabel("<b>Update Data</b>"), 1, 7, 1, 1)
        layout.addWidget(self.update_plot, 2, 7, 1, 1)

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
        self.scroll_window.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_window.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_window.setWidgetResizable(True)

        self.scroll_widget = QWidget()

        self.scroll_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.scroll_layout)

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
        self.ui.SIFG_plot.set_xlabel("Steps")
        self.ui.SIFG_plot.set_ylabel("Intensity")

        files = os.listdir(os.getcwd() + "/IFR/cache/SIFG_plot_data")
        for file in files:
            path, label = os.getcwd() + "/IFR/cache/SIFG_plot_data/", file[:-4]
            x, y = self._cache_file_load(path, label)
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

        background_bool = self.ui.background_plot.isChecked()
        sample_bool = self.ui.sample_plot.isChecked()
        original_bool = self.ui.original_plot.isChecked()
        processed_bool = self.ui.processed_plot.isChecked()
        fringe_bool = self.ui.select_fringe_plot.isChecked()

        if self.ui.mode_S.isChecked():
            type = "S"
        elif self.ui.mode_A.isChecked():
            type = "A"
        else:
            type = "T"

        self.ui.SSC_plot.clear()
        self.ui.SSC_plot.set_title("Spectrograph")
        self.ui.SSC_plot.set_xlabel("Frequency")
        self.ui.SSC_plot.set_ylabel("Intensity")

        files = os.listdir(os.getcwd() + "/IFR/cache/SSC_plot_data")
        for file in files:
            plot = False

            if original_bool and file[4] == "O":
                if file[6] == type:
                    if type == "S":
                        if background_bool and file[8] == "B":
                            plot = True
                        if sample_bool and file[8] == "S":
                            plot = True
                    else:
                        plot = True
            elif processed_bool and file[4] == "P":
                if file[6] == type:
                    if type == "S":
                        if background_bool and file[8] == "B":
                            plot = True
                        if sample_bool and file[8] == "S":
                            plot = True
                    else:
                        plot = True

            if plot:
                path, label = os.getcwd() + "/IFR/cache/SSC_plot_data/", file[:-4]
                x, y = self._cache_file_load(path, label)
                self.ui.SSC_plot.plot(x, y, label=label)
        
        if fringe_bool:
            path = os.getcwd() + "/IFR/cache/fringe_spectrographs/"

            fringe_names = []
            for i in range(self.ui.scroll_layout.count()):
                widget = self.ui.scroll_layout.itemAt(i).widget()
                if widget.isChecked():
                    background_fringe_label, sample_fringe_label, _ = widget.text().split(", ")
                    if background_bool:
                        fringe_names.append(background_fringe_label)
                    if sample_bool:
                        fringe_names.append(sample_fringe_label)
            
            for label in fringe_names:
                x, y = self._cache_file_load(path, label)
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

            x1 = self.sample_data.data["SIFG"].x
            y1 = self.sample_data.data["SIFG"].y
            label1 = "SIFG_O_S"

            x2 = self.sample_data.data["SSC"].x
            y2 = self.sample_data.data["SSC"].y
            label2 = "SSC_O_S_S"

            try:
                plot_params = self.prepare_plot_data(self.background_data.data["SSC"], self.sample_data.data["SSC"], state="O")
            except:
                plot_params = [(x2, y2, label2)]

            self.save_plot_data((x1, y1, label1), *plot_params)
            self.SIFG_plot()
            self.SSC_plot()

        else:
            self.background_data = OPUSLoader(path)

            x1 = self.background_data.data["SIFG"].x
            y1 = self.background_data.data["SIFG"].y
            label1 = "SIFG_O_B"

            x2 = self.background_data.data["SSC"].x
            y2 = self.background_data.data["SSC"].y
            label2 = "SSC_O_S_B"

            try:
                plot_params = self.prepare_plot_data(self.background_data.data["SSC"], self.sample_data.data["SSC"], state="O")
            except:
                plot_params = [(x2, y2, label2)]

            self.save_plot_data((x1, y1, label1), *plot_params)
            self.SIFG_plot()
            self.SSC_plot()

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
        ind = np.where((start < background_data.x) & (background_data.x < end))
        background_label = "fringe_" + str(np.max(background_data.y[ind])) + "b"

        length = self.background_data.data["SSC"].y.size
        fringe_spectrograph = DataOperations().fringe_spectrograph(background_data, start, end, length)
        fringe_spectrograph = DataOperations().alignment(fringe_spectrograph, self.background_data.data["SSC"])
        background_x, background_y = fringe_spectrograph.x, fringe_spectrograph.y

        sample_data = self.sample_data.data["SIFG"]
        ind = np.where((start < sample_data.x) & (sample_data.x < end))
        sample_label = "fringe_" + str(np.max(sample_data.y[ind])) + "s"

        length = self.sample_data.data["SSC"].y.size
        fringe_spectrograph = DataOperations().fringe_spectrograph(sample_data, start, end, length)
        fringe_spectrograph = DataOperations().alignment(fringe_spectrograph, self.sample_data.data["SSC"])
        sample_x, sample_y = fringe_spectrograph.x, fringe_spectrograph.y

        path = os.getcwd() + "/IFR/cache/fringe_spectrographs/"
        self._cache_file_save(path, background_label, background_x, background_y)
        self._cache_file_save(path, sample_label, sample_x, sample_y)

        self._update_fringe_list(sample_label + ", " + background_label + f", {start}-{end}")

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

    def _update_fringe_list(self, label: str) -> None:
        """Update the fringe selection scrollable area.

        Parameters
        ----------
        label : str
            Label identifier of the fringe.
        """

        layout = self.ui.scroll_widget.layout()
        layout.insertWidget(layout.count() - 1, QCheckBox(label))

    def update_plot(self) -> None:
        """Plot the processed spectrograph."""

        fringe_names = []
        for i in range(self.ui.scroll_layout.count()):
            widget = self.ui.scroll_layout.itemAt(i).widget()
            if widget.isChecked():
                fringe_names.append(widget.text())

        background_data = self.background_data.data["SSC"].copy()
        sample_data = self.sample_data.data["SSC"].copy()

        path = os.getcwd() + "/IFR/cache/fringe_spectrographs/"
        for fringe in fringe_names:
            fringe_one, fringe_two, _ = fringe.split(", ")

            _, y = self._cache_file_load(path, fringe_one)
            sample_data.y = sample_data.y - y

            _, y = self._cache_file_load(path, fringe_two)
            background_data.y = background_data.y - y
        
        plot_params = self.prepare_plot_data(background_data, sample_data, state="P")
        self.save_plot_data(*plot_params)
        self.SSC_plot()
    
    def prepare_plot_data(self, dataBlock_b: DataBlock, dataBlock_s: DataBlock, state: Literal["O", "P"]) -> List:
        """Return plot tuples of correct mode data.

        Parameters
        ----------
        dataBlock_b, dataBlock_s : DataBlock
            Background and sample single beam spectrograph `DataBlock`'s.
        state : {"O", "P"}
            Indicator of the data being original or processed.
            

        Returns
        -------
        List
            List of plotting tuples.
        
        Notes
        -----
        The returned list of plotting tuples can be unpacked into the
        `save_plot_data` method using the `*` parameter preix.
        """

        SSC_B_S = (dataBlock_b.x, dataBlock_b.y, f"SSC_{state}_S_B")
        SSC_S_S = (dataBlock_s.x, dataBlock_s.y, f"SSC_{state}_S_S")

        background_align = DataOperations().alignment(dataBlock_b, dataBlock_s)
        x = dataBlock_s.x
        y = dataBlock_s.y / background_align.y

        SSC_A = (x, y, f"SSC_{state}_A")

        y = np.exp(2 - y)

        SSC_T = (x, y, f"SSC_{state}_T")

        return [SSC_B_S, SSC_S_S, SSC_A, SSC_T]
    
    def save_plot_data(self, *args):
        """
        """

        SIFG_path = os.getcwd() + "/IFR/cache/SIFG_plot_data/"
        SSC_path = os.getcwd() + "/IFR/cache/SSC_plot_data/"
        fringe_path = os.getcwd() + "/IFR/cache/fringe_spectrographs/"

        for arg in args:
            x, y, label = arg[0], arg[1], arg[2]

            type = label.split("_")[0]

            if type == "SSC":
                path = SSC_path
            elif type =="SIFG":
                path = SIFG_path
            else:
                path = fringe_path
            
            self._cache_file_save(path, label, x, y)



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
