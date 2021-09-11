from openfisca_us_data import CPS

if 2020 not in CPS.years:
    CPS.generate(2020)


def test_income_variables():
    from openfisca_us import Microsimulation

    sim = Microsimulation(dataset=CPS)

    assert 8e12 < sim.calc("e00200", period=2020).sum() < 1e13
