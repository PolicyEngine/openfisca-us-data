from openfisca_uk_data.utils import dataset
from openfisca_uk_data.datasets.frs.frs import FRS
import shutil
import pandas as pd
import numpy as np
import h5py

@dataset
class SynthFRS:
    name = "synth_frs"
    openfisca_uk_compatible = True
    input_reform_from_year = FRS.input_reform_from_year

    def generate(year):
        from openfisca_uk import CountryTaxBenefitSystem

        ID_COLS = (
            "P_person_id",
            "P_benunit_id",
            "P_household_id",
            "B_benunit_id",
            "B_household_id",
            "H_household_id",
        )

        def anonymise(df: pd.DataFrame) -> pd.DataFrame:
            result = df.copy()
            for col in result.columns:
                if col not in ID_COLS:
                    # don't change identity columns, this breaks structures
                    if result[col].unique().size < 16:
                        # shuffle categorical columns
                        result[col] = result[col].sample(frac=1).values
                    else:
                        # shuffle + add noise to numeric columns
                        # noise = between -3% and +3% added to each row
                        noise = np.random.rand() * 3e-2 + 1.0
                        result[col] = result[col].sample(frac=1).values * noise
            return result

        year = 2018
        system = CountryTaxBenefitSystem()
        data = FRS.load(year)
        entities = ("person", "benunit", "household")
        entity_dfs = {key: {} for key in entities}
        for entity in entities:
            for variable in data.keys():
                if system.variables[variable].entity.key == entity:
                    entity_dfs[entity][variable] = data[variable][str(year)]
        person, benunit, household = map(lambda x: anonymise(pd.DataFrame(x)), entity_dfs.values())

        year = int(year)

        with h5py.File(
            SynthFRS.data_dir / SynthFRS.filename(year), mode="w"
        ) as f:
            for variable in person.columns:
                f[f"{variable}/{year}"] = person[variable].values
            for variable in benunit.columns:
                f[f"{variable}/{year}"] = benunit[variable].values
            for variable in household.columns:
                f[f"{variable}/{year}"] = household[variable].values


    def save(data_file, year: int = 2018):
        shutil.copyfile(data_file, SynthFRS.data_dir / SynthFRS.filename(year))