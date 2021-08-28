def test_cps_downloads():
    from openfisca_us_data import RawCPS

    RawCPS.generate(2020)
    assert RawCPS.file(2020).exists()
