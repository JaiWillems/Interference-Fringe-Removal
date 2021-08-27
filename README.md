# <img width="50" height="50" src="/IFR/figures/IFR_logo.png"> Interference-Fringe-Removal (IFR)

The IFR project is a data handling user interface for the FAR-IR beamline of the Canadian Light Source Inc.. The platform uses an in house method to remove interference fringes from OPUS FTIR spectroscopy data.

## User-Interface
![](IFR/figures/ui_display.png)
The Interference-Fringe-Removal functionality is accessible through a user interface that initializes by running the `IFR/main.py` script or by compiling and running as an executable.

A typical work flow should emulate the following pattern:
1. Load sample and background data,
1. Locate all fringes in the interferogram and select them by adding in their bounds to the "Fringe Localization" window,
1. Using the "Fringe Select" window, check which fringes to remove,
1. Select plotting preferences using the "Included Plots" and "Data Mode" controls,
1. Increase the `Plot Point reduction Factor` for more efficient plotting,
1. Update the spectrograph plot by pressing the "Update Plot" button,
1. Pan and zoom to the desired viewing window,
1. Reduce the `Plot Point Reduction Factor` and press "Update Plot" to view the effects of fringe removal on your data,
1. Iterate steps 3 - 8 until satisfied with the resulting data,
1. Select a zero filling factor, and
1. Save the ackground single beam, sample single beam, absorbance, and transmittance spectral data as well as the removed fringe locations as `.dpt` files using the "Save Filtered Data" button.

## Data Requirements
The program assumes that the input OPUS (`.0`) files have an interferogram data block that meets the requirements of being:

* Appropriatly Apodized,
* Phase Corrected,
* Single Sided, and
* Mono-Directional.

The inputted OPUS files must also contain a single beam spectral data block. Example OPUS data files can be seen in the `IFR/data` folder.
