from openfisca_uk_data.utils import (
    MAIN_INPUT_VARIABLES,
    dataset,
    uprate_variables,
)
import synthimpute as si
import numpy as np
import h5py


@dataset
class FRS_SPI_Adjusted:
    name = "frs_spi_adj"
    openfisca_uk_compatible = True
    input_reform_from_year = uprate_variables(MAIN_INPUT_VARIABLES)

    def generate(year):
        from openfisca_uk import Microsimulation
        from openfisca_uk_data.datasets.frs.frs import FRS
        from openfisca_uk_data.datasets.spi import SPI

        frs_sim = Microsimulation(dataset=FRS)
        spi_sim = Microsimulation(dataset=SPI)

        spi_earnings_and_interest = np.array(
            [
                spi_sim.calc("employment_income", year).values,
                spi_sim.calc("savings_interest_income", year).values,
                spi_sim.calc("age", year).values,
            ]
        ).T
        frs_earnings_and_interest = np.array(
            [
                frs_sim.calc("employment_income", year).values,
                frs_sim.calc("savings_interest_income", year).values,
                frs_sim.calc("age", year).values,
            ]
        ).T
        spi_dividend_income = spi_sim.calc("dividend_income", year).values
        spi_weight = spi_sim.calc("person_weight", year).values
        print(
            "Imputing dividend income for FRS respondents from SPI values...",
            end="",
        )
        imputed_dividend_income = si.rf_impute(
            x_train=spi_earnings_and_interest,
            y_train=spi_dividend_income,
            x_new=frs_earnings_and_interest,
            sample_weight_train=spi_weight,
            mean_quantile=0.18,
        )
        print(" completed.")
        imputed_dividend_income *= (
            frs_sim.calc("dividend_income", year).values > 0
        )
        frs_sim.simulation.set_input(
            "dividend_income", year, imputed_dividend_income
        )
        with h5py.File(
            FRS_SPI_Adjusted.data_dir / FRS_SPI_Adjusted.filename(year), "w"
        ) as f:
            for variable in MAIN_INPUT_VARIABLES:
                f[f"{variable}/{year}"] = frs_sim.calc(variable, year).values
