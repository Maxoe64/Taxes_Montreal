"""
Total des taxes foncières — synthèse de toutes les composantes.

total = taxe_fonciere_generale
      + taxe_artm
      + taxe_voirie
      + taxe_arrondissement (services + investissements + montant fixe)
"""

import numpy as np

from openfisca_core.periods import YEAR
from openfisca_core.variables import Variable

from openfisca_country_template.entities import Household


class total_taxes_foncieres(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Total annuel des taxes foncières municipales"
    unit = "currency-CAD"
    reference = [
        "https://montreal.ca/articles/comment-sont-calculees-les-taxes-municipales-8962"
    ]

    def formula(household, period, parameters):
        tfg = household("taxe_fonciere_generale", period)
        artm = household("taxe_artm", period)
        voirie = household("taxe_voirie", period)
        arr = household("taxe_arrondissement", period)

        return tfg + artm + voirie + arr


class total_taxes_foncieres_mensuel(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Estimation mensuelle des taxes foncières (total annuel / 12)"
    unit = "currency-CAD"

    def formula(household, period, parameters):
        total_annuel = household("total_taxes_foncieres", period)
        return total_annuel / 12
