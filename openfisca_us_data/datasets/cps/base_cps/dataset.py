from openfisca_us_data.datasets.cps.base_cps.model_input_variables import (
    from_BaseCPS,
)
from openfisca_us_data.utils import *
from openfisca_us_data.datasets.cps.raw_cps import RawCPS
import h5py

PERSON_COLUMNS = (
    "person_id",
    "person_tax_unit_id",
    "person_family_id",
    "person_spm_unit_id",
    "person_household_id",
    "person_weight",
    "P_INT_VAL",
)

TAXUNIT_COLUMNS = (
    "tax_unit_id",
    "tax_unit_weight",
)

FAMILY_COLUMNS = (
    "family_id",
    "family_weight",
)

SPMUNIT_COLUMNS = (
    "spm_unit_id",
    "spm_unit_weight",
)

HOUSEHOLD_COLUMNS = (
    "household_id",
    "household_weight",
)


@dataset
class BaseCPS:
    name = "base_cps"
    model = "openfisca_us"
    input_reform_from_year = from_BaseCPS

    def generate(year):
        with RawCPS.load(year) as storage:
            person = storage.person
            family = storage.family
            household = storage.household
        # prepend column names to avoid conflicting names between tables
        person.rename(
            columns={col: f"P_{col}" for col in person.columns}, inplace=True
        )
        family.rename(
            columns={col: f"F_{col}" for col in family.columns}, inplace=True
        )
        household.rename(
            columns={col: f"H_{col}" for col in household.columns},
            inplace=True,
        )
        person["person_household_id"] = person.P_PH_SEQ
        person["person_family_id"] = person.P_PH_SEQ * 10 + person.P_PF_SEQ
        person["person_id"] = person.P_PH_SEQ * 100 + person.P_P_SEQ
        person["person_tax_unit_id"] = person.P_TAX_ID
        person["person_spm_unit_id"] = person.P_SPM_ID

        family["family_id"] = family.F_FH_SEQ * 10 + family.F_FFPOS
        household["household_id"] = household.H_H_SEQ

        person["person_weight"] = person.P_A_FNLWGT
        tax_unit = pd.DataFrame(index=person.person_tax_unit_id.unique())
        spm_unit = pd.DataFrame(index=person.person_spm_unit_id.unique())
        tax_unit["tax_unit_id"] = tax_unit.index
        spm_unit["spm_unit_id"] = spm_unit.index
        tax_unit[
            "tax_unit_weight"
        ] = 1e5  # not accurate, just a placeholder until development
        spm_unit["spm_unit_weight"] = 1e5
        family["family_weight"] = family.F_FSUP_WGT
        household["household_weight"] = household.H_HSUP_WGT

        with h5py.File(BaseCPS.file(year), mode="w") as f:
            for col in PERSON_COLUMNS:
                f[f"{col}/{year}"] = person[col].values
            for col in TAXUNIT_COLUMNS:
                f[f"{col}/{year}"] = tax_unit[col].values
            for col in FAMILY_COLUMNS:
                f[f"{col}/{year}"] = family[col].values
            for col in HOUSEHOLD_COLUMNS:
                f[f"{col}/{year}"] = household[col].values
            for col in SPMUNIT_COLUMNS:
                f[f"{col}/{year}"] = spm_unit[col].values
