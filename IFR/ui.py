"""User interface file for the Interference-Fringe-Removal program."""


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QDesktopWidget, QGridLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QRadioButton, QScrollArea,
    QVBoxLayout, QWidget
)
import matplotlib.pyplot as plt


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
