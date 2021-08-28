from openfisca_us_data.datasets.cps.base_cps.survey_input_variables import (
    get_CPS_variables,
)
from openfisca_core.model_api import Variable, YEAR, Reform


def get_input_variables():
    from openfisca_us.entities import (
        Person,
        TaxUnit,
        Household,
        Family,
        SPMUnit,
    )

    class interest_income(Variable):
        value_type = float
        entity = Person
        label = u"Interest income"
        definition_period = YEAR

        def formula(person, period):
            return person("P_INT_VAL", period)

    input_variables = [interest_income]

    return input_variables


def from_BaseCPS(year: int = 2020):
    class reform(Reform):
        def apply(self):
            for var in get_CPS_variables():
                self.add_variable(var)
            for var in get_input_variables():
                self.update_variable(var)

    return reform
