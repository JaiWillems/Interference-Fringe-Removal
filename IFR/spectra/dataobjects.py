"""OPUS file handling.

The dataobjects module contains the `DataOPUS` and `DataBlock` class's along
with the `OPUSLoader` function to handle OPUS file data.
"""


import opusFC


class OPUSData(object):
    """Host OPUS file data.

    Attributes
    ----------
    data : Dict
        Dictionary of `DataBlock` objects where the keys are the blocks `type`
        attribute.
    """

    def __init__(self) -> None:
        """Initialize attributes."""

        self.data = {}


class DataBlock(object):
    """Host data block information.

    Attributes
    ----------
    dim : str
        Dimension of the datablock.
    type : str
        Datablock type.
    deriv_type : {"NONE", "1DER", "2DER", "NDER"}
        Datablock derivative type.
    params : dict
        Dictionary of data, sample, and instrument parameters.
    x : np.array
        Array of shape (n,) containing spectru x coordinate data.
    y : np.array
        Array of shape (n,) containing spectru y coordinate data.
    minY : float
        Minimum y value.
    maxY : float
        maximum y value.
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

        Returns
        -------
        DataBlock
            A copy of the host `DataBlock`.
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

    Parameters
    ----------
    path : str
        String specifying the path to an OPUS file.
    
    Returns
    -------
    OPUSData
        Return the file data as an `OPUSData` object.
    """

    opusData = OPUSData()
    data_blocks = opusFC.listContents(path)

    for data_block in data_blocks:
        data = opusFC.getOpusData(path, data_block)

        block_object = DataBlock()
        block_object.dim = data.dimension
        block_object.type = data.dataType
        block_object.deriv_type = data.derivative
        block_object.params = data.parameters
        block_object.x = data.x
        block_object.y = data.y
        block_object.minY = data.minY
        block_object.maxY = data.maxY

        opusData.data[block_object.type] = block_object
    
    return opusData
