from pathlib import Path
from typing import List
import pandas as pd
from openfisca_uk_data import DATA_DIR
from openfisca_uk_data.utils import data_folder

class Dataset:
    source: str = None
    years: List[int] = []
    metadata: dict = {}

    def __init__(self):
        self.data_folder = data_folder(DATA_DIR / self.__class__.__name__)

    def save(zipfile_path: str, year: int = None) -> None:
        raise NotImplementedError()
    
    def load(table: str = None, year: int = None) -> pd.DataFrame:
        raise NotImplementedError()
