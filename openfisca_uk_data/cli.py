from argparse import ArgumentParser
from openfisca_uk_data import (
    RawFRS,
    BaseFRS,
    FRS,
    SynthFRS,
    RawSPI,
    BaseSPI,
    SPI,
    FRS_SPI_Adjusted,
)


def main():
    datasets = {
        ds.name: ds
        for ds in (
            RawFRS,
            BaseFRS,
            FRS,
            SynthFRS,
            RawSPI,
            BaseSPI,
            SPI,
            FRS_SPI_Adjusted,
        )
    }
    parser = ArgumentParser(
        description="A utility for storing OpenFisca-UK-compatible microdata."
    )
    parser.add_argument("dataset", help="The dataset to select")
    parser.add_argument("action", help="The action to take")
    parser.add_argument(
        "args", nargs="*", help="The arguments to pass to the function"
    )
    args = parser.parse_args()
    try:
        return getattr(datasets[args.dataset], args.action)(*args.args)
    except Exception as e:
        print(f"Encountered an error: {e.with_traceback()}")


if __name__ == "__main__":
    main()
