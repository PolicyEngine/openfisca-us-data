# openfisca-us-data

This package provides utilities for storing and retrieving various US microdata sources for usage
in `openfisca-us`, with different configurations (e.g. imputations between surveys). All data is
stored and loaded in HDF5 format.

## Installation

This package can be installed via `pip install openfisca-us-data` or `pip install git+https://github.com/policyengine/openfisca-us-data`.

## General framework

This package is designed to be simple to add new OpenFisca-US-compatible datasets. To add a new dataset:
1. Add a new Python module as a single file or folder with `__init__.py` (optional)
2. Create a class with the `@dataset` decorator (from `utils.py`)
3. Define a `generate(year)` method
4. Ensure the class is imported in `openfisca_us/__init__.py` and `openfisca_us/cli.py`

## Usage

### Command Line Interface

All dataset classes can be imported from the package, and there is also a command line interface:
```console
openfisca-us-data [dataset_name] [method] [arg1] [arg2]
```
For example (doesn't work yet):
```console
openfisca-us-data cps generate 2019 cps.csv.gz
```

### Scripting
```
my_acs = ACS()
my_acs.generate(2016)  # retrieves the data
```

After successful running of the command above, the data has been stored. The `data_dir` property
shows where:
```
my_acs.data_dir
PosixPath('/mnt/c/devl/openfisca-us-data/openfisca_us_data/microdata/openfisca_us')
```

If you look inside, there's a auto-generated README file and an `acs_2016.hf file.
Note that it's 196 MB, so it contains some data. We can load that data (still in HDF5 format)
with the `load()` method.

```
acs_hd5 = my_acs.load(2016)

# h5py.File "acts like a Python dictionary" (https://docs.h5py.org/en/stable/quick.html)

list(acs_hd5.keys())

df1 = acs_hd5["SPM_unit_net_income"]
df2 = acs_hd5["person_weight"]

# Now we have an HDF5 dataset (These all appear to be vectors
df1.shape
df1[1:5]

pd.DataFrame(np.array(df1))
```
Note that at this point, you may quit the session and restart, and the data will still be saved:

```
my_acs = ACS()
acs_hd5 = my_acs.load(2016)

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
