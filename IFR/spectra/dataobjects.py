"""OPUS file handling.

This module contains the `DataOPUS` and `DataBlock` class's along with the
`OPUSLoader` function to handle OPUS file data.
"""


import imghdr
import opusFC


class OPUSData(object):
    """Host OPUS file data.

    The `OPUSData` class is a simple data structure to hold all plot
    representations, `DataBlock`'s, contained within an OPUS file.

    Attributes
    ----------
    data : Dict
        Dictionary of `DataBlock` objects where the key is the block's `type`
        attribute.
    """

    def __init__(self) -> None:
        """Initialize attributes."""

        self.data = {}


class DataBlock(object):
    """Host data block information.

    The `DataBlock` class is a simple data structure to hold all information
    regarding a specific plot representation from an OPUS file.

    Attributes
    ----------
    dim : str
        Dimension of the data block.
    type : str
        Data block type.
    deriv_type : {"NONE", "1DER", "2DER", "NDER"}
        Datablock derivative type.
    params : dict
        Dictionary of data parameters, sample parameters, and instrument
        parameters.
    x : np.array
        Array of shape (n,) containing x coordinate spectrum data.
    y : np.array
        Array of shape (n,) containing y coordinate spectrum data.
    minY : float
        Minimum y value.
    maxY : float
        Maximum y value.

    Methods
    -------
    copy()
        Return a `DataBlock` copy.
    """

    def __init__(self) -> None:
        """Initialize attributes."""

        self.dim = None
        self.type = None
        self.deriv_type = None
        self.params = None
        self.x = None
        self.y = None
        self.minY = None
        self.maxY = None

    def copy(self):
        """Return a `DataBlock` copy.

        This method returns a new instantiation of the data block with
        identicle attributes.

        Returns
        -------
        DataBlock
            A copy of the host `DataBlock`.

        Notes
        -----
        This method was inspired by the need to edit attributes of a
        `DataBlock` object in a function scope without changing the original
        instantiation.
        """

        dataBlock_new = DataBlock()

        dataBlock_new.dim = self.dim
        dataBlock_new.type = self.type
        dataBlock_new.deriv_type = self.deriv_type
        dataBlock_new.params = self.params
        dataBlock_new.x = self.x
        dataBlock_new.y = self.y
        dataBlock_new.minY = self.minY
        dataBlock_new.maxY = self.maxY

        return dataBlock_new


def OPUSLoader(path: str) -> OPUSData:
    """Return an `OPUSData` object of the OPUS file data.

    This conveinence function takes a path to an OPUS file and instantiates a
    `DataBlock` object for each plot data representation and combines them into
    one `OPUSData` object.

    Parameters
    ----------
    path : str
        String specifying the path to an OPUS file.

    Returns
    -------
    OPUSData
        Return the file data as an `OPUSData` object.
    """

    # Import OPUS data.
    opusData = OPUSData()
    data_blocks = opusFC.listContents(path)

    # Iterate through each plot representation.
    for data_block in data_blocks:

        # Get plot data.
        data = opusFC.getOpusData(path, data_block)

        # Create `DataBlock` object with plot data.
        block_object = DataBlock()
        block_object.dim = data.dimension
        block_object.type = data.dataType
        block_object.deriv_type = data.derivative
        block_object.params = data.parameters
        block_object.x = data.x
        block_object.y = data.y
        block_object.minY = data.minY
        block_object.maxY = data.maxY

        # Add `DataBlock` instantiation to `OPUSData` object.
        opusData.data[block_object.type] = block_object

    return opusData
