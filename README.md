# openfisca-uk-data

This package allows users to store and load various UK microdata sources for usage in `openfisca-uk`, with different configurations (e.g. imputations between surveys).

## What you probably want to do

To get this package working for OpenFisca-UK without access to the UKDA:
1. Download `synth_frs_2018.h5`
2. `openfisca-uk-data synth_frs save synth_frs_2018.h5`

To get this package working with the FRS microdata:
1. Have the TAB .zip file ready (8633~~~.zip)
2. `openfisca-uk-data raw_frs generate 2018 8633~~~.zip`
3. `openfisca-uk-data frs generate 2018`

## General framework

This package is designed to be simple to add new OpenFisca-UK-compatible datasets. To add a new dataset:
1. Add a new Python module as a single file or folder with `__init__.py` (optional)
2. Create a class with the `@dataset` decorator (from `utils.py`)
3. Define a `generate(year)` method
4. Ensure the class is imported in `openfisca_uk/__init__.py` and `openfisca_uk/cli.py`

## Usage

All dataset classes can be imported from the package, and there is also a command line interface:
```console
openfisca-uk-data [dataset_name] [method] [arg1] [arg2]
```
For example:
```console
openfisca-uk-data raw_frs generate 2018 data.zip
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

### RawFRS
- Not OpenFisca-UK-compatible
- Contains the tables from the raw microdata
### BaseFRS
- OpenFisca-UK-compatible
- Loads the named survey variables, and specifies how these should be transformed into the model's input variables using OpenFisca formulas
### FRS
- OpenFisca-UK-compatible
- Skips loading the named survey variables like BaseFRS, instead loading the calculated input variables from using BaseFRS
### SPI
- OpenFisca-UK-compatible
- Admin tax data
### SynthFRS
- OpenFisca-UK-compatible
- Inaccurate but gives ballpark-correct results without access to the full FRS (fields shuffled + random noise added)