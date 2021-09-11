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
    from openfisca_uk.tools.general import where

    class tax_unit_weight(Variable):
        value_type = float
        entity = TaxUnit
        label = u"Tax unit weight"
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            # Tax unit weight is the weight of the containing family
            return tax_unit.value_from_first_person(
                tax_unit.members.family.project(
                    tax_unit.members.family("family_weight", period)
                )
            )

    class e00200(Variable):
        value_type = float
        entity = Person
        label = u"Wage and salary"
        definition_period = YEAR

        def formula(person, period, parameters):
            return person("P_WSAL_VAL", period)

    class interest(Variable):
        value_type = float
        entity = Person
        label = u"Interest income"
        definition_period = YEAR

        def formula(person, period):
            return person("P_INT_VAL", period)

    class e00900(Variable):
        value_type = float
        entity = Person
        label = u"Self-employment income"
        definition_period = YEAR

        def formula(person, period, parameters):
            return person("P_SEMP_VAL", period)

    class e02100(Variable):
        value_type = float
        entity = Person
        label = u"label"
        definition_period = YEAR

        def formula(person, period, parameters):
            return person("P_FRSE_VAL", period)

    class divs(Variable):
        value_type = float
        entity = Person
        label = u"label"
        definition_period = YEAR

        def formula(person, period, parameters):
            return person("P_DIV_VAL", period)

    class rents(Variable):
        value_type = float
        entity = Person
        label = u"label"
        definition_period = YEAR

        def formula(person, period, parameters):
            return person("P_RNT_VAL", period)

    class e01500(Variable):
        value_type = float
        entity = Person
        label = u"label"
        definition_period = YEAR

        def formula(person, period, parameters):
            other_inc_type = person("P_OI_OFF", period)
            has_private_pensions = other_inc_type == 2
            has_annuities = other_inc_type == 13
            other_inc = person("P_OI_VAL", period)
            return (has_private_pensions | has_annuities) * other_inc

    class e00800(Variable):
        value_type = float
        entity = Person
        label = u"label"
        definition_period = YEAR

        def formula(person, period, parameters):
            has_alimony = person("P_OI_OFF", period) == 20
            return has_alimony * person("P_OI_VAL", period)

    class e02400(Variable):
        value_type = float
        entity = Person
        label = u"label"
        definition_period = YEAR

        def formula(person, period, parameters):
            return person("P_SS_VAL", period)

    class e02300(Variable):
        value_type = float
        entity = Person
        label = u"label"
        definition_period = YEAR

        def formula(person, period, parameters):
            return person("P_UC_VAL", period)

    return [
        tax_unit_weight,
        e00200,
        interest,
        e00900,
        e02100,
        divs,
        rents,
        e01500,
        e00800,
        e02400,
        e02300,
    ]


def from_BaseCPS(year: int = 2020):
    class reform(Reform):
        def apply(self):
            for var in get_CPS_variables():
                self.add_variable(var)
            for var in get_input_variables():
                self.update_variable(var)

    return reform
