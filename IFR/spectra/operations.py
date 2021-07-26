"""`DataBlock` operations.

The operations module contains the `DataOperations` class to manipulate
interferogram and spectrograph data held within `DataBlock` objects.
"""


from scipy.interpolate import interp1d
from spectra.dataobjects import DataBlock
from typing import Tuple
import matplotlib.pyplot as plt
import numpy as np


class DataOperations(object):
    """`DataBlock` Operations.

    The `DataOperations` class allows for the manipulation of interferogram and
    spectrograph data held within `DataBlock` objects.

    Methods
    -------
    mertz(dataBlock)
        Apply Mertz correction to interferometer data.
    FFT(dataBlock)
        Return the Fast Fourier Transform of the `dataBlock`.
    IFFT(dataBlock)
        Return the Inverse Fast Fourier Transform of the `dataBlock`.
    fringe_removal(min, max, dataBlock)
        Return `dataBlock` with fringe removed.
    alignment(dataBlock_one, dataBlock_two)
        Returned aligned `DataBlock` objects.
    """

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

    def FFT(self, dataBlock: DataBlock) -> DataBlock:
        """Return the Fast Fourier Transform of the `dataBlock`.

        Parameters
        ----------
        dataBlock : DataBlock
            `DataBlock` to be Fourier transformed.
        
        Returns
        -------
        DataBlock
            Return the Fourier transdformed `dataBlock`.
        """

        LWN = dataBlock.params["LWN"]
        SSP = dataBlock.params["SSP"]

        n = dataBlock.y.size
        y = dataBlock.y[:n//2]
        n = y.size

        y = np.fft.fft(y)[:n//2]
        x = np.fft.fftfreq(n, 1.12843 * SSP / (LWN))[:n//2]

        dataBlock_new = DataBlock()

        dataBlock_new.dim = dataBlock.dim
        if dataBlock.type == "SIFG":
            dataBlock_new.type = "SSC"
        dataBlock_new.deriv_type = dataBlock.deriv_type
        dataBlock_new.params = dataBlock.params
        dataBlock_new.x = x
        dataBlock_new.y = y
        dataBlock_new.minY = np.min(y)
        dataBlock_new.maxY = np.max(y)

        return dataBlock_new

    def IFFT(self, dataBlock: DataBlock) -> DataBlock:
        """Return the Inverse Fast Fourier Transform of the `dataBlock`.

        Parameters
        ----------
        dataBlock : DataBlock
            `DataBlock` to be inverse Fourier transformed.
        
        Returns
        -------
        DataBlock
            Return the Fourier transformed `dataBlock`.
        """

        x = dataBlock.x
        y = dataBlock.y
        n = y.size

        y = np.concatenate((y, -y[1:]))
        y = np.fft.ifft(y)
        x = np.linspace(-n, n, 2 * n - 1)

        dataBlock_new = DataBlock()

        dataBlock_new.dim = dataBlock.dim
        if dataBlock.type == "SIFG":
            dataBlock_new.type = "SSC"
        dataBlock_new.deriv_type = dataBlock.deriv_type
        dataBlock_new.params = dataBlock.params
        dataBlock_new.x = x
        dataBlock_new.y = y
        dataBlock_new.minY = np.min(y)
        dataBlock_new.maxY = np.max(y)

        return dataBlock_new
    
    def fringe_removal(self, min: int, max: int, dataBlock: DataBlock) -> DataBlock:
        """Return `dataBlock` with fringe removed.

        This method removes the fringe specified by `start` and `end`,
        inclusive, out of the inputted SIFG `DataBlock` and returns the
        revised `DataBlock`.

        Parameters
        ----------
        min : int
            The start x-value of the fringe to remove.
        max : int
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

        ind = np.where((x < min) | (x > max))[0]

        x_new = x[ind]
        y_new = y[ind]

        ind = np.where((x_new < -max) | (x_new > -min))[0]

        x_new = x_new[ind]
        y_new = y_new[ind]

        dataBlock_new = DataBlock()

        dataBlock_new.dim = dataBlock.dim
        dataBlock_new.type = dataBlock.type
        dataBlock_new.deriv_type = dataBlock.deriv_type
        dataBlock_new.params = dataBlock.params
        dataBlock_new.x = x_new
        dataBlock_new.y = y_new
        dataBlock_new.minY = np.min(y_new)
        dataBlock_new.maxY = np.max(y_new)

        return dataBlock_new
    
    def fringe_spectrograph(self, dataBlock: DataBlock, min: int, max: int) -> DataBlock:
        """Return the fringe spectrograph.

        This method takes a single, mono-directional interferogram with the
        point of zero pathlengths difference located at `x=0` and a fringe
        whose position is defined by `min` and `max` to calculate the fringe's
        contribution to the spectrum.

        Parameters
        ----------
        dataBlock : DataBlock
            Single, mono-directional interferogram.
        min : int
            The lower bounding x-value of the selected fringe.
        max : int
            The upper bounding x-value of the selected fringe.
        
        Returns
        -------
        DataBlock
            Returns the fringe spectrograph component as a `DataBlock` object.
        """

        LWN, SSP = dataBlock.params["LWN"], dataBlock.params["SSP"]
        x, y = dataBlock.x, dataBlock.y

        x_one, y_one = x[:max], y[:max]
        n_one = y_one.size
        x_two, y_two = x_one[:min], y_one[:min]
        n_two = y_two.size

        fill_size = n_one - n_two
        y_two = np.append(y_two, np.zeros((fill_size,)))
        x_two = np.indices((n_one,))[0]
        n_two = y_two.size

        y_one = np.fft.fft(y_one)[:n_one//2]
        x_one = np.fft.fftfreq(n_one, 1.12843 * SSP / LWN)[:n_one//2]
        y_two = np.fft.fft(y_two)[:n_two//2]
        x_two = np.fft.fftfreq(n_two, 1.12843 * SSP / LWN)[:n_two//2]

        y_final = y_two - y_one

        dataBlock_new = DataBlock()

        dataBlock_new.dim = dataBlock.dim
        dataBlock_new.type = "FIG"
        dataBlock_new.deriv_type = dataBlock.deriv_type
        dataBlock_new.params = dataBlock.params
        dataBlock_new.x = x_two
        dataBlock_new.y = y_final
        dataBlock_new.minY = np.min(y_final)
        dataBlock_new.maxY = np.max(y_final)

        return dataBlock_new

    def alignment(self, dataBlock_one: DataBlock, dataBlock_two: DataBlock) -> Tuple[DataBlock, DataBlock]:
        """Returned aligned `DataBlock` objects.

        This method interpolates the `DataBlock` with the shortest `x` and `y`
        attributes such that the `x` values align between the two `DataBlock`
        objects.

        Parameters
        ----------
        dataBlock_one, dataBlock_two : DataBlock
            `DataBlock` objects to align where `dataBlock_one`'s `x` and `y`
            attributes are shorter than those of `dataBlock_two`.
        
        Returns
        -------
        DataBlock
            Return aligned `DataBlock` objects.
        """

        y_one = dataBlock_one.y
        n_one = y_one.size

        x_two = dataBlock_two.x
        n_two = x_two.size

        x_one = x_two

        x_one_dx = np.linspace(0, n_one, n_one)
        x_one_idx = np.linspace(0, n_one, n_two)

        interp = interp1d(x_one_dx, y_one)
        y_one = interp(x_one_idx)

        dataBlock_one_new = DataBlock()

        dataBlock_one_new.dim = dataBlock_one.dim
        dataBlock_one_new.type = dataBlock_one.type
        dataBlock_one_new.deriv_type = dataBlock_one.deriv_type
        dataBlock_one_new.params = dataBlock_one.params
        dataBlock_one_new.x = x_one
        dataBlock_one_new.y = y_one
        dataBlock_one_new.minY = np.min(y_one)
        dataBlock_one_new.maxY = np.max(y_one)

        return dataBlock_one_new, dataBlock_two
