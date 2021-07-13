

from spectra import DataOPUS, DataOperations
import matplotlib.pyplot as plt


background_file_name = "BCKGRND_294.65K_8M_6X_03-17-21_15.31_Emission back parallel input_0.015360_80 kHz_KBr_BEB_AVG120.0"
data_file_name = "Propene_0.101Torr_294.65K_8M_6X_03-17-21_23.54_Emission back parallel input_0.000960_80 kHz_KBr_BEB_AVG122.0"
file_directory_path = "../Interferograms/"

background_path = file_directory_path + background_file_name
data_path = file_directory_path + data_file_name

background_data = DataOPUS(background_path)
propene_data = DataOPUS(data_path)

plt.plot(background_data.data["SIFG"].x, background_data.data["SIFG"].y, label="Background IFG", linewidth=0.5)
plt.plot(propene_data.data["SIFG"].x, propene_data.data["SIFG"].y, label="Propene IFG", linewidth=0.5)
plt.title("Interferogram")
plt.legend()
plt.grid()
plt.show()

plt.plot(background_data.data["SSC"].x, background_data.data["SSC"].y, label="Background SSC", linewidth=0.5)
plt.plot(propene_data.data["SSC"].x, propene_data.data["SSC"].y, label="Propene SSC", linewidth=0.5)
plt.title("Spectrograph")
plt.legend()
plt.grid()
plt.show()
