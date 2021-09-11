def get_CPS_variables():
    from openfisca_core.model_api import Variable, YEAR
    from openfisca_us.entities import (
        Person,
        TaxUnit,
        Household,
        Family,
        SPMUnit,
    )

    class P_WSAL_VAL(Variable):
        value_type = float
        entity = Person
        label = u"Wage and salary"
        definition_period = YEAR

    class P_INT_VAL(Variable):
        value_type = float
        entity = Person
        label = u"Edited total combined interest income"
        definition_period = YEAR

    class P_SEMP_VAL(Variable):
        value_type = float
        entity = Person
        label = u"Self-employment income"
        definition_period = YEAR

    class P_FRSE_VAL(Variable):
        value_type = float
        entity = Person
        label = u"label"
        definition_period = YEAR

    class P_DIV_VAL(Variable):
        value_type = float
        entity = Person
        label = u"Dividends"
        definition_period = YEAR

    class P_RNT_VAL(Variable):
        value_type = float
        entity = Person
        label = u"Rent"
        definition_period = YEAR

    class P_RTM_VAL(Variable):
        value_type = float
        entity = Person
        label = u"label"
        definition_period = YEAR

    class P_OI_OFF(Variable):
        value_type = float
        entity = Person
        label = u"Type of other income source"
        definition_period = YEAR

    class P_OI_VAL(Variable):
        value_type = float
        entity = Person
        label = u"Other income amount"
        definition_period = YEAR

    class P_SS_VAL(Variable):
        value_type = float
        entity = Person
        label = u"Reported Social Security"
        definition_period = YEAR

    class P_UC_VAL(Variable):
        value_type = float
        entity = Person
        label = u"Reported unemployment benefits"
        definition_period = YEAR

    CPS_variables = [
        P_WSAL_VAL,
        P_INT_VAL,
        P_SEMP_VAL,
        P_FRSE_VAL,
        P_DIV_VAL,
        P_RNT_VAL,
        # P_RTM_VAL,
        P_OI_OFF,
        P_OI_VAL,
        P_SS_VAL,
        P_UC_VAL,
    ]

    return CPS_variables
