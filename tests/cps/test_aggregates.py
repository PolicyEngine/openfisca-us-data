from openfisca_us_data import CPS, REPO
from openfisca_us import Microsimulation
import pytest
import yaml
import pandas as pd
from itertools import product

MAX_REL_ERROR = 0.05
YEARS = (2020,)
VARIABLES = (
    "e00200",
    "e00900",
    "e02400",
    "e02300",
    "e01500",
    "e00800",
)
with open(REPO.parent / "tests" / "cps" / "taxcalc_cps.yml", "r") as f:
    tc = yaml.load(f)
sims = {}


@pytest.mark.dependency(name="dataset")
@pytest.mark.parametrize("year", (2020,))
def test_dataset_generates(year):
    CPS.generate(year)


@pytest.mark.dependency(depends=["dataset"])
@pytest.mark.parametrize("year", (2020,))
def test_openfisca_us_compatible(year):
    from openfisca_us import Microsimulation

    Microsimulation(dataset=CPS, year=year)


@pytest.mark.dependency(depends=["dataset"])
@pytest.mark.parametrize("year,variable", product(YEARS, VARIABLES))
def test_agg_against_taxcalc(year, variable):
    if year not in sims:
        sims[year] = Microsimulation(dataset=CPS, year=year)
    result = sims[year].calc(variable).sum()
    target = tc[variable][year]
    assert abs(result / target) < MAX_REL_ERROR


def _get_taxcalc_aggregates(
    cps_csv: str, cps_weights_csv: str
) -> pd.DataFrame:
    cps, weights = [
        pd.read_csv(file, compression="gzip")
        for file in (cps_csv, cps_weights_csv)
    ]
    aggregates = pd.DataFrame(
        {
            year: [
                (cps[column] * weights[f"WT{year}"]).sum() for column in cps
            ]
            for year in YEARS
        }
    )
    return aggregates
