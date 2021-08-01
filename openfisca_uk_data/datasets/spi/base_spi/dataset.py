from openfisca_uk_data.datasets.spi.base_spi.model_input_variables import (
    from_BaseSPI,
)
from openfisca_uk_data.utils import dataset
from openfisca_uk_data.datasets.spi.raw_spi import RawSPI
import numpy as np
import pandas as pd
import shutil
import h5py


@dataset
class BaseSPI:
    name = "base_spi"
    openfisca_uk_compatible = True
    input_reform_from_year = from_BaseSPI

    def generate(year):
        person = RawSPI.load(year)["main"]
        missing_population = 66e6 - person.FACT.sum()
        person = person.append(
            {"FACT": missing_population}, ignore_index=True
        ).fillna(0)
        person.columns = [col.upper() for col in person.columns]
        ids = np.arange(len(person))
        person["P_person_id"] = ids
        person["P_benunit_id"] = ids
        person["P_household_id"] = ids
        weight = person.FACT
        person["P_FACT"] = weight

        person["P_role"] = "adult"

        benunit = pd.DataFrame(dict(B_benunit_id=ids))

        household = pd.DataFrame(dict(H_household_id=ids))

        benunit["B_FACT"] = weight
        household["H_FACT"] = weight

        with h5py.File(BaseSPI.file(year), mode="w") as f:
            for variable in person.columns:
                f[f"{variable}/{year}"] = person[variable].values
            for variable in benunit.columns:
                f[f"{variable}/{year}"] = benunit[variable].values
            for variable in household.columns:
                f[f"{variable}/{year}"] = household[variable].values
