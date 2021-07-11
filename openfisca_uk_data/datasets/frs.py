from pathlib import Path
from typing import List
from openfisca_uk_data.dataset import Dataset
import pandas as pd


class FRS(Dataset):
    source: str = "https://beta.ukdataservice.ac.uk/datacatalogue/series/series?id=200017#!/access-data"
    years: List[int] = []
    metadata: dict = {}

    def save(zipfile_path: str, year: int = None) -> None:
        raise NotImplementedError()

    def load(table: str = None, year: int = None) -> pd.DataFrame:
        raise NotImplementedError()
