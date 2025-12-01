import os
from dongnae import DongnaeEngine

_CurrentDir = os.path.dirname(__file__)
_DataPath = os.path.join(_CurrentDir, 'data', 'dongnaeKR_251130.csv')

class dongnaekr(DongnaeEngine):
    """
    DongnaeEngine with pre-loaded Korean dataset.
    """
    def __init__(self):
        super().__init__(csv_path=_DataPath)

__all__ = ['dongnaekr']
