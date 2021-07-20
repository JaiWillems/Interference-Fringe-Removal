

from spectra import DataOperations,  OPUSLoader
import matplotlib.pyplot as plt


# Get file paths.
background_file_name = "BCKGRND_294.65K_8M_6X_03-17-21_15.31_Emission back parallel input_0.015360_80 kHz_KBr_BEB_AVG120.0"
sample_file_name = "Propene_0.101Torr_294.65K_8M_6X_03-17-21_23.54_Emission back parallel input_0.000960_80 kHz_KBr_BEB_AVG122.0"
file_directory_path = "IFR/data/"

background_path = file_directory_path + background_file_name
sample_path = file_directory_path + sample_file_name


# Prepare file data.
background_data = OPUSLoader(background_path)
sample_data = OPUSLoader(sample_path)

background_SSC = DataOperations().mertz(background_data.data["SIFG"], background_data.data["SSC"])
background_SIFG = DataOperations().IFFT(background_SSC)

sample_SSC = DataOperations().mertz(sample_data.data["SIFG"], sample_data.data["SSC"])
sample_SIFG = DataOperations().IFFT(sample_SSC)


while 1:
    plt.figure()

    plt.subplot(1, 2, 1)
    plt.plot(background_SIFG.x, background_SIFG.y, label="Background IFG", linewidth=0.5)
    plt.plot(sample_SIFG.x, sample_SIFG.y, label="Propene IFG", linewidth=0.5)
    plt.title("Interferogram")
    plt.legend()
    plt.grid()

    plt.subplot(1, 2, 2)
    plt.plot(background_SSC.x[::50], background_SSC.y[::50], label="Background SSC", linewidth=0.5)
    plt.plot(sample_SSC.x[::50], sample_SSC.y[::50], label="Propene SSC", linewidth=0.5)
    plt.title("Spectrograph")
    plt.legend()
    plt.grid()

    plt.show()

    start = int(input("Fringe Start Index: "))
    end = int(input("Fringe End Index: "))

    sample_SIFG = DataOperations().fringe_removal(start, end, sample_SIFG)
    sample_SSC = DataOperations().FFT(sample_SIFG)

