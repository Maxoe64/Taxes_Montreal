"""
Taxes secondaires du conseil municipal :
- Taxe relative au financement de la contribution à l'ARTM
- Taxe relative à la voirie

Ces taxes suivent la même logique que la taxe foncière générale
(taux variés par catégorie, taux différenciés pour le non résidentiel).
"""

import numpy as np

from openfisca_core.periods import YEAR
from openfisca_core.variables import Variable

from openfisca_country_template.entities import Household

from openfisca_montreal.variables.immeuble import CategorieImmeuble


class taxe_artm(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = (
        "Montant annuel de la taxe relative au financement "
        "de la contribution à l'ARTM"
    )
    unit = "currency-CAD"
    reference = [
        "https://montreal.ca/articles/taux-de-taxes-pour-2026-106147"
    ]

    def formula(household, period, parameters):
        base = household("base_imposition", period)
        categorie = household("categorie_immeuble", period)

        p = parameters(period).taxes_foncieres.conseil_municipal.taxe_artm
        seuil = parameters(period).taxes_foncieres.seuils.seuil_non_residentiel

        # Résidentiel
        montant_res = base * p.residentiel / 100

        # Non résidentiel (taux différenciés)
        t1 = np.minimum(base, seuil)
        t2 = np.maximum(base - seuil, 0)
        montant_nr = t1 * p.non_residentiel_tranche_1 / 100 + t2 * p.non_residentiel_tranche_2 / 100

        # Terrain vague
        montant_tv = base * p.terrain_vague_desservi / 100

        is_res = (
            (categorie == CategorieImmeuble.residentiel)
            + (categorie == CategorieImmeuble.residentiel_6_plus)
        )
        is_nr = (categorie == CategorieImmeuble.non_residentiel)
        is_tv = (categorie == CategorieImmeuble.terrain_vague_desservi)

        return np.select(
            [is_res, is_nr, is_tv],
            [montant_res, montant_nr, montant_tv],
            default=montant_res,
        )


class taxe_voirie(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Montant annuel de la taxe relative à la voirie"
    unit = "currency-CAD"
    reference = [
        "https://montreal.ca/articles/taux-de-taxes-pour-2026-106147"
    ]

    def formula(household, period, parameters):
        base = household("base_imposition", period)
        categorie = household("categorie_immeuble", period)

        p = parameters(period).taxes_foncieres.conseil_municipal.taxe_voirie

        # Résidentiel
        montant_res = base * p.residentiel / 100

        # Non résidentiel (même taux pour les deux tranches)
        montant_nr = base * p.non_residentiel / 100

        # Terrain vague
        montant_tv = base * p.terrain_vague_desservi / 100

        is_res = (
            (categorie == CategorieImmeuble.residentiel)
            + (categorie == CategorieImmeuble.residentiel_6_plus)
        )
        is_nr = (
            (categorie == CategorieImmeuble.non_residentiel)
            + (categorie == CategorieImmeuble.mixte)
        )
        is_tv = (categorie == CategorieImmeuble.terrain_vague_desservi)

        return np.select(
            [is_res, is_nr, is_tv],
            [montant_res, montant_nr, montant_tv],
            default=montant_res,
        )
