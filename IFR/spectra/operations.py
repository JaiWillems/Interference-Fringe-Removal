"""`DataBlock` and Numpy array operations.

This module contains the `DataOperations` class to manipulate interferogram and
spectrum data held within `DataBlock` and Numpy array objects.
"""


from spectra.dataobjects import DataBlock
from typing import Tuple
import numpy as np


class DataOperations(object):
    """`DataBlock` and Numpy array operations.

    The `DataOperations` class allows for the manipulation of interferogram and
    spectrum data held within `DataBlock` and Numpy array objects.

    Methods
    -------
    FFT(y_data, LWN, SSP, LFL)
        Return the (Hermitian) Fast Fourier Transform.
    zero_fill(data, factor, dl=0)
        Return `DataBlock` with zero filled array's.
    fringe_spectrograph(dataBlock, min, max)
        Return the fringe spectrum component.
    alignment(dataBlock_one, dataBlock_two)
        Return the aligned `DataBlock` object.
    """

    def FFT(self, y: np.array, LWN: float, SSP: float, LFL:
            float) -> Tuple[np.array, np.array]:
        """Return the (Hermitian) Fast Fourier Transform.

        This method takes in a dependent spectrum data array and performs the
        Hermitian Fast Fourier Transform on the data.

        Parameters
        ----------
        y : np.array
            Dependent variable data array to be Fourier Transformed.
        LWN : float
            Laser wave number.
        SSP : float
            Sample spacing divisor.
        LFL : float
            Low folding limit.

        Returns
        -------
        tuple
            Return a tuple of Numpy arrays each of shape (n,) containing the
            x and y Fourier Transformed data.

        Notes
        -----
        The Hermitian Fourier Transform which requires data to have Hermitian
        symmetry was justified by the program input data being phase corrected.
        """

        n = y.size
        y_out = np.fft.hfft(y)[:n]  # Take only the positive frequency parts.
        x_out = np.fft.fftfreq(2 * n)[:n] * 2 * LWN / SSP + LFL

        return x_out, y_out

    def zero_fill(self, data: DataBlock, factor: int, dl: int=0) -> DataBlock:
        """Return `DataBlock` with zero filled array's.

        This method will zero fill the x and y data arrays of the input
        `DataBlock` in accordance with the `factor` and `dl` parameters.

        Parameters
        ----------
        data : DataBlock
            `DataBlock` object containing the interferogram data to zero fill.
        factor : int
            Zero fill factor as a positive integer.
        dl : int, optional
            Pad the input `data` with `dl` zero values before extending the
            data by the zero fill factor. Note that `dl` must be a positive
            integer.

        Returns
        -------
        DataBlock
            `DataBlock` containing the x and y zero filled data arrays.

        Notes
        -----
        This method will first append `dl` zeroes to the data arrays before
        applying the zero fill factor. The `dl` parameter was added in to
        allow `DataBlock` alignment before zero filling the data. For example,
        one might increase a background data set to the length of the sample
        data set before applying the same zero fill factor to both data sets.
        This ensures the final data in both cases have the same final number
        of points which is essential for transmittance and absorbance
        calculations.

        After the `dl` parameter is applied, the method will then extend the
        array using the zero fill factor, `factor`. The zero fill factor will
        increase the new length (after the `dl` operation) of the y data array
        by appending zeros such that its length is a `factor` times larger. The
        x data array will be lengthed by having its indices extended.
        """

        # Get data.
        x_data, y_data = data.x, data.y

        # Extend arrays if the dl parameter is positive.
        if dl > 0:
            curr_length = y_data.size

            # Determine extension arrays.
            x_extend = np.linspace(curr_length + 1, curr_length + dl + 1, dl)
            y_extend = np.zeros((dl,))

            # Extend arrays.
            x_data = np.append(x_data, x_extend)
            y_data = np.append(y_data, y_extend)

        # Determine the number of points to extend using the zero fill factor.
        curr_length = y_data.size
        pad_length = (factor - 1) * curr_length

        # Determine extension arrays.
        x_extend = np.linspace(curr_length, curr_length + pad_length, pad_length)
        y_extend = np.zeros((pad_length,))

        # Extend arrays.
        x = np.append(x_data, x_extend)
        y = np.append(y_data, y_extend)

        # Create output DataBlock.
        dataBlock_new = data.copy()
        dataBlock_new.x = x
        dataBlock_new.y = y
        dataBlock_new.minY = np.min(y)
        dataBlock_new.maxY = np.max(y)

        return dataBlock_new

    def fringe_spectrograph(self, dataBlock: DataBlock, min: int, max:
                            int) -> DataBlock:
        """Return the fringe spectrum component.

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
            Returns the fringe spectrum component as a `DataBlock` object.
            The fringe spectrum will have the same number of points as the
            input `dataBlock` data.

        Notes
        -----
        This method calculates the fringe spectrum component using the
        following steps:

        1. Find the interferogram data up to an including the fringe. FFT the
        data.

        2. Find the interferogram data up to but not including the fringe. FFT
        the data.

        3. Subtract the FFT's data from part 2 from the FFT'd data in part 1 to
        get the spectrum component due only to the fringe.
        """

        # Get instrument parameters.
        LWN = dataBlock.params["LWN"]
        SSP = dataBlock.params["SSP"]
        LFL = dataBlock.params["LFL"]

        y = dataBlock.y

        n_init = 2 * y.size

        # Get the data and sizes of the two data sets to FFT.
        # y_one contains the fringe whereas y_two does not.
        y_one, y_two = y[:max + 1], y[:min]
        n_one, n_two = y_one.size, y_two.size

        # Zero fill the data arrays to be of length n_init.
        # The final FFT will cause half the points to have negative
        # frequencies. We want only the positive frequency values and will
        # loose half out data points doing this, thus we extend arrays to two
        # times the input data length.
        y_one = np.append(y_one, np.zeros((n_init - n_one,)))
        y_two = np.append(y_two, np.zeros((n_init - n_two,)))

        # FFT the data.
        x, y_one = self.FFT(y_one, LWN, SSP, LFL)
        x, y_two = self.FFT(y_two, LWN, SSP, LFL)

        # Subtract to get the fringe component.
        y_final = y_one - y_two

        # Create new data block.
        dataBlock_new = dataBlock.copy()
        dataBlock_new.type = "FIG"
        dataBlock_new.x = x[::2]
        dataBlock_new.y = y_final[::2]
        dataBlock_new.minY = np.min(y_final)
        dataBlock_new.maxY = np.max(y_final)

        return dataBlock_new

    def alignment(self, dataBlock_one: DataBlock, dataBlock_two:
                  DataBlock) -> DataBlock:
        """Return an aligned `DataBlock` object.

        This method zero fills `dataBlock_one`'s interferogram to the length of
        `dataBlock_two` and returns the `DataBlock` object containing the
        single beam spectrum of `dataBlock_one`.

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

        Notes
        -----
        This method is designed to make background and sample spectra have the
        same number of points before taking their ratio for transmittance
        calculations.

        The process takes the inverse Fourier Transform of `dataBlock_one` to
        get a double sided interferogram. It then appends zeros within the
        center of the interferogram to get the same number of points as
        `dataBlock_two` before applying the Fourier Transform to get the
        aligned spectrum.
        """

        y_one = dataBlock_one.y
        n_one = y_one.size

        x_two = dataBlock_two.x
        n_two = x_two.size

        # Get the spectrums interferogram.
        y_one = np.fft.ifft(y_one)

        # Generate the new interferogram components.
        part_one = y_one[:n_one//2]
        part_two = np.zeros((n_two - n_one,))
        part_three = y_one[n_one//2:]

        # Zero fill the data array.
        y_one = np.concatenate((part_one, part_two, part_three))

        # Attain the spectrum.
        y_one = np.fft.fft(y_one)

        x_one = x_two

        # Create output data block.
        dataBlock_one_new = dataBlock_one.copy()
        dataBlock_one_new.x = x_one
        dataBlock_one_new.y = y_one
        dataBlock_one_new.minY = np.min(y_one)
        dataBlock_one_new.maxY = np.max(y_one)

        return dataBlock_one_new
