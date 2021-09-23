from openfisca_us_data.utils import US, dataset
from openfisca_us_data.datasets.acs.raw_acs import RawACS
from pandas import DataFrame
import h5py


@dataset
class ACS:
    name = "acs"
    model = US

    def generate(self, year: int) -> None:
        """Generates the ACS dataset.

        Args:
            year (int): The year of the raw ACS to use.
        """

        # Prepare raw ACS tables
        year = int(year)
        if year not in RawACS.years:
            RawACS.generate(year)

        raw_data = RawACS.load(year)
        acs = h5py.File(ACS.file(year), mode="w")

        person, spm_unit, household = [
            raw_data[entity]
            for entity in (
                "person",
                "spm_unit",
                "household",
            )
        ]

        add_ID_variables(acs, person, spm_unit, household)
        add_SPM_variables(acs, spm_unit)

        raw_data.close()
        acs.close()


def add_ID_variables(
    acs: h5py.File,
    person: DataFrame,
    spm_unit: DataFrame,
    household: DataFrame,
):
    """Add basic ID and weight variables.

    Args:
        acs (h5py.File): The ACS dataset file.
        person (DataFrame): The person table of the ACS.
        spm_unit (DataFrame): The SPM unit table created from the person table
            of the ACS.
        household (DataFrame): The household table of the ACS.
    """
    # Add primary and foreign keys
    acs["person_id"] = person.SERIALNO * 100 + person.SPORDER
    acs["person_spm_unit_id"] = person.SPM_ID
    acs["spm_unit_id"] = spm_unit.SPM_ID
    acs["person_household_id"] = person.SERIALNO
    acs["household_id"] = household.SERIALNO

    # Add weights
    acs["person_weight"] = person.WT / 1e2
    
    acs["spm_unit_weight"] = spm_unit.SPM_WEIGHT / 1e2


def add_SPM_variables(acs: h5py.File, spm_unit: DataFrame):
    acs["SPM_unit_net_income"] = spm_unit.SPM_RESOURCES
    acs["poverty_threshold"] = spm_unit.SPM_POVTHRESHOLD