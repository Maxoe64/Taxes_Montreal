"""
Taxes d'arrondissement — services et investissements.

Chaque arrondissement fixe deux taux à taux unique (identique pour
toutes les catégories d'immeubles). Certains arrondissements ajoutent
un montant fixe par unité d'évaluation (ex: Lachine = 57,91 $).

Source: Budget 2026, taux d'arrondissements
"""

import numpy as np

from openfisca_core.periods import YEAR
from openfisca_core.variables import Variable

from openfisca_country_template.entities import Household

from openfisca_montreal.variables.immeuble import Arrondissement


class taxe_arrondissement(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = (
        "Montant annuel des taxes d'arrondissement "
        "(services + investissements + montant fixe)"
    )
    unit = "currency-CAD"
    reference = [
        "https://montreal.ca/articles/taux-de-taxes-pour-2026-106147"
    ]

    def formula(household, period, parameters):
        """
        Calcule le total des taxes d'arrondissement.

        Pour chaque arrondissement:
          taxe = base × (taux_services + taux_investissements) / 100
                 + montant_fixe
        """
        base = household("base_imposition", period)
        arr = household("arrondissement", period)

        p_arr = parameters(period).taxes_foncieres.arrondissements.taux_arrondissements

        # Table de correspondance: enum → (taux_services, taux_investissements, montant_fixe)
        # On construit les tableaux de taux en itérant sur les arrondissements
        arrondissement_params = {
            Arrondissement.ahuntsic_cartierville: "ahuntsic_cartierville",
            Arrondissement.anjou: "anjou",
            Arrondissement.cote_des_neiges_ndg: "cote_des_neiges_ndg",
            Arrondissement.ile_bizard_sainte_genevieve: "ile_bizard_sainte_genevieve",
            Arrondissement.lachine: "lachine",
            Arrondissement.lasalle: "lasalle",
            Arrondissement.le_plateau_mont_royal: "le_plateau_mont_royal",
            Arrondissement.le_sud_ouest: "le_sud_ouest",
            Arrondissement.mercier_hochelaga_maisonneuve: "mercier_hochelaga_maisonneuve",
            Arrondissement.montreal_nord: "montreal_nord",
            Arrondissement.outremont: "outremont",
            Arrondissement.pierrefonds_roxboro: "pierrefonds_roxboro",
            Arrondissement.riviere_des_prairies_pat: "riviere_des_prairies_pat",
            Arrondissement.rosemont_la_petite_patrie: "rosemont_la_petite_patrie",
            Arrondissement.saint_laurent: "saint_laurent",
            Arrondissement.saint_leonard: "saint_leonard",
            Arrondissement.verdun: "verdun",
            Arrondissement.ville_marie: "ville_marie",
            Arrondissement.villeray_saint_michel_parc_extension: "villeray_saint_michel_parc_extension",
        }

        # Initialiser le résultat à zéro
        result = np.zeros_like(base)

        for enum_val, param_key in arrondissement_params.items():
            arr_data = getattr(p_arr, param_key)
            taux_services = arr_data.services
            montant_fixe = arr_data.montant_fixe

            # Gestion du cas spécial de L'Île-Bizard–Sainte-Geneviève
            # qui a deux taux d'investissements selon le secteur.
            # Par simplification, on utilise le taux L'Île-Bizard par défaut.
            if param_key == "ile_bizard_sainte_genevieve":
                taux_invest = arr_data.investissements_ile_bizard
            else:
                taux_invest = arr_data.investissements

            taux_total = taux_services + taux_invest
            montant = base * taux_total / 100 + montant_fixe

            mask = (arr == enum_val)
            result = np.where(mask, montant, result)

        return result
