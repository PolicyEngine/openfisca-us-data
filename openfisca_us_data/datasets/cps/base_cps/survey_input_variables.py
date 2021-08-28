def get_CPS_variables():
    from openfisca_core.model_api import Variable, YEAR
    from openfisca_us.entities import Person

    class P_INT_VAL(Variable):
        value_type = float
        entity = Person
        label = u"Edited total combined interest income"
        definition_period = YEAR

    class P_RTM_VAL(Variable):
        value_type = float
        entity = Person
        label = u"wahtever the raw data column is"
        definition_period = YEAR

    CPS_variables = [P_INT_VAL]

    return CPS_variables
