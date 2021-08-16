"""User interface file for the Interference-Fringe-Removal program."""


from definitions import (
    FRINGE_CACHE_PATH, ROOT_DIR, SIFG_CACHE_PATH, SSC_CACHE_PATH
)
from functools import partial
from matplotlib import cycler
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QComboBox, QDesktopWidget,
    QFileDialog, QGridLayout, QLabel, QLineEdit, QMainWindow, QPushButton,
    QRadioButton, QScrollArea, QVBoxLayout, QWidget
)
from spectra.dataobjects import DataBlock, OPUSLoader
from spectra.operations import DataOperations as DO
from typing import List, Literal, Tuple, Union
import matplotlib.pyplot as plt
import numpy as np
import os
import sys


plt.style.use('ggplot')
plt.style.use('seaborn-dark')
color_list = ['#EE6666', '#3388BB', '#9988DD', '#EECC55', '#88BB44', '#FFBBBB']
colors = cycler('color', color_list)
plt.rc('axes', facecolor='#E6E6E6', edgecolor='none', axisbelow=True, prop_cycle=colors)

plt.rcParams['agg.path.chunksize'] = 10000

class UI(QMainWindow):

    def __init__(self) -> None:
        """Initialize main UI window."""

        super().__init__()

        self.setWindowIcon(QIcon("figures/IFR_logo.png"))

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
        self.SIFG_figure.tight_layout()
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
        self.SSC_figure.tight_layout()
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
        self.zff_input = QComboBox()
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
        self.PPRF = QComboBox()

        # Widget styling.
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

        # Data mode button grouping.
        self.mode_button_group = QButtonGroup(self.mode_S)
        self.mode_button_group.addButton(self.mode_S)
        self.mode_button_group.addButton(self.mode_A)
        self.mode_button_group.addButton(self.mode_T)
        self.mode_S.setChecked(True)

        # Configuring ZFF combo box options.
        self.zff_input.addItem("--Zero Fill Factor--")
        self.zff_input.addItem("0")
        self.zff_input.addItem("1")
        self.zff_input.addItem("2")
        self.zff_input.addItem("4")
        self.zff_input.addItem("8")
        self.zff_input.addItem("12")
        self.zff_input.addItem("16")

        # Configuring PPRF combo box options.
        self.PPRF.addItem("1")
        self.PPRF.addItem("2")
        self.PPRF.addItem("3")
        self.PPRF.addItem("4")
        self.PPRF.addItem("5")

        # Widget organization.
        layout = QGridLayout()
        layout.addWidget(QLabel("<b>File Handling</b>"), 1, 1, 1, 1)
        layout.addWidget(self.background_upload, 2, 1, 1, 1)
        layout.addWidget(self.sample_upload, 3, 1, 1, 1)
        layout.addWidget(self.save_data, 4, 1, 1, 1)
        layout.addWidget(self.zff_input, 5, 1, 1, 1)
        layout.addWidget(QLabel("<b>Fringe Localization</b>"), 1, 2, 1, 2)
        layout.addWidget(QLabel("Start:"), 2, 2, 1, 1)
        layout.addWidget(self.fringe_start, 2, 3, 1, 1)
        layout.addWidget(QLabel("End:"), 3, 2, 1, 1)
        layout.addWidget(self.fringe_end, 3, 3, 1, 1)
        layout.addWidget(self.select_fringe, 4, 2, 1, 2)
        layout.addWidget(QLabel("<b>Fringe Select</b>"), 1, 4, 1, 1)
        layout.addWidget(self._scrollable_area(), 2, 4, 5, 1)
        layout.addWidget(QLabel("<b>Included Plots</b>"), 1, 5, 1, 1)
        layout.addWidget(self.background_plot, 2, 5, 1, 1)
        layout.addWidget(self.sample_plot, 3, 5, 1, 1)
        layout.addWidget(self.original_plot, 4, 5, 1, 1)
        layout.addWidget(self.processed_plot, 5, 5, 1, 1)
        layout.addWidget(self.select_fringe_plot, 6, 5, 1, 1)
        layout.addWidget(QLabel("<b>Data Mode</b>"), 1, 6, 1, 1)
        layout.addWidget(self.mode_S, 2, 6, 1, 1)
        layout.addWidget(self.mode_A, 3, 6, 1, 1)
        layout.addWidget(self.mode_T, 4, 6, 1, 1)
        layout.addWidget(QLabel("<b>Update Data</b>"), 1, 7, 1, 1)
        layout.addWidget(self.update_plot, 2, 7, 1, 1)

        layout.addWidget(QLabel("<b>Plot Point Reduction Factor</b>"), 5, 6, 1, 2)
        layout.addWidget(self.PPRF, 6, 6, 1, 2) 

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
        self.ui.save_data.clicked.connect(self.save_dpt)

    def SIFG_plot(self) -> None:
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

        files = os.listdir(SIFG_CACHE_PATH)
        for file in files:
            path, label = SIFG_CACHE_PATH, file[:-4]
            x, y = self._cache_file_load(path, label)
            self.ui.SIFG_plot.plot(x, y, label=self.get_plot_name(label))

        self.ui.SIFG_plot.legend()
        self.ui.SIFG_plot.grid()
        self.ui.SIFG_canvas.draw()

    def SSC_plot(self):
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
            type = "SB"
        elif self.ui.mode_A.isChecked():
            type = "A"
        else:
            type = "T"

        x_lim = self.ui.SSC_plot.get_xlim()
        y_lim = self.ui.SSC_plot.get_ylim()

        self.ui.SSC_plot.clear()
        self.ui.SSC_plot.set_title("Spectrograph")

        if self.prev_type == type:
            self.ui.SSC_plot.set_xlim(x_lim)
            self.ui.SSC_plot.set_ylim(y_lim)
        else:
            if type == "A":
                y_lim = (0, 5.5)
            elif type == "T":
                y_lim = (-0.1, 1.1)

            self.ui.SSC_plot.set_ylim(y_lim)


        self.prev_type = type

        self.ui.SSC_plot.set_xlabel("Frequency")
        self.ui.SSC_plot.set_ylabel("Intensity")

        files = os.listdir(SSC_CACHE_PATH)
        for file in files:
            file_parts = file[:-4].split("_")
            plot = False

            if original_bool and file_parts[1] == "O":
                if file_parts[2] == type:
                    if type == "SB":
                        if background_bool and file_parts[3] == "B":
                            plot = True
                        if sample_bool and file_parts[3] == "S":
                            plot = True
                    else:
                        plot = True
            elif processed_bool and file_parts[1] == "P":
                if file_parts[2] == type:
                    if type == "SB":
                        if background_bool and file_parts[3] == "B":
                            plot = True
                        if sample_bool and file_parts[3] == "S":
                            plot = True
                    else:
                        plot = True

            if plot:
                PPRF = int(self.ui.PPRF.currentText())
                path, label = SSC_CACHE_PATH, file[:-4]
                x, y = self._cache_file_load(path, label)
                self.ui.SSC_plot.plot(x[::PPRF], y[::PPRF], label=self.get_plot_name(label))

        if fringe_bool:

            fringe_names = []
            for i in range(self.ui.scroll_layout.count()):
                widget = self.ui.scroll_layout.itemAt(i).widget()
                if widget.isChecked():
                    labels = widget.text()
                    fringe_label_s, fringe_label_b, _ = labels.split(", ")
                    if background_bool:
                        fringe_names.append(fringe_label_b)
                    if sample_bool:
                        fringe_names.append(fringe_label_s)

            for label in fringe_names:
                x, y = self._cache_file_load(FRINGE_CACHE_PATH, label)
                self.ui.SSC_plot.plot(x, y, label=label)

        self.ui.SSC_plot.legend()
        self.ui.SSC_plot.grid()
        self.ui.SSC_canvas.draw()

    def get_plot_name(self, label):
        """Return plot name from data label.

        Parameters
        ----------
        label : str
            String representing the data label

        Returns
        -------
        str
            String representing the plot name.
        """

        define = {"SIFG": "SIFG",
                  "SSC": "SSC",
                  "O": "Original",
                  "P": "Processed",
                  "S": "Sample",
                  "B": "Background",
                  "SB": "Single Beam",
                  "A": "Absorbance",
                  "T": "Transmittance"}

        label_parts = label.split("_")
        name_parts = []

        for part in label_parts:
            name_parts.append(define[part])

        return " ".join(name_parts)

    def upload_data(self, sample: bool) -> None:
        """Upload OPUS data.

        Parameters
        ----------
        sample : bool
            If `sample=True`, the selected file upload will initialize the
            sample data, else it will initialize the background data.
        """

        caption, filter = "Open File", "OPUS files (*.0)"
        path, _ = QFileDialog.getOpenFileName(caption=caption, filter=filter)

        if path == "":
            return None

        if sample:
            self.sample_data = OPUSLoader(path)

            SIFG_data = self.sample_data.data["SIFG"]
            SSC_data = self.sample_data.data["SSC"]

            x1 = SIFG_data.x
            y1 = SIFG_data.y
            label1 = "SIFG_O_S"

            LWN, SSP = SIFG_data.params["LWN"], SIFG_data.params["SSP"]
            LFL = SSC_data.params["LFL"]
            x2, y2 = DO().FFT(y1, LWN, SSP, LFL)
            label2 = "SSC_O_SB_S"

            SSC_data.x = x2
            SSC_data.y = y2

            try:
                plot_params = self.prepare_plot_data(
                    self.background_data.data["SSC"], SSC_data, state="O")
            except:
                plot_params = [(x2, y2, label2)]

            self.prev_type = "SB"

            self.save_plot_data((x1, y1, label1), *plot_params)
            x_min, x_max = np.min(x2) - 0.1 * np.max(x2), 1.1 * np.max(x2)
            self.ui.SSC_plot.set_xlim(x_min, x_max)
            y_min, y_max = np.min(y2) - 0.1 * np.max(y2), 1.1 * np.max(y2)
            self.ui.SSC_plot.set_ylim(y_min, y_max)
            self.SIFG_plot()
            self.SSC_plot()

        else:
            self.background_data = OPUSLoader(path)

            SIFG_data = self.background_data.data["SIFG"]
            SSC_data = self.background_data.data["SSC"]

            x1 = SIFG_data.x
            y1 = SIFG_data.y
            label1 = "SIFG_O_B"

            LWN, SSP = SIFG_data.params["LWN"], SIFG_data.params["SSP"]
            LFL = SSC_data.params["LFL"]
            x2, y2 = DO().FFT(y1, LWN, SSP, LFL)
            label2 = "SSC_O_SB_B"

            SSC_data.x = x2
            SSC_data.y = y2

            try:
                plot_params = self.prepare_plot_data(
                    SSC_data, self.sample_data.data["SSC"], state="O")
            except:
                plot_params = [(x2, y2, label2)]

            self.prev_type = "SB"

            self.save_plot_data((x1, y1, label1), *plot_params)
            self.SIFG_plot()
            x_min, x_max = np.min(x2) - 0.1 * np.max(x2), 1.1 * np.max(x2)
            self.ui.SSC_plot.set_xlim(x_min, x_max)
            y_min, y_max = np.min(y2) - 0.1 * np.max(y2), 1.1 * np.max(y2)
            self.ui.SSC_plot.set_ylim(y_min, y_max)
            self.SSC_plot()

    def fringe_localization(self) -> None:
        """Calculate fringe spectrograph component.

        This method uses the user defined fringe bounds to localize the fringe
        and calculate the spectrograph component due to the fringe.
        Additionally it will save the resulting fringe spectrograph components
        to `.npy` binary files.
        """

        try:
            background_data = self.background_data.data["SIFG"]
            sample_data = self.sample_data.data["SIFG"]
        except:
            return None

        start = int(self.ui.fringe_start.text())
        end = int(self.ui.fringe_end.text())

        if (end - start <= 0) or (end < 0) or (start < 0):
            return None

        ind = np.where((start <= background_data.x) & (background_data.x <= end))
        background_label = "fringe_" + str(np.max(background_data.y[ind])) + "b"

        fringe_spectrograph = DO().fringe_spectrograph(background_data, start, end)
        background_x, background_y = fringe_spectrograph.x, fringe_spectrograph.y

        ind = np.where((start <= sample_data.x) & (sample_data.x <= end))
        sample_label = "fringe_" + str(np.max(sample_data.y[ind])) + "s"

        fringe_spectrograph = DO().fringe_spectrograph(sample_data, start, end)
        sample_x, sample_y = fringe_spectrograph.x, fringe_spectrograph.y

        path = FRINGE_CACHE_PATH
        self._cache_file_save(path, background_label, background_x, background_y)
        self._cache_file_save(path, sample_label, sample_x, sample_y)

        fringe_label = sample_label + ", " + background_label + f", {start}-{end}"
        self._update_fringe_list(fringe_label)

    def _cache_file_save(self, path: str, label: str, x: np.array, y: np.array) -> None:
        """Save file to cache system as a `.npy` format.

        Parameters
        ----------
        path : str
            Path to the cache file of interest. The path must not end with a
            forward slash.

        label : str
            Label identifier used for file naming.
        x, y : np.array
            Arrays of shape (n,) containing data to be saved.
        """

        file_name = path + "/" + label
        x, y = x.reshape((-1, 1)), y.reshape((-1, 1))
        data = np.concatenate((x, y), axis=1)
        np.save(file_name, data)

    def _cache_file_load(self, path: str, label: str) -> Tuple:
        """Load file from cache system.

        Parameters
        ----------
        path : str
            Path to the cache file of interest. The path must not end with a
            forward slash.
        label : str
            Label identifier used for file naming.

        Returns
        -------
        x, y : np.array
            Arrays of shape (n,) containing data to be saved.
        """

        file_name = path + "/" + label + ".npy"
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

        try:
            background_data = self.background_data.data["SSC"].copy()
            sample_data = self.sample_data.data["SSC"].copy()
        except:
            self.ui.mode_S.setChecked(True)
            return None

        fringe_names = []
        for i in range(self.ui.scroll_layout.count()):
            widget = self.ui.scroll_layout.itemAt(i).widget()
            if widget.isChecked():
                fringe_names.append(widget.text())

        path = FRINGE_CACHE_PATH
        self.fringes = {}
        for fringe in fringe_names:
            fringe_one, fringe_two, bounds = fringe.split(", ")
            start, end = bounds.split("-")
            start, end = int(start), int(end)
            self.fringes[fringe] = start, end

            _, y = self._cache_file_load(path, fringe_one)
            sample_data.y = sample_data.y - y

            _, y = self._cache_file_load(path, fringe_two)
            background_data.y = background_data.y - y

        plot_params = self.prepare_plot_data(background_data, sample_data, state="P")
        self.save_plot_data(*plot_params)
        self.SSC_plot()

    def prepare_plot_data(self, dataBlock_b: DataBlock, dataBlock_s: DataBlock,
                          state: Literal["O", "P"]) -> List:
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

        SSC_B_S = (dataBlock_b.x, dataBlock_b.y, f"SSC_{state}_SB_B")
        SSC_S_S = (dataBlock_s.x, dataBlock_s.y, f"SSC_{state}_SB_S")

        background_align = DO().alignment(dataBlock_b, dataBlock_s)
        x = dataBlock_s.x
        y = np.real(dataBlock_s.y) / np.real(background_align.y)

        SSC_T = (x, y, f"SSC_{state}_T")

        y = np.exp(2 - y)

        SSC_A = (x, y, f"SSC_{state}_A")

        return [SSC_B_S, SSC_S_S, SSC_A, SSC_T]

    def save_plot_data(self, *args: Union[List, Tuple]) -> None:
        """Save plottable data to `.npy` binary files.

        Parameters
        ----------
        args : List, Tuple
            A series of tuples containing the data x values, y values, and
            data label in the following format: `(x, y, label)`.
        """

        for arg in args:
            x, y, label = arg[0], arg[1], arg[2]

            type = label.split("_")[0]

            if type == "SSC":
                path = SSC_CACHE_PATH
            elif type == "SIFG":
                path = SIFG_CACHE_PATH
            else:
                path = FRINGE_CACHE_PATH

            self._cache_file_save(path, label, x, y)

    def save_dpt(self) -> None:
        """Save processed spectrograph as a DPT file.

        This method only works when a proccessed data file exists.
        """

        caption, filter = "Save File", "Data Point Table files (*.dpt)"
        path, _ = QFileDialog.getSaveFileName(caption=caption, filter=filter)

        if path == "":
            return None

        zff = self.ui.zff_input.currentText()
        try:
            zff = int(zff)
        except:
            zff = 1

        # Create and save background single beam spectrum.
        dl = self.sample_data.data["SIFG"].y.size - self.background_data.data["SIFG"].y.size
        background_SIFG = DO().zero_fill(self.background_data.data["SIFG"], zff, dl)

        LWN_b = background_SIFG.params["LWN"]
        SSP_b = background_SIFG.params["SSP"]
        LFL_b = background_SIFG.params["LFL"]

        for fringe in self.fringes:

            min, max = self.fringes[fringe]

            background_fringe = DO().fringe_spectrograph(background_SIFG, min, max)
            background_SIFG.y = background_SIFG.y - background_fringe.y

        x_b, y_b = DO().FFT(background_SIFG.y, LWN_b, SSP_b, LFL_b)

        del background_SIFG

        x, y = x_b.reshape((-1, 1)), y_b.reshape((-1, 1))
        dpt_data_b = np.concatenate((x, y), axis=1)
        file_name = path[:-4] + f"_ZFF{zff}_SINGLE_BEAM_BACKGROUND.dpt"
        np.savetxt(file_name, dpt_data_b, fmt="%4.7f", delimiter=",")

        # Create and save sample single beam spectrum.
        sample_SIFG = DO().zero_fill(self.sample_data.data["SIFG"], zff)

        LWN_s = sample_SIFG.params["LWN"]
        SSP_s = sample_SIFG.params["SSP"]
        LFL_s = sample_SIFG.params["LFL"]

        for fringe in self.fringes:

            min, max = self.fringes[fringe]

            sample_fringe = DO().fringe_spectrograph(sample_SIFG, min, max)
            sample_SIFG.y = sample_SIFG.y - sample_fringe.y

        x_s, y_s = DO().FFT(sample_SIFG.y, LWN_s, SSP_s, LFL_s)

        del sample_SIFG

        x, y = x_s.reshape((-1, 1)), y_s.reshape((-1, 1))
        dpt_data_s = np.concatenate((x, y), axis=1)
        file_name = path[:-4] + f"_ZFF{zff}_SINGLE_BEAM_SAMPLE.dpt"
        np.savetxt(file_name, dpt_data_s, fmt="%4.7f", delimiter=",")

        # Create and save transmittance spectrum.
        y_t = np.real(y_s) / np.real(y_b)
        y = y_t.reshape((-1, 1))
        dpt_data_t = np.concatenate((x, y), axis=1)
        file_name = path[:-4] + f"_ZFF{zff}_TRANSMITTANCE.dpt"
        np.savetxt(file_name, dpt_data_t, fmt="%4.7f", delimiter=",")

        del y_b, y_s

        # Create and save absorbance spectrum.
        y_a = np.exp(2 - y_t)
        y = y_a.reshape((-1, 1))
        dpt_data_a = np.concatenate((x, y), axis=1)
        file_name = path[:-4] + f"_ZFF{zff}_ABSORBANCE.dpt"
        np.savetxt(file_name, dpt_data_a, fmt="%4.7f", delimiter=",")

        # Save fringe locations.
        fringe_locations = np.array(list(self.fringes.values())).astype(float)
        file_name = path[:-4] + "_REMOVED_FRINGES.dpt"
        np.savetxt(file_name, fringe_locations, fmt="%4.7f", delimiter=",")

    def disable_widgets(self):
        for i in range(self.ui.ui_layout.count()):
            widget = self.ui.ui_layout.itemAt(i).widget()
            widget.setEnabled(False)

    def enable_widgets(self):
        for i in range(self.ui.ui_layout.count()):
            widget = self.ui.ui_layout.itemAt(i).widget()
            widget.setEnabled(True)


def cache_setup(root_dir):
    """Setup the cache file system.

    This function initializes the programs file cache system of directories.

    Parameters
    ----------
    root_dir : str
        string representing the programs root directory.
    """

    os.makedirs(root_dir + "/cache/fringe_spectrographs")
    os.makedirs(root_dir + "/cache/SIFG_plot_data")
    os.makedirs(root_dir + "/cache/SSC_plot_data")


def program_exit():
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

    for path in paths:
        files = os.listdir(path)
        for file in files:
            if file[-4:] == ".npy":
                os.remove(path + file)

    os.rmdir(FRINGE_CACHE_PATH)
    os.rmdir(SIFG_CACHE_PATH)
    os.rmdir(SSC_CACHE_PATH)
    os.rmdir(os.path.join(ROOT_DIR, "cache"))


cache_setup(ROOT_DIR)
app = QApplication([])
app.setStyle("Windows")
ui = UI()
Controller(ui=ui)
sys.exit(program_exit())
