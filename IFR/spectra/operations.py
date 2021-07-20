

from spectra.dataobjects import DataBlock
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


class DataOperations:

    def __init__(self):
        
        super().__init__()
    
    def _zero_fill(self, data, factor):
        """Return zero filled array.

        Parameters
        ----------
        data : np.array
            Array of size (n,) to zero fill.
        factor : int
            Zero fill factor.
        
        Returns
        -------
        Tuple
            Tuple containing the x and y zero filled array data.

        Notes
        -----
        The zero fill factor will increase the length of the inputted array
        by `factor` times.
        """

        curr_length = data.size
        pad_length = factor * curr_length
        end_length = curr_length + pad_length

        x = np.arange(0, end_length, 1)
        y = np.append(data, np.zeros((pad_length,)))

        return x, y
    
    def _rotate(self, data: np.array) -> np.array:
        """Return rotated array.

        This method localizes the point of zero pathlengths difference (ZPD)
        and rotates the interferogram such that the ZPD point and all points
        to its right get moved to the left of the interferogram.

        Parameters
        ----------
        data : np.array
            Array of shape (n,) containing interferogram data to rotate.
        
        Returns
        -------
        np.array
            Rotated interferogram.
        """

        ZPD = int(np.where(data == np.max(data))[0])

        left = data[:ZPD]
        right = data[ZPD:]
        data = np.concatenate((right, left))

        return data


    def mertz(self, dataBlock, dataBlock_2):
        """Apply Mertz correction to interferometer data.

        Parameters
        ----------
        dataBlock : DataBlock
            `DataBlock` containing the uncorrected interferogram data.
        
        Returns
        -------
        x, y : np.array
            Typle of arrays containing the corrected spectrograph.
        """

        # fig = plt.figure()

        # Part 1.
        LWN = dataBlock.params["LWN"]
        SSP = dataBlock.params["SSP"]

        n = dataBlock.y.size
        x = dataBlock.x[:n//2]
        y = dataBlock.y[:n//2]
        n = y.size

        x, y = self._zero_fill(y, 2)

        # Multiply by weighting function.
        ZPD = int(np.where(y == np.max(y))[0])
        ramp = np.linspace(0, 1, 2 * ZPD)
        plateu = np.full((y.size - 2 * ZPD), 1)
        weighting_func = np.concatenate((ramp, plateu))
        y *= weighting_func

        # Rotate interferogram.
        y = self._rotate(y)

        # Perform FFT
        n = y.size
        y = np.fft.fft(y)[:n//2]
        x = np.fft.fftfreq(n, SSP / (2 * LWN))[:n//2]

        # Part 2.
        n2 = dataBlock.y.size
        x2 = dataBlock.x[:n2//2]
        y2 = dataBlock.y[:n2//2]
        n2 = y2.size

        ZPD = int(np.where(y2 == np.max(y2))[0])
        y2 = y2[:2 * ZPD]

        x2, y2 = self._zero_fill(y2, 2)
        y2 = self._rotate(y2)

        n2 = y2.size
        y2 = np.fft.fft(y2)[:n2//2]
        x2 = np.fft.fftfreq(n2, SSP / (2 * LWN))[:n2//2]

        phase = np.arctan2(np.imag(y2), np.real(y2))

        plt.subplot(1, 2, 1)
        plt.plot(x, np.real(y), linewidth=0.5, label="Real Part (Part 1)")
        plt.plot(x, np.imag(y), linewidth=0.5, label="Imaginary Part (Part 1)")
        plt.plot(x2, np.real(y2), linewidth=0.5, label="Real Part (Part 2)")
        plt.plot(x2, np.imag(y2), linewidth=0.5, label="Imaginary Part (Part 2)")
        plt.plot(x2, phase, linewidth=0.5, label="Phase")
        plt.title("Spectra Components")
        plt.xlim(300, 1300)
        plt.ylim(-4, 4)
        plt.legend()
        plt.grid()

        x = np.real(x)
        y = np.real(y)
        x2 = np.real(x2)
        y2 = np.real(y2)

        y = y[np.where(x < np.max(x2))[0]]
        x = x[np.where(x < np.max(x2))[0]]
        phase_interp = interp1d(x2, phase)
        phase = phase_interp(x)
        y2_interp = interp1d(x2, y2, kind="cubic")
        y2 =y2_interp(x)
        x2 = x

        y3 = np.real(y) * np.cos(phase) + np.imag(y) * np.sin(phase)
    
        plt.subplot(1, 2, 2)
        plt.plot(dataBlock_2.x, dataBlock_2.y, label="OPUS Spectrum", linewidth=0.5)
        plt.plot(x2, y3, linewidth=0.5, label="Python Spectrum")
        plt.title("Corrected Spectrograph")
        plt.xlim(300, 1300)
        plt.ylim(-0.5, 5)
        plt.legend()
        plt.grid()
        plt.show()

        dataBlock.x = x2
        dataBlock.y = y2
        dataBlock.minY = np.min(y2)
        dataBlock.maxY = np.max(y2)

        return dataBlock


    def FFT(self, dataBlock):
        """Return the Fast Fourier Transform of the `dataBlock`.

        Parameters
        ----------
        dataBlock : DataBlock
            `DataBlock` to be FFT'd.
        
        Returns
        -------
        DataBlock
            Return the FFT'd `dataBlock`.
        """

        LWN = dataBlock.params["LWN"]
        SSP = dataBlock.params["SSP"]

        n = dataBlock.y.size
        y = dataBlock.y[:n//2]
        n = y.size

        y = np.fft.fft(y)
        x = np.fft.fftfreq(n, SSP / (2 * LWN))

        if dataBlock.type == "SIFG":
            dataBlock.type == "SSC"
        dataBlock.x = x
        dataBlock.y = y
        dataBlock.minY = np.min(y)
        dataBlock.maxY = np.max(y)

        return dataBlock

    def IFFT(self, dataBlock):
        """
        """

        LWN = dataBlock.params["LWN"]
        SSP = dataBlock.params["SSP"]

        x = dataBlock.x
        y = dataBlock.y
        n = y.size

        y = np.fft.ifft(y)
        x = np.linspace(0, n, n)

        if dataBlock.type == "SSC":
            dataBlock.type = "SIFG"
        dataBlock.x = x
        dataBlock.y = y
        dataBlock.minY = np.min(y)
        dataBlock.maxY = np.max(y)

        return dataBlock
    
    def fringe_removal(self, start: int, end: int, dataBlock: DataBlock) -> DataBlock:
        """Return `dataBlock` with fringe removed.

        This method removes the fringe specified by `start` and `end`,
        inclusive, out of the inputted SIFG `DataBlock` and returns the
        revised `DataBlock`.

        Parameters
        ----------
        start : int
            The start x-value of the fringe to remove.
        end : int
            The end x-value of the fringe to remove.
        dataBlock : DataBlock
            A SIFG `DataBlock` to edit.
        
        Returns
        -------
        DataBlock
            Return a `DataBlock` object with the detailed fringe removed.
        """

        x = dataBlock.x
        y = dataBlock.y

        dataBlock.x = np.concatenate((x[:start], x[end + 1:]))
        dataBlock.y = np.concatenate((y[:start], y[end + 1:]))

        return dataBlock



