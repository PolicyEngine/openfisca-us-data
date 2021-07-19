from openfisca_uk_data.datasets.frs.base_frs.model_input_variables import (
    from_BaseFRS,
)
from openfisca_uk_data.utils import dataset
import pandas as pd
import numpy as np
import warnings
from openfisca_uk_data.datasets.frs.raw_frs import RawFRS
import h5py


@dataset
class BaseFRS:
    name = "base_frs"
    openfisca_uk_compatible = True
    input_reform_from_year = from_BaseFRS

    def generate(year):
        raw_frs_files = RawFRS.load(year)
        tables = (
            "adult",
            "child",
            "accounts",
            "benefits",
            "job",
            "benunit",
            "househol",
            "chldcare",
        )
        (
            frs_adult,
            frs_child,
            frs_accounts,
            frs_benefits,
            frs_job,
            frs_benunit,
            frs_household,
            frs_childcare,
        ) = [raw_frs_files[table] for table in tables]

        person = frs_adult.drop(["AGE"], axis=1)
        person["role"] = "adult"

        get_new_columns = lambda df: list(
            df.columns.difference(person.columns)
        ) + ["person_id"]
        person = pd.merge(
            person,
            frs_child[get_new_columns(frs_child)],
            how="outer",
            on="person_id",
        ).sort_values("person_id")

        person["role"].fillna("child", inplace=True)

        # link capital income sources (amounts summed by account type)

        accounts = (
            frs_accounts[get_new_columns(frs_accounts)]
            .groupby(["person_id", "ACCOUNT"])
            .sum()
            .reset_index()
        )
        accounts = accounts.pivot(index="person_id", columns="ACCOUNT")[
            ["ACCINT"]
        ].reset_index()
        accounts.columns = accounts.columns.get_level_values(1)
        accounts = accounts.add_prefix("ACCINT_ACCOUNT_CODE_").reset_index()
        person = pd.merge(
            person,
            accounts,
            how="outer",
            left_on="person_id",
            right_on="ACCINT_ACCOUNT_CODE_",
        )

        # link benefit income sources (amounts summed by benefit program)

        bens = frs_benefits[get_new_columns(frs_benefits)]

        # distinguish income-related JSA and ESA from contribution-based variants

        bonus_to_IB_benefits = 1000 * (
            bens.VAR2.isin((2, 4)) & bens.BENEFIT.isin((14, 16))
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            bens["BENEFIT"] += bonus_to_IB_benefits
        benefits = bens.groupby(["person_id", "BENEFIT"]).sum().reset_index()
        benefits = benefits.pivot(index="person_id", columns="BENEFIT")[
            ["BENAMT"]
        ].reset_index()
        benefits.columns = benefits.columns.get_level_values(1)
        benefits = benefits.add_prefix("BENAMT_BENEFIT_CODE_").reset_index()
        person = pd.merge(
            person,
            benefits,
            how="outer",
            left_on="person_id",
            right_on="BENAMT_BENEFIT_CODE_",
        )

        # link job-level data (all fields summed across all jobs)

        job = (
            frs_job[get_new_columns(frs_job)]
            .groupby("person_id")
            .sum()
            .reset_index()
        )
        person = pd.merge(person, job, how="outer", on="person_id").fillna(0)

        person["benunit_id"] = person["person_id"] // 1e1
        person["household_id"] = person["person_id"] // 1e2

        childcare = (
            frs_childcare[get_new_columns(frs_childcare)]
            .groupby("person_id")
            .sum()
            .reset_index()
        )
        person = pd.merge(
            person, childcare, how="outer", on="person_id"
        ).fillna(0)
        person = person.add_prefix("P_")

        # generate benefit unit and household datasets

        benunit = frs_benunit.fillna(0).add_prefix("B_")

        # Council Tax is severely under-reported in the micro-data - find
        # mean & std for each (region, CT band) pair and sample from distribution.
        # rows with missing regions or CT bands are sampled from the same distributions, respectively

        CT_mean = frs_household.groupby(
            ["GVTREGNO", "CTBAND"], dropna=False
        ).CTANNUAL.mean()
        CT_std = frs_household.groupby(
            ["GVTREGNO", "CTBAND"], dropna=False
        ).CTANNUAL.std()
        pairs = frs_household.set_index(["GVTREGNO", "CTBAND"])
        hh_CT_mean = CT_mean[pairs.index].values
        hh_CT_std = CT_std[pairs.index].values
        ct = np.random.randn(len(pairs)) * hh_CT_std + hh_CT_mean
        household = frs_household.fillna(0).add_prefix("H_")
        household.H_CTANNUAL = np.where(
            household.H_CTANNUAL == 0, ct, household.H_CTANNUAL
        )
        average_CT = household.H_CTANNUAL.dropna().mean()
        household.fillna(average_CT, inplace=True)

        raw_frs_files.close()

        # store dataset for future use
        year = int(year)

        with h5py.File(
            BaseFRS.data_dir / BaseFRS.filename(year), mode="w"
        ) as f:
            for variable in person.columns:
                f[f"{variable}/{year}"] = person[variable].values
            for variable in benunit.columns:
                f[f"{variable}/{year}"] = benunit[variable].values
            for variable in household.columns:
                f[f"{variable}/{year}"] = household[variable].values
