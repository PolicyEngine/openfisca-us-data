from openfisca_us_data import RawCPS, BaseCPS

if 2020 not in RawCPS.years:
    RawCPS.generate(2020)
BaseCPS.generate(2020)


def test_income_variables():
    from openfisca_us import Microsimulation

    sim = Microsimulation(dataset=BaseCPS)

    assert 8e13 < sim.calc("e00200", period=2020).sum() < 1e13
