# openfisca-us-data

This package allows users to store and load various US microdata sources for usage in `openfisca-us`, with different configurations (e.g. imputations between surveys).

## Installation

This package can be installed via `pip install openfisca-us-data` or `pip install git+https://github.com/policyengine/openfisca-us-data`.

## General framework

This package is designed to be simple to add new OpenFisca-US-compatible datasets. To add a new dataset:
1. Add a new Python module as a single file or folder with `__init__.py` (optional)
2. Create a class with the `@dataset` decorator (from `utils.py`)
3. Define a `generate(year)` method
4. Ensure the class is imported in `openfisca_us/__init__.py` and `openfisca_us/cli.py`

## Usage

All dataset classes can be imported from the package, and there is also a command line interface:
```console
openfisca-us-data [dataset_name] [method] [arg1] [arg2]
```
For example (doesn't work yet):
```console
openfisca-us-data cps generate 2019 cps.csv.gz
```

## The `dataset` class decorator

This package uses a class decorator to ensure all datasets have the same loading/saving/querying interface. To use it, use the `@` symbol:
```python
@dataset
class CustomDataset:
    input_reform_from_year: Callable[int -> Reform]
    def generate(year):
        ...
    ...
```

## Current datasets

### RawCPS
- Not OpenFisca-US-compatible
- Contains the tables from the raw microdata
### CPS
- OpenFisca-US-compatible
- Contains OpenFisca-US-compatible input arrays.
### RawACS
- Not OpenFisca-US-compatible
- Contains the tables from the raw [ACS SPM research file](https://www.census.gov/data/datasets/time-series/demo/supplemental-poverty-measure/acs-research-files.html) microdata.
### ACS
- OpenFisca-US-compatible
- Contains OpenFisca-US-compatible input arrays.
