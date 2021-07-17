from openfisca_uk_data.utils import dataset
from pathlib import Path
import shutil
from tqdm import tqdm
import pandas as pd


@dataset
class RawSPI:
    name = "raw_spi"
    openfisca_uk_compatible = False

    def generate(year, zipfile) -> None:
        folder = Path(zipfile)
        year = str(year)
        if not folder.exists():
            raise FileNotFoundError("Invalid path supplied")
        new_folder = RawSPI.data_dir / "tmp"
        shutil.unpack_archive(folder, new_folder)
        folder = new_folder
        main_folder = next(folder.iterdir())
        with pd.HDFStore(RawSPI.data_dir / RawSPI.filename(year)) as file:
            if (main_folder / "tab").exists():
                data_folder = main_folder / "tab"
                data_files = list(data_folder.glob("*.tab"))
                task = tqdm(data_files, desc="Saving data tables")
                for filepath in task:
                    task.set_description(f"Saving {filepath.name}")
                    table_name = "main"
                    df = pd.read_csv(
                        filepath, delimiter="\t", low_memory=False
                    ).apply(pd.to_numeric, errors="coerce")
                    file[table_name] = df
            else:
                raise FileNotFoundError("Could not find any TAB files.")

        # Clean up tmp storage.

        tmp_folder = RawSPI.data_dir / "tmp"
        if tmp_folder.exists():
            shutil.rmtree(tmp_folder)
