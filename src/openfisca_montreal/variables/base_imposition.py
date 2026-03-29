"""
Base d'imposition — calcul avec mesure d'étalement.

La Ville de Montréal lisse sur 3 ans la différence de valeur entre
le rôle précédent et le rôle en vigueur : un tiers de la variation
est appliqué chaque année.

Exemple (source: montreal.ca):
  Rôle 2023-2025 : 560 000 $
  Rôle 2026-2028 : 620 000 $
  Variation      :  60 000 $

  Base 2026 (année 1) : 560 000 + (1/3 × 60 000) = 580 000 $
  Base 2027 (année 2) : 560 000 + (2/3 × 60 000) = 600 000 $
  Base 2028 (année 3) : 560 000 + (3/3 × 60 000) = 620 000 $
"""

import numpy as np

from openfisca_core.periods import YEAR
from openfisca_core.variables import Variable

from openfisca_country_template.entities import Household


class base_imposition(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = (
        "Base d'imposition après application de la mesure d'étalement. "
        "C'est la valeur utilisée pour calculer les taxes."
    )
    unit = "currency-CAD"
    reference = [
        "https://montreal.ca/articles/comment-sont-calculees-les-taxes-municipales-8962"
    ]

    def formula(household, period, parameters):
        """
        Calcule la base d'imposition en appliquant l'étalement triennal.

        base = valeur_precedent + (annee_role / 3) × (valeur_courant - valeur_precedent)

        Si annee_role n'est pas entre 1 et 3, on utilise la valeur courante
        intégrale (pas d'étalement).
        """
        val_precedent = household("valeur_fonciere_role_precedent", period)
        val_courant = household("valeur_fonciere_role_courant", period)
        annee = household("annee_role", period)

        # Clamp annee_role entre 1 et 3
        annee_clamped = np.clip(annee, 1, 3)

        variation = val_courant - val_precedent
        base = val_precedent + (annee_clamped / 3.0) * variation

        return base
