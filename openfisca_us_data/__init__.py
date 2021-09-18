from openfisca_us_data.datasets import *
from pathlib import Path

REPO = Path(__file__).parent

DATASETS = (
    BaseCPS,
    RawCPS,
    CPS,
)
