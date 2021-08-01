from openfisca_uk_data.datasets.spi.base_spi import BaseSPI
from openfisca_uk_data.datasets.spi.raw_spi import RawSPI
from openfisca_core.model_api import *
from openfisca_uk_data.datasets.spi.base_spi.model_input_variables import (
    get_input_variables,
)
from openfisca_uk_data.utils import (
    CAPITAL_INCOME_VARIABLES,
    LABOUR_INCOME_VARIABLES,
    dataset,
    uprated,
)
import h5py


def from_FRS(year: int = 2018):
    from openfisca_uk import CountryTaxBenefitSystem

    system = CountryTaxBenefitSystem()
    variables = []
    for variable in get_input_variables():
        try:
            variables += [type(system.variables[variable.__name__])]
        except:
            variables += [variable]
    for i in range(len(variables)):
        variable = variables[i]
        if variable.__name__ in LABOUR_INCOME_VARIABLES:
            variables[i] = uprated(
                "uprating.labour_income", from_year=year + 1
            )(variable)
        elif variable.__name__ in CAPITAL_INCOME_VARIABLES:
            variables[i] = uprated(
                "uprating.labour_income", from_year=year + 1
            )(variable)
        else:
            variables[i] = uprated(from_year=year + 1)(variable)

    class reform(Reform):
        def apply(self):
            for var in variables:
                self.update_variable(var)

    return reform


@dataset
class SPI:
    name = "spi"
    openfisca_uk_compatible = True

    def generate(year):
        base_frs_years = BaseSPI().years
        if len(base_frs_years) == 0:
            raw_frs_years = RawSPI().years
            if len(raw_frs_years) == 0:
                raise Exception("No FRS microdata to generate from")
            else:
                base_frs_year = max(raw_frs_years)
        else:
            base_frs_year = max(base_frs_years)

        from openfisca_uk import Microsimulation

        base_frs_sim = Microsimulation(dataset=BaseSPI, year=base_frs_year)
        person_vars, benunit_vars, household_vars = [
            [
                var.__name__
                for var in get_input_variables()
                if var.entity.key == entity
            ]
            for entity in ("person", "benunit", "household")
        ]
        person_vars += [
            "P_person_id",
            "P_benunit_id",
            "P_household_id",
            "P_role",
        ]
        benunit_vars += ["B_benunit_id"]
        household_vars += ["H_household_id"]
        with h5py.File(SPI.file(year), mode="w") as f:
            for year in range(int(year), int(year) + 10):
                for variable in person_vars + benunit_vars + household_vars:
                    f[f"{variable}/{year}"] = base_frs_sim.calc(
                        variable, year
                    ).values
