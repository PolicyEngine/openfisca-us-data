from pathlib import Path
from typing import List
from openfisca_uk_data.utils import dataset
import pandas as pd
import shutil
from openfisca_uk_data.utils import DATA_DIR, safe_rmdir, data_folder
import re
from tqdm import tqdm
import h5py
import numpy as np
import warnings


@dataset
class RawFRS:
    name = "raw_frs"
    openfisca_uk_compatible = False

    def generate(year, zipfile) -> None:
        folder = Path(zipfile)
        year = str(year)

        if not folder.exists():
            raise FileNotFoundError("Invalid path supplied.")

        new_folder = RawFRS.data_dir / "tmp"
        shutil.unpack_archive(folder, new_folder)
        folder = new_folder

        main_folder = next(folder.iterdir())
        tab_folder = main_folder / "tab"
        if tab_folder.exists():
            criterion = re.compile("[a-z]+\.tab")
            data_files = [
                path
                for path in tab_folder.iterdir()
                if criterion.match(path.name)
            ]
            task = tqdm(data_files, desc="Saving raw data tables")
            with pd.HDFStore(RawFRS.data_dir / RawFRS.filename(year)) as file:
                for filepath in task:
                    task.set_description(
                        f"Saving raw data tables ({filepath.name})"
                    )
                    table_name = filepath.name.replace(".tab", "")
                    df = pd.read_csv(
                        filepath, delimiter="\t", low_memory=False
                    ).apply(pd.to_numeric, errors="coerce")
                    if "PERSON" in df.columns:
                        df["person_id"] = (
                            df.sernum * 1e2 + df.BENUNIT * 1e1 + df.PERSON
                        )
                    if "BENUNIT" in df.columns:
                        df["benunit_id"] = df.sernum * 1e2 + df.BENUNIT * 1e1
                    if "sernum" in df.columns:
                        df["household_id"] = df.sernum * 1e2
                    file[table_name] = df
        else:
            raise FileNotFoundError("Could not find the TAB files.")

        tmp_folder = RawFRS.data_dir / "tmp"
        if tmp_folder.exists():
            safe_rmdir(tmp_folder)
