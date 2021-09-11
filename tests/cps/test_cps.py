from openfisca_us_data import RawCPS, BaseCPS

if 2020 not in RawCPS.years:
    RawCPS.generate(2020)
BaseCPS.generate(2020)


def test_income_variables():
    from openfisca_us import Microsimulation

    sim = Microsimulation()

    print(sim.calc("interest").sum())
