"""Store OPUS file data.

The dataobjects module contains the `DataOPUS` and `DataBlock` class's to
organize and store OPUs file data.
"""


import opusFC


class DataOPUS(object):
    """Store OPUS file data.
    
    The `DataOPUS` class takes the path to an OPUS file and uploads the data
    into `DataBlock` objects.

    Parameters
    ----------
    path : str
        Path of OPUS file.
    
    Attributes
    ----------
    data : dict
        Dictionary containing `DataBlock` objects where the keys are the
        `DataBlock.type` attributes.
    """

    def __init__(self, path: str) -> None:
        """Initialize attributes."""

        self.data = {}

        data_blocks = opusFC.listContents(path)

        for data_block in data_blocks:
            block_object = DataBlock(opusFC.getOpusData(path, data_block))
            self.data[block_object.type] = block_object


class DataBlock(object):
    """Locallize OPUS data blocks.
    
    Parameters
    ----------
    data : opusFC.SingleDataReturn
        Data composing an OPUS data block.
    
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

    def __init__(self, data: opusFC.SingleDataReturn) -> None:
        """Initialize attributes."""

        self.dim = data.dimension
        self.type = data.dataType
        self.deriv_type = data.derivative
        self.params = data.parameters
        self.x = data.x
        self.y = data.y
        self.minY = data.minY
        self.maxY = data.maxY
