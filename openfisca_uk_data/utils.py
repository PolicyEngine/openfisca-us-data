from pathlib import Path
import shutil
from typing import Callable, Type
from openfisca_core.model_api import *


def data_folder(path: str, erase=False) -> Path:
    folder = Path(path)
    folder.mkdir(exist_ok=True, parents=True)
    if erase:
        shutil.rmtree(folder)
        folder.mkdir()
    return folder


def safe_rmdir(path: str):
    if Path(path).exists():
        shutil.rmtree(path)


PACKAGE_DIR = Path(__file__).parent
DATA_DIR = PACKAGE_DIR / "microdata"


LABOUR_INCOME_VARIABLES = (
    "employment_income",
    "self_employment_income",
)

CAPITAL_INCOME_VARIABLES = (
    "pension_income",
    "dividend_income",
    "savings_interest_income",
    "trading_income",
    "property_income",
    "sublet_income",
)


def uprated(parameter: str = None, from_year: int = 2018) -> Callable:
    def get_uprating_variable(variable: Type[Variable]) -> Type[Variable]:
        def formula(entity, period, parameters):
            if parameter is None:
                return entity(variable.__name__, period.last_year)
            else:
                current_year_factor = parameters(period)
                last_year_factor = parameters(period.last_year)
                for name in parameter.split("."):
                    last_year_factor = last_year_factor[name]
                    current_year_factor = current_year_factor[name]
                multiplier = current_year_factor / last_year_factor
                return multiplier * entity(variable.__name__, period.last_year)

        setattr(variable, f"formula_{from_year}", formula)
        return variable

    return get_uprating_variable
