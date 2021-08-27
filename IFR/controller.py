"""User interface file for the Interference-Fringe-Removal program.

This module contains the `Controller` class to add functionality to the
programs widgets.
"""


from definitions import FRINGE_CACHE_PATH, SIFG_CACHE_PATH, SSC_CACHE_PATH
from functools import partial
from PyQt5.QtWidgets import QCheckBox, QFileDialog
from spectra.dataobjects import DataBlock, OPUSLoader
from spectra.operations import DataOperations as DO
from typing import List, Literal, Tuple
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
    cache_file_save(path, label, x, y)
        Save file to cache system as a `.npy` format.
    cache_file_load(path, label)
        Load file from cache system.
    update_fringe_list(label)
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
        """Initialize attributes.

        Notes
        -----
        This method initializes the `Controller` class by setting important
        attributes and calling the method to connect widgets to control
        sequences.
        """

        self.ui = ui
        self.fringes = {}

        self.connect_signals()

    def connect_signals(self) -> None:
        """Connect widgets to control sequences.

        This method adds functionality to widgets by connecting them to
        control sequences to be called when interfaced with.
        """

        self.ui.background_upload.clicked.connect(partial(self.upload_data, False))
        self.ui.sample_upload.clicked.connect(partial(self.upload_data, True))
        self.ui.select_fringe.clicked.connect(self.fringe_localization)
        self.ui.update_plot.clicked.connect(self.update_plot)
        self.ui.save_data.clicked.connect(self.save_dpt)

    def SIFG_plot(self) -> None:
        """Plot interferogram data.

        This method plots all interferogram data on the interferogram plot.

        Notes
        -----
        This method will load and plot every data file in the interferogram
        cache file directory.
        """

        # Configure plot parameter.
        self.ui.SIFG_plot.clear()
        self.ui.SIFG_plot.set_title("Interferogram")
        self.ui.SIFG_plot.set_xlabel("Steps")
        self.ui.SIFG_plot.set_ylabel("Intensity")

        # Gather and plot interferogram data.
        files = os.listdir(SIFG_CACHE_PATH)
        for file in files:
            path, label = SIFG_CACHE_PATH, file[:-4]
            x, y = self.cache_file_load(path, label)
            self.ui.SIFG_plot.plot(x, y, label=self.get_plot_name(label))

        # Configure and update plot.
        self.ui.SIFG_plot.legend()
        self.ui.SIFG_plot.grid()
        self.ui.SIFG_canvas.draw()

    def SSC_plot(self) -> None:
        """Plot spectrum data.

        This method plots all spectrum data that satisfies the constraints of
        the included plots and data mode settings.

        Parameters
        ----------
        args : tuple
            Tuple of length three with format `(x, y, label)` where `x` is the
            x data, `y` is the y-data, and `label` is the plot label.

        Notes
        -----
        This method iterates through all data files in the spectrum cache file
        directory. The program then decodes the data information using the file
        label and checks if the data should be plotted comparing it to the
        user selected plotting parameters (i.e. selected plots and plot mode
        controls).
        """

        # Get which "included plot" checkboxes are selected.
        background_bool = self.ui.background_plot.isChecked()
        sample_bool = self.ui.sample_plot.isChecked()
        original_bool = self.ui.original_plot.isChecked()
        processed_bool = self.ui.processed_plot.isChecked()
        fringe_bool = self.ui.select_fringe_plot.isChecked()

        # Determine the data mode to plot.
        if self.ui.mode_S.isChecked():
            type = "SB"
        elif self.ui.mode_A.isChecked():
            type = "A"
        else:
            type = "T"

        # Get current plot axis limits.
        x_lim = self.ui.SSC_plot.get_xlim()
        y_lim = self.ui.SSC_plot.get_ylim()

        # Initialize a clear plot.
        self.ui.SSC_plot.clear()
        self.ui.SSC_plot.set_title("Spectrograph")

        # If the plot type has not changed since the last plot update, then
        # keep the same zoom parameters. Otherwise, set new zoom parameters.
        if self.prev_type == type:
            self.ui.SSC_plot.set_xlim(x_lim)
            self.ui.SSC_plot.set_ylim(y_lim)
        else:
            if type == "A":
                y_lim = (0, 10)
            elif type == "T":
                y_lim = (-5, 5)

            self.ui.SSC_plot.set_ylim(y_lim)

        self.prev_type = type

        # Configure plot.
        self.ui.SSC_plot.set_xlabel("Frequency")
        self.ui.SSC_plot.set_ylabel("Intensity")

        # Check and plot desired spectra.
        files = os.listdir(SSC_CACHE_PATH)
        for file in files:

            # If a plot type does not satisfy the desired plot constraints then
            # do not plot the data.
            file_parts = file[:-4].split("_")
            plot = True

            if file_parts[2] != type:
                plot = False

            if file_parts[1] == "O" and not original_bool:
                plot = False
            elif file_parts[1] == "P" and not processed_bool:
                plot = False

            try:
                if file_parts[3] == "B" and not background_bool:
                    plot = False
                elif file_parts[3] == "S" and not sample_bool:
                    plot = False
            except:
                pass

            # Plot the data if it satisfies all contraints.
            if plot:
                # Get plotting data and settings.
                PPRF = int(self.ui.PPRF.currentText())
                path, label = SSC_CACHE_PATH, file[:-4]
                x, y = self.cache_file_load(path, label)

                # Reduce plotting points.
                x_plot, y_plot = x[::PPRF], y[::PPRF]

                # Get label and plot data.
                label = self.get_plot_name(label)
                self.ui.SSC_plot.plot(x_plot, y_plot, label=label)

        # Plot fringes if fringes are selected to plot.
        if fringe_bool:

            # Create list of fringe labels to plot.
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

            # Plot selected fringes.
            for label in fringe_names:
                x, y = self.cache_file_load(FRINGE_CACHE_PATH, label)
                self.ui.SSC_plot.plot(x, y, label=label)

        # Configure plot.
        self.ui.SSC_plot.legend()
        self.ui.SSC_plot.grid()
        self.ui.SSC_canvas.draw()

    def get_plot_name(self, label: str) -> str:
        """Return plot name from data label.

        This method takes an encoded file label and decodes the plot
        information to create useful names for plot legends.

        Parameters
        ----------
        label : str
            String representing the data label

        Returns
        -------
        str
            String representing the plot name.

        Notes
        -----
        The file naming convention for single beam data is `{a}_{b}_SB_{c}`,
        for absorbance data is `{a}_{b}_A`, and for transmittance data is
        `{a}_{b}_T` where `a` defines the plot type as either an interferogram
        ("SIFG") or spectrum ("SSC"), `b` defines the plot as either original
        ("O") or processed ("P") data, and `c` defines the data as either
        sample ("S") or background ("B") data.
        """

        # Define correspondance between a label and name.
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

        # Populate name information for each label part.
        for part in label_parts:
            name_parts.append(define[part])

        # Convert the list to a name string.
        name = " ".join(name_parts)

        return name

    def upload_data(self, sample: bool) -> None:
        """Upload OPUS data.

        This method opens a file select window to allow the selection of a data
        file. It then loads, saves, and plots the file data.

        Parameters
        ----------
        sample : bool
            If `sample=True`, the selected file upload will initialize the
            sample data, else it will initialize the background data.

        Notes
        -----
        After getting the file path, this method will upload the data and do
        some preliminary processing. It will then get all neccessary plot
        representations defined by the plotting parameters and save the
        representations as `.npy` binary files. By saving these files, they
        will be accessible to the plotting function when `update_plot` is
        called.
        """

        # Get file path.
        caption, filter = "Open File", "OPUS files (*.0)"
        path, _ = QFileDialog.getOpenFileName(caption=caption, filter=filter)

        # Error handling for when no path is selected.
        if path == "":
            return None

        # Upload and prepare data.
        data = OPUSLoader(path)
        if sample:
            self.sample_data = data
        else:
            self.background_data = data
        SIFG_data = data.data["SIFG"]
        SSC_data = data.data["SSC"]

        # Update the spectrum plot using the programs FFT methodology.
        LWN, SSP = SIFG_data.params["LWN"], SIFG_data.params["SSP"]
        LFL = SSC_data.params["LFL"]
        SSC_data.x, SSC_data.y = DO().FFT(SIFG_data.y, LWN, SSP, LFL)

        # If this is the second of the two file uploads, prepare the
        # transmittance and absorbance data.
        try:
            if sample:
                data = self.background_data.data["SSC"]
            else:
                data = self.sample_data.data["SSC"]
            plot_params = self.prepare_plot_data(data, SSC_data, state="O")
        except:
            plot_params = [(SSC_data.x, SSC_data.y, "SSC_O_SB_S")]

        self.prev_type = "SB"

        # Get file label.
        label = "SIFG_O_S" if sample else "SIFG_O_B"

        # Save generate plot represetations as .npy binary files.
        self.save_plot_data((SIFG_data.x, SIFG_data.y, label), *plot_params)

        # Set spectrum x scale.
        x_min = np.min(SSC_data.x) - 0.1 * np.max(SSC_data.x)
        x_max = 1.1 * np.max(SSC_data.x)
        self.ui.SSC_plot.set_xlim(x_min, x_max)

        # Set spectrum y scale.
        y_min = np.min(SSC_data.y) - 0.1 * np.max(SSC_data.y)
        y_max = 1.1 * np.max(SSC_data.y)
        self.ui.SSC_plot.set_ylim(y_min, y_max)

        self.SIFG_plot()
        self.SSC_plot()

    def fringe_localization(self) -> None:
        """Calculate the fringe spectrum component.

        Notes
        -----
        This method takes the fringe start and end positions to localize the
        fringe and calculate the fringe spectrum component. The fringe is then
        named and stored in the fringe cache file directory as a `.npy`
        binary file.
        """

        # Do not calculate fringe if both the sample and background are not
        # uploaded.
        try:
            background_data = self.background_data.data["SIFG"]
            sample_data = self.sample_data.data["SIFG"]
        except:
            return None

        # Get fringe bounds.
        start = int(self.ui.fringe_start.text())
        end = int(self.ui.fringe_end.text())

        # Do not calculate if the fringe location is invalid.
        if (end - start <= 0) or (end < 0) or (start < 0):
            return None

        # Get background fringe label.
        ind = np.where((start <= background_data.x) & (background_data.x <= end))
        background_label = "fringe_" + str(np.max(background_data.y[ind])) + "b"

        # Get the background fringe spectrum component.
        fringe_spectrograph = DO().fringe_spectrograph(background_data, start, end)
        background_x, background_y = fringe_spectrograph.x, fringe_spectrograph.y

        # Get the sample fringe label.
        ind = np.where((start <= sample_data.x) & (sample_data.x <= end))
        sample_label = "fringe_" + str(np.max(sample_data.y[ind])) + "s"

        # Get the sample fringe spectrum component.
        fringe_spectrograph = DO().fringe_spectrograph(sample_data, start, end)
        sample_x, sample_y = fringe_spectrograph.x, fringe_spectrograph.y

        # Save fringe spectrum components to cache file system.
        path = FRINGE_CACHE_PATH
        self.cache_file_save(path, background_label, background_x, background_y)
        self.cache_file_save(path, sample_label, sample_x, sample_y)

        # Add the fringe to the fringe select window.
        fringe_label = sample_label + ", " + background_label + f", {start}-{end}"
        self.update_fringe_list(fringe_label)

    def cache_file_save(self, path: str, label: str, x: np.array, y:
                        np.array) -> None:
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

        Notes
        -----
        The interim data is stored as files to reduce time to plot data when
        the update plot button is pressed. Binary files were chosen due to
        quicker upload and save times over other file formats.
        """

        # Get file label.
        file_name = path + "/" + label

        # Prepare file data.
        x, y = x.reshape((-1, 1)), y.reshape((-1, 1))
        data = np.concatenate((x, y), axis=1)

        # Save data file.
        np.save(file_name, data)

    def cache_file_load(self, path: str, label: str) -> Tuple[np.array, np.array]:
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

        Notes
        -----
        The interim data is stored as files to reduce time to plot data when
        the update plot button is pressed. Binary files were chosen due to
        quicker upload and save times over other file formats.
        """

        # Get file name.
        file_name = path + "/" + label + ".npy"

        # Upload and prepare data.
        data = np.load(file_name)
        x, y = data[:, 0], data[:, 1]

        return x, y

    def update_fringe_list(self, label: str) -> None:
        """Update the fringe selection scrollable area.

        Parameters
        ----------
        label : str
            Label identifier of the fringe.

        Notes
        -----
        This method is called after the fringe localization method to add the
        newly localized fringe to the fringe select window and allow for fringe
        removal.
        """

        layout = self.ui.scroll_widget.layout()
        layout.insertWidget(layout.count() - 1, QCheckBox(label))

    def update_plot(self) -> None:
        """Plot the processed spectra.

        This method takes the single beam spectra data, subtracts the selected
        fringes, and plots the processed spectra data.
        """

        # Check if data is available, else do not execute method.
        try:
            background_data = self.background_data.data["SSC"].copy()
            sample_data = self.sample_data.data["SSC"].copy()
        except:
            self.ui.mode_S.setChecked(True)
            return None

        # Get selected fringe labels.
        fringe_names = []
        for i in range(self.ui.scroll_layout.count()):
            widget = self.ui.scroll_layout.itemAt(i).widget()
            if widget.isChecked():
                fringe_names.append(widget.text())

        # Subtract selected fringe spectrum components from single beam data.
        path = FRINGE_CACHE_PATH
        self.fringes = {}
        for fringe in fringe_names:
            fringe_one, fringe_two, bounds = fringe.split(", ")
            start, end = bounds.split("-")
            start, end = int(start), int(end)
            self.fringes[fringe] = start, end

            _, y = self.cache_file_load(path, fringe_one)
            sample_data.y = sample_data.y - y

            _, y = self.cache_file_load(path, fringe_two)
            background_data.y = background_data.y - y

        # Prepare, save, and plot data.
        plot_params = self.prepare_plot_data(background_data, sample_data, state="P")
        self.save_plot_data(*plot_params)
        self.SSC_plot()

    def prepare_plot_data(self, dataBlock_b: DataBlock, dataBlock_s: DataBlock,
                          state: Literal["O", "P"]) -> List:
        """Return plot tuples of correct mode data.

        This method takes background and sample data blocks to calculate and
        return the required plots.

        Parameters
        ----------
        dataBlock_b, dataBlock_s : DataBlock
            Background and sample single beam spectral `DataBlock`'s.
        state : {"O", "P"}
            Indicator of the data being original or processed.

        Returns
        -------
        List
            List of plotting tuples.

        Notes
        -----
        This method is designed to return a list of plotting tuples that can be
        unpacked into the `save_plot_data` method using the `*` parameter
        prefix. By doing this, all neccessary plot representations will be
        saved in the cache file system and become available when updating the
        spectrograph plot.
        """

        plots = []

        # Get single beam plotting tuples.
        SSC_B_S = (dataBlock_b.x, dataBlock_b.y, f"SSC_{state}_SB_B")
        SSC_S_S = (dataBlock_s.x, dataBlock_s.y, f"SSC_{state}_SB_S")

        plots.extend([SSC_B_S, SSC_S_S])

        # Check if transmittance or absorbance is needed.
        t_bool = self.ui.mode_T.isChecked()
        a_bool = self.ui.mode_A.isChecked()

        if t_bool or a_bool or state == "O":

            # Calculate the transmittance spectrum.
            background_align = DO().alignment(dataBlock_b, dataBlock_s)
            x = dataBlock_s.x
            y = np.real(dataBlock_s.y) / np.real(background_align.y)

            # Limit the spectrum values to prevent overflow errors.
            y[np.where(y > 5)] = 5
            y[np.where(y < -5)] = -5

            # Get transmittance plotting tuple.
            SSC_T = (x, y, f"SSC_{state}_T")

            plots.append(SSC_T)

            if a_bool or state == "O":

                # Calculate the absorbance spectrum.
                y = -np.log10(y)

                # Get absorbance plotting tuple.
                SSC_A = (x, y, f"SSC_{state}_A")

                plots.append(SSC_A)

        return plots

    def save_plot_data(self, *args: Tuple) -> None:
        """Save plottable data to `.npy` binary files.

        This method takes a series of plotting tuples defined in the
        `prepare_plot_data` method and saved the data as binary files for
        plotting.

        Parameters
        ----------
        args : Tuple
            A series of tuples containing the data x values, y values, and
            data label in the following format: `(x, y, label)`.

        Notes
        -----
        This method is designed to make data that was prepared by the
        `prepare_plot_data` method and save them such that the `update_plot`
        method can be called to plot all data that satisfies the plotting
        constraints.

        By the construction of the `prepare_plot_data`, `save_plot_data`, and
        `update_plot`, only the desired plots will be calculated and saved
        before being plotted.
        """

        for arg in args:

            # Get tuple information.
            x, y, label = arg[0], arg[1], arg[2]

            type = label.split("_")[0]

            # Get file save directory.
            if type == "SSC":
                path = SSC_CACHE_PATH
            elif type == "SIFG":
                path = SIFG_CACHE_PATH
            else:
                path = FRINGE_CACHE_PATH

            # Save data.
            self.cache_file_save(path, label, x, y)

    def save_dpt(self) -> None:
        """Save processed spectra data as a DPT file.

        This method saves zero filled and processed single beam, absorbance,
        and transmittance data as data point tables.

        Notes
        -----
        This method first zero fills the background and sample single beam
        data and zero fills by the inputted factor before re-calculating and
        removing all fringe components. The absorbance and transmittance data
        is then calculated. In total, five files will be exported containing
        the background single beam, sample single beam, absorbance,
        transmittance, and remove fringe locations.
        """

        # Get file save path.
        caption, filter = "Save File", "Data Point Table files (*.dpt)"
        path, _ = QFileDialog.getSaveFileName(caption=caption, filter=filter)

        # Do not continue is an invalid file name is given.
        if path == "":
            return None

        # Get the zero fill factor.
        zff = self.ui.zff_input.currentText()
        try:
            zff = int(zff)
        except:
            zff = 1

        # Zero fill the background interferogram.
        n_sample = self.sample_data.data["SIFG"].y.size
        n_background = self.background_data.data["SIFG"].y.size
        dl = n_sample - n_background
        background_SIFG = DO().zero_fill(self.background_data.data["SIFG"], zff, dl)

        # Get background instrument parameters.
        LWN_b = background_SIFG.params["LWN"]
        SSP_b = background_SIFG.params["SSP"]
        LFL_b = background_SIFG.params["LFL"]

        # Get the zero filled background single beam.
        x_b, y_b = DO().FFT(background_SIFG.y, LWN_b, SSP_b, LFL_b)
        x_b, y_b = np.real(x_b), np.real(y_b)

        for fringe in self.fringes:

            min, max = self.fringes[fringe]

            # Calculate each fringe spectrum components.
            background_fringe = DO().fringe_spectrograph(background_SIFG, min, max)
            y_b = y_b - np.real(background_fringe.y)

        del background_SIFG

        # Save the background single beam data.
        x, y = x_b.reshape((-1, 1)), y_b.reshape((-1, 1))
        dpt_data_b = np.concatenate((x, y), axis=1)
        file_name = path[:-4] + f"_ZFF{zff}_SINGLE_BEAM_BACKGROUND.dpt"
        np.savetxt(file_name, dpt_data_b, fmt="%4.7f", delimiter=",")

        # Zero fill the sample interferogran.
        sample_SIFG = DO().zero_fill(self.sample_data.data["SIFG"], zff)

        # Get the sample instrument parameters.
        LWN_s = sample_SIFG.params["LWN"]
        SSP_s = sample_SIFG.params["SSP"]
        LFL_s = sample_SIFG.params["LFL"]

        # Get the zero filled sample single beam.
        x_s, y_s = DO().FFT(sample_SIFG.y, LWN_s, SSP_s, LFL_s)
        x_s, y_s = np.real(x_s), np.real(y_s)

        for fringe in self.fringes:

            min, max = self.fringes[fringe]

            # Calculate each fringe spectrum component.
            sample_fringe = DO().fringe_spectrograph(sample_SIFG, min, max)
            y_s = y_s - np.real(sample_fringe.y)

        del sample_SIFG

        # Save the sample single beam data.
        x, y = x_s.reshape((-1, 1)), y_s.reshape((-1, 1))
        dpt_data_s = np.concatenate((x, y), axis=1)
        file_name = path[:-4] + f"_ZFF{zff}_SINGLE_BEAM_SAMPLE.dpt"
        np.savetxt(file_name, dpt_data_s, fmt="%4.7f", delimiter=",")

        # Calculate the transmittance spectrum.
        y_t = np.real(y_s) / np.real(y_b)
        y_t[np.where(y_t > 5)] = 5
        y_t[np.where(y_t < -5)] = -5

        # Save the transmittance spectrum.
        y = y_t.reshape((-1, 1))
        dpt_data_t = np.concatenate((x, y), axis=1)
        file_name = path[:-4] + f"_ZFF{zff}_TRANSMITTANCE.dpt"
        np.savetxt(file_name, dpt_data_t, fmt="%4.7f", delimiter=",")

        del y_b, y_s

        # Calculate the absorbance spectrum.
        y_a = -np.log10(y_t)

        # Save the absorbance spectrum.
        y = y_a.reshape((-1, 1))
        dpt_data_a = np.concatenate((x, y), axis=1)
        file_name = path[:-4] + f"_ZFF{zff}_ABSORBANCE.dpt"
        np.savetxt(file_name, dpt_data_a, fmt="%4.7f", delimiter=",")

        # Save fringe locations.
        fringe_locations = np.array(list(self.fringes.values())).astype(float)
        file_name = path[:-4] + "_REMOVED_FRINGES.dpt"
        np.savetxt(file_name, fringe_locations, fmt="%4.7f", delimiter=",")
