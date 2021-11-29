import requests
from io import BytesIO
from zipfile import ZipFile

import pandas as pd

from openfisca_us_data.utils import *


@dataset
class RawCE:
    """Raw data extractor class for the Consumer Expenditure Survey"""

    name = "raw_ce"

    def generate(year: int, revised_q1=True) -> None:
        """Save the Raw Consumer Expendure data in HDF5 format via PyTables"""
        file_year_code = str(year)[-2:]
        file_year_after_code = str(year + 1)[-2:]
        url = f"https://www.bls.gov/cex/pumd/data/comma/intrvw{file_year_code}.zip"

        response = requests.get(url, stream=True)
        total_size_in_bytes = int(response.headers.get("content-length", 200e6))
        progress_bar = tqdm(
            total=total_size_in_bytes,
            unit="iB",
            unit_scale=True,
            desc="Downloading CE Survey",
        )
        if response.status_code == 404:
            raise FileNotFoundError("Received a 404 response when fetching the data.")
        try:
            with BytesIO() as file, pd.HDFStore(RawCE.file(year), mode="w") as storage:
                content_length_actual = 0
                for data in response.iter_content(int(1e6)):
                    progress_bar.update(len(data))
                    content_length_actual += len(data)
                    file.write(data)
                progress_bar.set_description("Downloaded CE Survey Data")
                progress_bar.total = content_length_actual
                progress_bar.close()
                zipfile = ZipFile(file)
                q1_suffix = "x" if revised_q1 else ""

                dirstring = f"intrvw{file_year_code}/intrvw{file_year_code}"
                quarter_filenames = [
                    f"fmli{file_year_code}1{q1_suffix}",
                    f"fmli{file_year_code}2",
                    f"fmli{file_year_code}3",
                    f"fmli{file_year_code}4",
                    f"fmli{file_year_after_code}1",
                ]

                for quarter in range(1, 6):
                    filename = quarter_filenames[quarter - 1]
                    with zipfile.open(f"{dirstring}/{filename}.csv") as f:
                        q_df = pd.read_csv(f)
                        q_df.insert(0, "nominal_year", year)
                        q_df.insert(1, "nominal_quarter", quarter)
                        q_df.insert(
                            2, "cu_id", q_df["NEWID"].apply(lambda x: get_unit_id(x))
                        )
                        q_df.insert(
                            3,
                            "interview_id",
                            q_df["NEWID"].apply(lambda x: get_interview_id(x)),
                        )
                        q_df.insert(4, "interview_mo", q_df["QINTRVMO"])
                        q_df.insert(5, "interview_yr", q_df["QINTRVYR"])
                        q_df.insert(6, "weight", q_df["FINLWT21"])
                        storage[filename] = q_df

        except Exception as e:
            RawCE.remove(year)
            raise ValueError(
                "Attempted to extract and save the CSV files, "
                + f"but encountered an error: {e}"
            )


def get_unit_id(newid):
    """Extract the Consumer Unit from the NewId"""
    return int(str(newid)[:-1])


def get_interview_id(newid):
    """Extract the Interview Id from the NewId"""
    return int(str(newid)[-1])
