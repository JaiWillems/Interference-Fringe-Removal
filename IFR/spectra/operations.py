"""`DataBlock` and Numpy array operations.

The operations module contains the `DataOperations` class to manipulate
interferogram and spectrograph data held within `DataBlock` and Numpy array
objects.
"""


from spectra.dataobjects import DataBlock
from typing import Tuple
import numpy as np


class DataOperations(object):
    """`DataBlock` and Numpy array operations.

    The `DataOperations` class allows for the manipulation of interferogram and
    spectrograph data held within `DataBlock` and Numpy array objects.

    Methods
    -------
    FFT(y_data, LWN, SSP, LFL)
        Return the (Hermitian) Fast Fourier Transform.
    zero_fill(data, factor, dl=0)
        Return `DataBlock` with zero filled array.
    fringe_spectrograph(dataBlock, min, max)
        Return the fringe spectrograph.
    alignment(dataBlock_one, dataBlock_two)
        Return aligned `DataBlock` object.
    """

    def __init__(self) -> None:
        
        super().__init__()
    
    def FFT(self, y_data: np.array, LWN: float, SSP: float, LFL: float) -> Tuple[np.array, np.array]:
        """Return the (Hermitian) Fast Fourier Transform.

        Parameters
        ----------
        y_data : np.array
            Dependent variable data array to perform the Fourier Transform on.
        LWN : float
            Laser wave number.
        SSP : float
            Sample spacing divisor.
        LFL : float
            Low folding limit.

        Returns
        -------
        tuple
            Return a tuple of numpy arrays each of shape (n,) containing the
            x and y FFT'd data.
        """

        n = y_data.size
        y_out = np.fft.hfft(y_data)[:n]
        x_out = np.fft.fftfreq(2 * n)[:n] * 2 * LWN / SSP + LFL

        return x_out, y_out
    
    def zero_fill(self, data: DataBlock, factor: int, dl: int=0) -> DataBlock:
        """Return `DataBlock` with zero filled array.

        Parameters
        ----------
        data : DataBlock
            `DataBlock` object containing the interferogram data to zero fill.
        factor : int
            Zero fill factor.
        dl : int, optional
            Pad the inputted `data` with `dl` zero values before extending the
            data by the zero fill factor.
        
        Returns
        -------
        DataBlock
            `DataBlock` containing the x and y zero filled array data.

        Notes
        -----
        The zero fill factor will increase the length of the y data array by
        appending zeros such that its length is a `factor` times larger. The x
        data array will have its indices extended.
        """

        x_data, y_data = data.x, data.y

        if dl:
            curr_length = y_data.size
            x_data = np.append(x_data, np.linspace(curr_length + 1, curr_length + dl + 1, dl))
            y_data = np.append(y_data, np.zeros((dl,)))

        curr_length = y_data.size
        pad_length = (factor - 1) * curr_length

        x = np.append(x_data, np.linspace(curr_length, curr_length + pad_length, pad_length))
        y = np.append(y_data, np.zeros((pad_length,)))

        dataBlock_new = data.copy()

        dataBlock_new.x = x
        dataBlock_new.y = y
        dataBlock_new.minY = np.min(y)
        dataBlock_new.maxY = np.max(y)

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
            The lower bounding x-index of the selected fringe.
        max : int
            The upper bounding x-index of the selected fringe.
        
        Returns
        -------
        DataBlock
            Returns the fringe spectrograph component as a `DataBlock` object.
            The fringe spectrograph will have the same number of points as the
            inputted `dataBlock` size.
        """

        LWN = dataBlock.params["LWN"]
        SSP = dataBlock.params["SSP"]
        LFL = dataBlock.params["LFL"]

        y = dataBlock.y

        n_init = 2 * y.size

        y_one, y_two = y[:max + 1], y[:min]
        n_one, n_two = y_one.size, y_two.size

        y_one = np.append(y_one, np.zeros((n_init - n_one,)))
        y_two = np.append(y_two, np.zeros((n_init - n_two,)))

        y_one = np.fft.fft(y_one)[:n_init//2]
        y_two = np.fft.fft(y_two)[:n_init//2]
        x = np.fft.fftfreq(n_init, SSP / LWN)[:n_init//2] + LFL

        y_final = y_one - y_two

        dataBlock_new = dataBlock.copy()

        dataBlock_new.type = "FIG"
        dataBlock_new.x = x
        dataBlock_new.y = y_final
        dataBlock_new.minY = np.min(y_final)
        dataBlock_new.maxY = np.max(y_final)

        return dataBlock_new

    def alignment(self, dataBlock_one: DataBlock, dataBlock_two: DataBlock) -> DataBlock:
        """Return aligned `DataBlock` object.

        This method takes `dataBlock_one` and zero fills it's interferogram to
        the length of `dataBlock_two` and returns the `DataBlock` object
        containing the single beam spectrum of `dataBlock_one`.

        Parameters
        ----------
        dataBlock_one, dataBlock_two : DataBlock
            Single beam `DataBlock` objects to align where the `x` and `y`
            attributes of `dataBlock_one` are shorter than those of
            `dataBlock_two`.
        
        Returns
        -------
        DataBlock
            Return the aligned `dataBlock_one` object.
        """

        y_one = dataBlock_one.y
        n_one = y_one.size

        x_two = dataBlock_two.x
        n_two = x_two.size

        y_one = np.fft.ifft(y_one)
        y_one = np.concatenate((y_one[:n_one//2], np.zeros((n_two - n_one,)), y_one[n_one//2:]))
        y_one = np.fft.fft(y_one)

        x_one = x_two

        dataBlock_one_new = dataBlock_one.copy()

        dataBlock_one_new.x = x_one
        dataBlock_one_new.y = y_one
        dataBlock_one_new.minY = np.min(y_one)
        dataBlock_one_new.maxY = np.max(y_one)

        return dataBlock_one_new
