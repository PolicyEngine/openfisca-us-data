from openfisca_us_data.utils import *
import requests
from io import BytesIO
import pandas as pd


@dataset
class RawACS:
    name = "raw_acs"

    def generate(self, year: int):
        try:
            url = f"https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_pu_{year}.sas7bdat"
            response = requests.get(url, stream=True)
            total_size_in_bytes = int(
                response.headers.get("content-length", 200e6)
            )
            progress_bar = tqdm(
                total=total_size_in_bytes,
                unit="iB",
                unit_scale=True,
                desc="Downloading ACS SPM research file",
            )
        except Exception as e:
            raise FileNotFoundError(
                f"Attempted to download the ACS SPM research file for {year}, but encountered an error: {e.with_traceback()}"
            )
        try:
            with BytesIO() as file, pd.HDFStore(RawCPS.file(year)) as storage:
                content_length_actual = 0
                for data in response.iter_content(int(1e6)):
                    progress_bar.update(len(data))
                    content_length_actual += len(data)
                    file.write(data)
                progress_bar.set_description("Downloaded ACS SPM research file")
                progress_bar.total = content_length_actual
                progress_bar.close()
                storage["person"] = person = pd.read_sas(file).fillna(0)
                storage["spm_unit"] = create_SPM_unit_table(person)
                storage["household"] = create_household_table(person)
        except Exception as e:
            raise ValueError(
                f"Attempted to extract and save the CSV files, but encountered an error: {e.with_traceback()}"
            )


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


def create_household_table(person: pd.DataFrame) -> pd.DataFrame:
    return person[["SERIALNO", "st", "PUMA"]].groupby(person.SERIALNO).first()
