from openfisca_us_data import CE


def test_ce_from_2019():
    """Test the Consumer Expenditure data generating functions for 2019"""
    ce = CE()
    ce.generate(2019)
    ce_2019 = ce.load(2019)

    assert(len(set(ce_2019.keys()).intersection({"annual", "household"})) == 2)

    # Test household average demographic estimate -------------------------
    est_income_bf_tax = ce_2019["/annual/income_before_tax"][()]
    assert(round(est_income_bf_tax) == 82743)

    # Test household average expenditure estimate -------------------------
    est_alcohol_expense = ce_2019["/annual/alcohol"][()]
    assert(round(est_alcohol_expense) == 536)

    # Test Household Sector CO2 emissions are "in the ballpark" -----
    est_co2_kg_per_hh = ce_2019["/annual/co2_kg"][()]
    hhs_in_us = 122.8E6
    kg_per_metric_ton = 1000
    est_total_tons_co2 = est_co2_kg_per_hh * hhs_in_us / kg_per_metric_ton
    assert(round(est_total_tons_co2 / 1E9) > 2)
    assert(round(est_total_tons_co2 / 1E9) < 6)

    # Test Household Sector CO2 emissions are "in the ballpark" -----
    hh_keys = {"demographics", "emissions", "expenditures", "survey"}
    assert(len(set(ce_2019["/household"].keys()).intersection(hh_keys)) == 4)

    hh_co2_emissions = ce_2019["/household/emissions/co2_kg"][:]
    assert(len(hh_co2_emissions) == 26903)
