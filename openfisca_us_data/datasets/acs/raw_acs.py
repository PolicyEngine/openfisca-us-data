from openfisca_us_data.utils import *
import requests
from io import BytesIO
import pandas as pd
from zipfile import ZipFile

@dataset
class RawACS:
    name = "raw_acs"

    def generate(year: int) -> None:
        url = f"https://www2.census.gov/programs-surveys/acs/data/pums/{year}/1-Year/csv_pus.zip"
        request = requests.get(url)
        file = ZipFile(BytesIO(request.content))
        file.extractall(f'{year}_pus')

        url2 = 'https://www2.census.gov/programs-surveys/acs/data/pums/2019/1-Year/csv_hus.zip'
        request = requests.get(url2)
        file = ZipFile(BytesIO(request.content))
        file.extractall(f'{year}_hus')

        try:
            with pd.HDFStore(RawACS.file(year)) as storage:
                persona = pd.read_csv(f'{year}_pus/psam_pusa.csv')
                personb = pd.read_csv(f'{year}_pus/psam_pusb.csv')
                person_df = pd.concat(persona, personb).fillna(0)
                person_df.columns = person_df.columns.str.upper()

                householda = pd.read_csv(f'{year}_hus/psam_husa.csv')
                householdb = pd.read_csv(f'{year}_hus/psam_husa.csv')
                household_df = pd.concat(householda, householdb).fillna(0)
                household_df.columns = household_df.columns.str.upper()

        except Exception as e:
            RawACS.remove(year)
            raise ValueError(
                f"Attempted to extract and save the CSV files, but encountered an error: {e}"
            )