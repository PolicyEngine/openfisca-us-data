from openfisca_us_data.utils import *
import requests
from io import BytesIO
import pandas as pd


@dataset
class RawACS:
    name = "raw_acs"

    def generate(year: int) -> None:
        url = f"https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_pu_{year}.sas7bdat"
        response = requests.get(url, stream=True)
        total_size_in_bytes = int(
            response.headers.get("content-length", 1.2e9)
        )
        progress_bar = tqdm(
            total=total_size_in_bytes,
            unit="iB",
            unit_scale=True,
            desc="Downloading ACS SPM research file",
        )
        if response.status_code == 404:
            raise FileNotFoundError(
                "Received a 404 response when fetching the data."
            )
        try:
            with BytesIO() as file, pd.HDFStore(RawACS.file(year)) as storage:
                content_length_actual = 0
                for data in response.iter_content(int(1e6)):
                    progress_bar.update(len(data))
                    content_length_actual += len(data)
                    file.write(data)
                progress_bar.set_description(
                    "Downloaded ACS SPM research file"
                )
                progress_bar.total = content_length_actual
                progress_bar.close()
                person = pd.read_sas(file, format="sas7bdat")
                person = person.fillna(0)
                person.columns = person.columns.str.upper()
                storage["person"] = person
                storage["spm_unit"] = create_SPM_unit_table(person)
                storage["household"] = create_household_table(person)
        except Exception as e:
            RawACS.remove(year)
            raise ValueError(
                f"Attempted to extract and save the CSV files, but encountered an error: {e}"
            )


def create_SPM_unit_table(person: pd.DataFrame) -> pd.DataFrame:
    SPM_UNIT_COLUMNS = [
        "CAPHOUSESUB",
        "CAPWKCCXPNS",
        "CHILDCAREXPNS",
        "EITC",
        "ENGVAL",
        "EQUIVSCALE",
        "FEDTAX",
        "FEDTAXBC",
        "FICA",
        "GEOADJ",
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
        "WICVAL",
        "WKXPNS",
        "WUI_LT15",
        "ID",
    ]
    return (
        person[["SPM_" + column for column in SPM_UNIT_COLUMNS]]
        .groupby(person.SPM_ID)
        .first()
    )


def create_household_table(person: pd.DataFrame) -> pd.DataFrame:
    return person[["SERIALNO", "ST", "PUMA"]].groupby(person.SERIALNO).first()
