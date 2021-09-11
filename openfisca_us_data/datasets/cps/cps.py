from openfisca_us_data.utils import US, dataset
from openfisca_us_data.datasets.cps.base_cps import BaseCPS
from openfisca_us_data.datasets.cps.raw_cps import RawCPS
from openfisca_us_data.datasets.cps.base_cps.model_input_variables import (
    get_input_variables,
)
import h5py


@dataset
class CPS:
    name = "cps"
    model = US

    def generate(year) -> None:
        if year not in BaseCPS.years:
            if year not in RawCPS.years:
                RawCPS.generate(year)
            BaseCPS.generate(year)
        from openfisca_us import Microsimulation

        base_cps_sim = Microsimulation(dataset=BaseCPS, year=year)
        person_vars, benunit_vars, household_vars = [
            [
                var.__name__
                for var in get_input_variables()
                if var.entity.key == entity
            ]
            for entity in ("person", "benunit", "household")
        ]
        with h5py.File(CPS.file(year), mode="w") as f:
            for variable in person_vars + benunit_vars + household_vars:
                try:
                    f[f"{variable}/{year}"] = base_cps_sim.calc(
                        variable, year
                    ).values
                except:
                    f[f"{variable}/{year}"] = base_cps_sim.calc(
                        variable, year
                    ).values.astype("S")
