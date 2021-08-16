"""`DataBlock` operations.

The operations module contains the `DataOperations` class to manipulate
interferogram and spectrograph data held within `DataBlock` objects.
"""


from spectra.dataobjects import DataBlock
import numpy as np


class DataOperations(object):
    """`DataBlock` Operations.

    The `DataOperations` class allows for the manipulation of interferogram and
    spectrograph data held within `DataBlock` objects.

    Methods
    -------
    zero_fill(x_data, y_data, factor)
        Return zero filled array.
    fringe_spectrograph(dataBlock, min, max, length)
        Return the fringe spectrograph.
    alignment(dataBlock_one, dataBlock_two)
        Returned aligned `DataBlock` objects.
    """

    def __init__(self):
        
        super().__init__()
    
    def FFT(self, y, LWN, SSP, LFL):
        """
        """

        n = y.size
        y_out = np.fft.hfft(y)[:n]
        x_out = np.fft.fftfreq(2 * n)[:n] * 2 * LWN / SSP + LFL

        return x_out, y_out
    
    def zero_fill(self, data: DataBlock, factor: int, dl: int=0):
        """Return zero filled array.

        Parameters
        ----------
        data : DataBlock
            `DataBlock` object containing the data to zero fill.
        factor : int
            Zero fill factor.
        dl : int, optional
            Pad the inputted `data` with `dl` zero values before expanding the
            data by the zero fill factor.
        
        Returns
        -------
        DataBlock
            `DataBlock` containing the x and y zero filled array data.

        Notes
        -----
        The zero fill factor will increase the length of the y data array by
        the factor `factor` from appending zeros. The x data array will have
        its indices extended.
        """

        x_data, y_data = data.x, data.y

        if dl:
            curr_length = y_data.size
            x_data = np.append(x_data, np.linspace(curr_length, curr_length + dl, dl))
            y_data = np.append(y_data, np.zeros((dl,)))

        curr_length = y_data.size
        pad_length = (factor - 1) * curr_length

        x = np.append(x_data, np.linspace(curr_length, curr_length + pad_length, pad_length))
        y = np.append(y_data, np.zeros((pad_length,)))

        dataBlock_new = DataBlock()

        dataBlock_new.dim = data.dim
        dataBlock_new.type = data.type
        dataBlock_new.deriv_type = data.deriv_type
        dataBlock_new.params = data.params
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
            The lower bounding x-value of the selected fringe.
        max : int
            The upper bounding x-value of the selected fringe.
        
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

        dataBlock_new = DataBlock()

        dataBlock_new.dim = dataBlock.dim
        dataBlock_new.type = "FIG"
        dataBlock_new.deriv_type = dataBlock.deriv_type
        dataBlock_new.params = dataBlock.params
        dataBlock_new.x = x
        dataBlock_new.y = y_final
        dataBlock_new.minY = np.min(y_final)
        dataBlock_new.maxY = np.max(y_final)

        return dataBlock_new

    def alignment(self, dataBlock_one: DataBlock, dataBlock_two: DataBlock) -> DataBlock:
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
            Return aligned `DataBlock` object.
        """

        y_one = dataBlock_one.y
        n_one = y_one.size

        x_two = dataBlock_two.x
        n_two = x_two.size

        y_one = np.fft.ifft(y_one)
        y_one = np.concatenate((y_one[:n_one//2], np.zeros((n_two - n_one,)), y_one[n_one//2:]))
        y_one = np.fft.fft(y_one)

        x_one = x_two

        dataBlock_one_new = DataBlock()

        dataBlock_one_new.dim = dataBlock_one.dim
        dataBlock_one_new.type = dataBlock_one.type
        dataBlock_one_new.deriv_type = dataBlock_one.deriv_type
        dataBlock_one_new.params = dataBlock_one.params
        dataBlock_one_new.x = x_one
        dataBlock_one_new.y = y_one
        dataBlock_one_new.minY = np.min(y_one)
        dataBlock_one_new.maxY = np.max(y_one)

        return dataBlock_one_new
