"""
Variables d'entrée décrivant un immeuble à Montréal.

Ce module définit les Enums pour les catégories d'immeubles et les
arrondissements, ainsi que les variables d'entrée nécessaires au calcul
des taxes foncières.
"""

from numpy import datetime64

from openfisca_core.indexed_enums import Enum
from openfisca_core.periods import YEAR
from openfisca_core.variables import Variable

from openfisca_country_template.entities import Household


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class CategorieImmeuble(Enum):
    """
    Catégories d'immeubles reconnues par la Ville de Montréal.

    Source: Comment sont calculées les taxes municipales, Ville de Montréal.
    https://montreal.ca/articles/comment-sont-calculees-les-taxes-municipales-8962
    """

    residentiel = "Résidentiel (≤ 5 logements)"
    residentiel_6_plus = "Résidentiel (6 logements ou plus)"
    non_residentiel = "Non résidentiel / commercial"
    mixte = "Mixte (partie résidentielle + non résidentielle)"
    terrain_vague_desservi = "Terrain vague desservi"


class Arrondissement(Enum):
    """
    Les 19 arrondissements de la Ville de Montréal.

    Chaque arrondissement impose ses propres taux de taxe
    (services et investissements).
    """

    ahuntsic_cartierville = "Ahuntsic-Cartierville"
    anjou = "Anjou"
    cote_des_neiges_ndg = "Côte-des-Neiges–Notre-Dame-de-Grâce"
    ile_bizard_sainte_genevieve = "L'Île-Bizard–Sainte-Geneviève"
    lachine = "Lachine"
    lasalle = "LaSalle"
    le_plateau_mont_royal = "Le Plateau-Mont-Royal"
    le_sud_ouest = "Le Sud-Ouest"
    mercier_hochelaga_maisonneuve = "Mercier–Hochelaga-Maisonneuve"
    montreal_nord = "Montréal-Nord"
    outremont = "Outremont"
    pierrefonds_roxboro = "Pierrefonds-Roxboro"
    riviere_des_prairies_pat = "Rivière-des-Prairies–Pointe-aux-Trembles"
    rosemont_la_petite_patrie = "Rosemont–La Petite-Patrie"
    saint_laurent = "Saint-Laurent"
    saint_leonard = "Saint-Léonard"
    verdun = "Verdun"
    ville_marie = "Ville-Marie"
    villeray_saint_michel_parc_extension = "Villeray–Saint-Michel–Parc-Extension"


# ---------------------------------------------------------------------------
# Variables d'entrée (input variables)
# ---------------------------------------------------------------------------


class categorie_immeuble(Variable):
    value_type = Enum
    possible_values = CategorieImmeuble
    default_value = CategorieImmeuble.residentiel
    entity = Household
    definition_period = YEAR
    label = "Catégorie de l'immeuble selon la classification de Montréal"
    reference = [
        "https://montreal.ca/articles/comment-sont-calculees-les-taxes-municipales-8962"
    ]


class arrondissement(Variable):
    value_type = Enum
    possible_values = Arrondissement
    default_value = Arrondissement.ville_marie
    entity = Household
    definition_period = YEAR
    label = "Arrondissement dans lequel se situe l'immeuble"
    reference = [
        "https://montreal.ca/arrondissements"
    ]


class valeur_fonciere_role_precedent(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    default_value = 0
    label = "Valeur inscrite au rôle d'évaluation foncière précédent (2023-2025)"
    unit = "currency-CAD"
    reference = [
        "https://montreal.ca/articles/comment-sont-calculees-les-taxes-municipales-8962"
    ]


class valeur_fonciere_role_courant(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    default_value = 0
    label = "Valeur inscrite au rôle d'évaluation foncière en vigueur (2026-2028)"
    unit = "currency-CAD"
    reference = [
        "https://montreal.ca/articles/comment-sont-calculees-les-taxes-municipales-8962"
    ]


class annee_role(Variable):
    value_type = int
    entity = Household
    definition_period = YEAR
    default_value = 1
    label = (
        "Année dans le cycle du rôle triennal (1, 2 ou 3). "
        "Année 1 = 2026, Année 2 = 2027, Année 3 = 2028."
    )
    reference = [
        "https://montreal.ca/articles/comment-sont-calculees-les-taxes-municipales-8962"
    ]


class proportion_non_residentielle(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    default_value = 0
    label = (
        "Pour les immeubles mixtes, proportion de la valeur attribuable "
        "à la partie non résidentielle (entre 0 et 1)"
    )
