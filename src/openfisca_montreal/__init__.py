"""
OpenFisca Montréal — Extension pour les taxes foncières municipales.

Encode les règles de taxation foncière de la Ville de Montréal,
incluant la taxe foncière générale, la taxe ARTM, la taxe de voirie,
les taxes d'arrondissement (19 arrondissements) et la mesure d'étalement.

Source réglementaire :
- Budget de fonctionnement 2026, Ville de Montréal
- Taux de taxes 2026 (conseil municipal et arrondissements)
- Rôle d'évaluation foncière 2026-2027-2028

Licence : AGPL-3.0
"""

import os

from openfisca_country_template import CountryTaxBenefitSystem

COUNTRY_DIR = os.path.dirname(os.path.abspath(__file__))


class MontrealTaxBenefitSystem(CountryTaxBenefitSystem):
    """Système de taxes foncières de Montréal, extension de country-template."""

    def __init__(self):
        super().__init__()
        self.load_extension(COUNTRY_DIR)
