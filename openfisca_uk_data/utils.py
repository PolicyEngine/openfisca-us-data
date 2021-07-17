from pathlib import Path
import shutil
from typing import Callable, Type
from openfisca_core.model_api import *
from pathlib import Path
import shutil
from typing import List
import pandas as pd
import re
import os
from functools import wraps
import h5py


def dataset(cls):
    def generate():
        raise NotImplementedError("No dataset generation function specified")

    if cls.openfisca_uk_compatible:
        cls.data_dir = data_folder(DATA_DIR / "openfisca_uk")
    else:
        cls.data_dir = data_folder(DATA_DIR / "external")

    def years(self):
        pattern = re.compile(f"\n{cls.name}_([0-9]+).h5")
        matches = list(
            map(
                int,
                pattern.findall(
                    "\n".join(
                        map(lambda path: path.name, cls.data_dir.iterdir())
                    )
                ),
            )
        )
        return matches

    cls.years = property(years)

    def last_year(self):
        return sorted(cls.years)[-1]

    cls.last_year = property(last_year)

    def filename(year):
        return f"{cls.name}_{year}.h5"

    cls.filename = staticmethod(filename)

    def load(year) -> pd.DataFrame:
        file = cls.data_dir / cls.filename(year)
        if cls.openfisca_uk_compatible:
            if not file.exists():
                try:
                    cls.generate(year)
                except:
                    print(
                        "No data for the specified year and dataset, and generation failed."
                    )
            return h5py.File(file)
        else:
            return pd.HDFStore(file)

    def remove(year=None):
        if year is None:
            filenames = map(cls.filename(year), cls.years)
        else:
            filenames = (cls.filename(year),)
        for filename in filenames:
            filepath = cls.data_dir / filename
            if filepath.exists():
                os.remove(filepath)

    cls.remove = staticmethod(remove)

    def remove_first_then(generate_func):
        def new_generate_func(year, *args):
            cls.remove(year)
            return generate_func(year, *args)

        return new_generate_func

    if hasattr(cls, "generate"):
        cls.generate = staticmethod(remove_first_then(cls.generate))
    else:
        cls.generate = staticmethod(generate)

    cls.load = staticmethod(load)

    if not hasattr(cls, "input_reform_from_year"):
        cls.input_reform_from_year = lambda year: ()

    return cls


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
