"""
Taxe foncière générale — principale composante du compte de taxes.

Les taux varient selon la catégorie d'immeuble.
Pour les immeubles non résidentiels, un système de taux différenciés
s'applique avec un seuil à 900 000 $ :
  - Tranche 1 : valeur ≤ 900 000 $
  - Tranche 2 : valeur > 900 000 $

Source: Budget 2026, Ville de Montréal
"""

import numpy as np

from openfisca_core.periods import YEAR
from openfisca_core.variables import Variable

from openfisca_country_template.entities import Household

from openfisca_montreal.variables.immeuble import CategorieImmeuble


class taxe_fonciere_generale(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Montant annuel de la taxe foncière générale"
    unit = "currency-CAD"
    reference = [
        "https://montreal.ca/articles/taux-de-taxes-pour-2026-106147",
        "https://montreal.ca/articles/comment-sont-calculees-les-taxes-municipales-8962",
    ]

    def formula(household, period, parameters):
        """
        Calcule la taxe foncière générale.

        Pour résidentiel: base × taux_residentiel / 100
        Pour non résidentiel:
          min(base, seuil) × taux_tranche_1 / 100
          + max(base - seuil, 0) × taux_tranche_2 / 100
        Pour terrain vague: base × taux_terrain_vague / 100
        """
        base = household("base_imposition", period)
        categorie = household("categorie_immeuble", period)
        proportion_nr = household("proportion_non_residentielle", period)

        p = parameters(period).taxes_foncieres.conseil_municipal.taxe_fonciere_generale
        seuil = parameters(period).taxes_foncieres.seuils.seuil_non_residentiel

        # Taux résidentiel
        taux_res = p.residentiel

        # Taux non résidentiel (tranches)
        taux_nr_1 = p.non_residentiel_tranche_1
        taux_nr_2 = p.non_residentiel_tranche_2

        # Taux terrain vague
        taux_tv = p.terrain_vague_desservi

        # --- Calcul résidentiel simple ---
        montant_residentiel = base * taux_res / 100

        # --- Calcul non résidentiel avec taux différenciés ---
        tranche_1 = np.minimum(base, seuil)
        tranche_2 = np.maximum(base - seuil, 0)
        montant_non_residentiel = (
            tranche_1 * taux_nr_1 / 100
            + tranche_2 * taux_nr_2 / 100
        )

        # --- Calcul terrain vague ---
        montant_terrain_vague = base * taux_tv / 100

        # --- Calcul mixte ---
        # Partie résidentielle + partie non résidentielle
        base_res_mixte = base * (1 - proportion_nr)
        base_nr_mixte = base * proportion_nr
        tranche_1_mixte = np.minimum(base_nr_mixte, seuil)
        tranche_2_mixte = np.maximum(base_nr_mixte - seuil, 0)
        montant_mixte = (
            base_res_mixte * taux_res / 100
            + tranche_1_mixte * taux_nr_1 / 100
            + tranche_2_mixte * taux_nr_2 / 100
        )

        # Sélection selon la catégorie
        result = np.select(
            [
                categorie == CategorieImmeuble.residentiel,
                categorie == CategorieImmeuble.residentiel_6_plus,
                categorie == CategorieImmeuble.non_residentiel,
                categorie == CategorieImmeuble.mixte,
                categorie == CategorieImmeuble.terrain_vague_desservi,
            ],
            [
                montant_residentiel,
                montant_residentiel,  # Même taux en 2026
                montant_non_residentiel,
                montant_mixte,
                montant_terrain_vague,
            ],
            default=montant_residentiel,
        )

        return result
