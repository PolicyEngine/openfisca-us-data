from pathlib import Path
import shutil

def data_folder(path: str, erase=False) -> Path:
    folder = Path(path)
    folder.mkdir(exist_ok=True, parents=True)
    if erase:
        shutil.rmtree(folder)
        folder.mkdir()
    return folder