"""User interface file for the Interference-Fringe-Removal program."""


from definitions import FRINGE_CACHE_PATH, SIFG_CACHE_PATH, SSC_CACHE_PATH
from functools import partial
from PyQt5.QtWidgets import QCheckBox, QFileDialog
from spectra.dataobjects import DataBlock, OPUSLoader
from spectra.operations import DataOperations as DO
from typing import List, Literal, Tuple, Union
import numpy as np
import os


class Controller(object):
    """Add functionality to the user interface widgets.

    The `Controller` class connects widgets of the user interface to control
    sequences to add widget functionality.

    Parameters
    ----------
    ui : UI
        The user interface for the `Controller` class to control.
    
    Attributes
    ----------
    ui : UI
        The user interface for the `Controller` class to control.
    fringes : dict
        Dictionary of fringes where the keys are the fringe names and the
        values are tuples containing the start and end x-values associated
        with the fringe.
    
    Methods
    -------
    connect_signals()
        Connect widgets to control sequences.
    SIFG_plot()
        Plot interferogram data.
    SSC_plot()
        Plot spectrum data.
    get_plot_name(label)
        Return plot name from data label.
    upload_data(sample)
        Upload OPUS data.
    fringe_localization()
        Calculate the fringe spectrum component.
    _cache_file_save(path, label, x, y)
        Save file to cache system as a `.npy` format.
    _cache_file_load(path, label)
        Load file from cache system.
    _update_fringe_list(label)
        Update the fringe selection scrollable area.
    update_plot()
        Plot the processed spectrogra.
    prepare_plot_data(dataBlock_b, dataBlock_s, state)
        Return plot tuples of correct mode data.
    save_plot_data(*args)
        Save plottable data to `.npy` binary files.
    save_dpt()
        Save processed spectra data as a DPT file.
    """

    def __init__(self, ui):
        """Initialize attributes."""

        self.ui = ui
        self.fringes = {}

        self.connect_signals()

    def connect_signals(self) -> None:
        """Connect widgets to control sequences."""

        self.ui.background_upload.clicked.connect(partial(self.upload_data, False))
        self.ui.sample_upload.clicked.connect(partial(self.upload_data, True))
        self.ui.select_fringe.clicked.connect(self.fringe_localization)
        self.ui.update_plot.clicked.connect(self.update_plot)
        self.ui.save_data.clicked.connect(self.save_dpt)

    def SIFG_plot(self) -> None:
        """Plot interferogram data."""

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

    def SSC_plot(self) -> None:
        """Plot spectrum data.

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

    def get_plot_name(self, label: str) -> str:
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
        """Calculate the fringe spectrum component.

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

    def _cache_file_load(self, path: str, label: str) -> Tuple[np.array, np.array]:
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
        """Plot the processed spectra."""

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
            Background and sample single beam spectrum `DataBlock`'s.
        state : {"O", "P"}
            Indicator of the data being original or processed.

        Returns
        -------
        List
            List of plotting tuples.

        Notes
        -----
        The returned list of plotting tuples can be unpacked into the
        `save_plot_data` method using the `*` parameter prefix.
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

    def save_plot_data(self, *args: Tuple) -> None:
        """Save plottable data to `.npy` binary files.

        Parameters
        ----------
        args : Tuple
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
        """Save processed spectra data as a DPT file.

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

        x_b, y_b = DO().FFT(background_SIFG.y, LWN_b, SSP_b, LFL_b)
        x_b, y_b = np.real(x_b), np.real(y_b)

        for fringe in self.fringes:

            min, max = self.fringes[fringe]

            background_fringe = DO().fringe_spectrograph(background_SIFG, min, max)
            y_b = y_b - np.real(background_fringe.y)

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

        x_s, y_s = DO().FFT(sample_SIFG.y, LWN_s, SSP_s, LFL_s)
        x_s, y_s = np.real(x_s), np.real(y_s)

        for fringe in self.fringes:

            min, max = self.fringes[fringe]

            sample_fringe = DO().fringe_spectrograph(sample_SIFG, min, max)
            y_s = y_s - np.real(sample_fringe.y)

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
