from openfisca_us_data.utils import *
import requests
from io import BytesIO
from zipfile import ZipFile
import pandas as pd


@dataset
class RawCPS:
    name = "raw_cps"

    def generate(year: int) -> None:
        # Files are named for a year after the year the survey represents.
        # For example, the 2020 CPS was administered in March 2021, so it's
        # named 2021.
        file_year = int(year) + 1
        file_year_code = str(file_year)[-2:]
        url = f"https://www2.census.gov/programs-surveys/cps/datasets/{file_year}/march/asecpub{file_year_code}csv.zip"
        response = requests.get(url, stream=True)
        total_size_in_bytes = int(
            response.headers.get("content-length", 200e6)
        )
        progress_bar = tqdm(
            total=total_size_in_bytes,
            unit="iB",
            unit_scale=True,
            desc="Downloading ASEC",
        )
        if response.status_code == 404:
            raise FileNotFoundError(
                "Received a 404 response when fetching the data."
            )
        try:
            with BytesIO() as file, pd.HDFStore(
                RawCPS.file(year), mode="w"
            ) as storage:
                content_length_actual = 0
                for data in response.iter_content(int(1e6)):
                    progress_bar.update(len(data))
                    content_length_actual += len(data)
                    file.write(data)
                progress_bar.set_description("Downloaded ASEC")
                progress_bar.total = content_length_actual
                progress_bar.close()
                zipfile = ZipFile(file)
                with zipfile.open(f"pppub{file_year_code}.csv") as f:
                    storage["person"] = person = pd.read_csv(f).fillna(0)
                with zipfile.open(f"ffpub{file_year_code}.csv") as f:
                    person_family_id = person.PH_SEQ * 10 + person.PF_SEQ
                    family = pd.read_csv(f).fillna(0)
                    family_id = family.FH_SEQ * 10 + family.FFPOS
                    family = family[family_id.isin(person_family_id)]
                    storage["family"] = family
                with zipfile.open(f"hhpub{file_year_code}.csv") as f:
                    person_household_id = person.PH_SEQ
                    household = pd.read_csv(f).fillna(0)
                    household_id = household.H_SEQ
                    household = household[
                        household_id.isin(person_household_id)
                    ]
                    storage["household"] = household
                storage["tax_unit"] = create_tax_unit_table(person)
                storage["spm_unit"] = create_SPM_unit_table(person)
        except Exception as e:
            RawCPS.remove(year)
            raise ValueError(
                f"Attempted to extract and save the CSV files, but encountered an error: {e}"
            )


def create_tax_unit_table(person: pd.DataFrame) -> pd.DataFrame:
    TAX_UNIT_COLUMNS = [
        "ACTC_CRD",
        "AGI",
        "CTC_CRD",
        "EIT_CRED",
        "FED_RET",
        "FEDTAX_AC",
        "FEDTAX_BC",
        "MARG_TAX",
        "STATETAX_A",
        "STATETAX_B",
        "TAX_INC",
        "TAX_ID",
    ]
    return person[TAX_UNIT_COLUMNS].groupby(person.TAX_ID).sum()


def create_SPM_unit_table(person: pd.DataFrame) -> pd.DataFrame:
    SPM_UNIT_COLUMNS = [
        "ACTC",
        "CAPHOUSESUB",
        "CAPWKCCXPNS",
        "CHILDCAREXPNS",
        "CHILDSUPPD",
        "EITC",
        "ENGVAL",
        "EQUIVSCALE",
        "FAMTYPE",
        "FEDTAX",
        "FEDTAXBC",
        "FICA",
        "GEOADJ",
        "HAGE",
        "HHISP",
        "HMARITALSTATUS",
        "HRACE",
        "MEDXPNS",
        "NUMADULTS",
        "NUMKIDS",
        "NUMPER",
        "POOR",
        "POVTHRESHOLD",
        "RESOURCES",
        "SCHLUNCH",
        "SNAPSUB",
        "STTAX",
        "TENMORTSTATUS",
        "TOTVAL",
        "WCOHABIT",
        "WEIGHT",
        "WFOSTER22",
        "WICVAL",
        "WKXPNS",
        "WNEWHEAD",
        "WNEWPARENT",
        "WUI_LT15",
        "ID",
    ]
    return (
        person[["SPM_" + column for column in SPM_UNIT_COLUMNS]]
        .groupby(person.SPM_ID)
        .first()
    )
