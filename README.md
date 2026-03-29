# OpenFisca Montréal — Simulateur de taxes foncières

Extension [OpenFisca](https://openfisca.org/) qui encode les règles de taxation
foncière de la Ville de Montréal en code exécutable (*Rules as Code*).

## Qu'est-ce que c'est ?

Ce package modélise le calcul complet d'un compte de taxes foncières
montréalais, incluant :

- **Taxe foncière générale** — avec taux variés par catégorie d'immeuble
  et taux différenciés pour le non résidentiel (seuil à 900 000 $)
- **Taxe ARTM** — contribution au transport métropolitain
- **Taxe de voirie** — entretien du réseau routier
- **Taxes d'arrondissement** — 19 arrondissements avec taux de services,
  d'investissements et montants fixes
- **Mesure d'étalement** — lissage triennal de la variation du rôle foncier

Les taux encodés sont ceux du **Budget 2026** de la Ville de Montréal.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Utilisation

### API Python

```python
from openfisca_montreal import MontrealTaxBenefitSystem

system = MontrealTaxBenefitSystem()
simulation = system.new_simulation()

# Définir la situation
simulation.set_input("categorie_immeuble", 2026, "residentiel")
simulation.set_input("arrondissement", 2026, "rosemont_la_petite_patrie")
simulation.set_input("valeur_fonciere_role_precedent", 2026, 450000)
simulation.set_input("valeur_fonciere_role_courant", 2026, 500000)
simulation.set_input("annee_role", 2026, 1)

# Calculer
total = simulation.calculate("total_taxes_foncieres", 2026)
print(f"Total annuel: {total[0]:.2f} $")
print(f"Mensuel: {total[0] / 12:.2f} $")
```

### API Web (JSON)

```bash
# Démarrer le serveur
openfisca serve --port 5000 \
  --country-package openfisca_country_template \
  --extensions openfisca_montreal
```

Requête de calcul :

```bash
curl -X POST http://localhost:5000/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "households": {
      "mon_immeuble": {
        "categorie_immeuble": {"2026": "residentiel"},
        "arrondissement": {"2026": "rosemont_la_petite_patrie"},
        "valeur_fonciere_role_precedent": {"2026": 450000},
        "valeur_fonciere_role_courant": {"2026": 500000},
        "annee_role": {"2026": 1},
        "total_taxes_foncieres": {"2026": null},
        "taxe_fonciere_generale": {"2026": null},
        "taxe_artm": {"2026": null},
        "taxe_voirie": {"2026": null},
        "taxe_arrondissement": {"2026": null}
      }
    },
    "persons": {
      "proprietaire": {}
    }
  }'
```

## Tests

```bash
openfisca test tests/ \
  --country-package openfisca_country_template \
  --extensions openfisca_montreal
```

## Structure du package

```
src/openfisca_montreal/
├── __init__.py
├── parameters/
│   └── taxes_foncieres/
│       ├── conseil_municipal/
│       │   ├── taxe_fonciere_generale.yaml   # Taux par catégorie
│       │   ├── taxe_artm.yaml                # Taux ARTM
│       │   └── taxe_voirie.yaml              # Taux voirie
│       ├── arrondissements/
│       │   └── taux_arrondissements.yaml      # 19 arrondissements
│       └── seuils.yaml                        # Seuil 900 000 $
└── variables/
    ├── immeuble.py               # Enums + variables d'entrée
    ├── base_imposition.py        # Étalement triennal
    ├── taxe_fonciere_generale.py # Taxe principale
    ├── taxes_secondaires.py      # ARTM + voirie
    ├── taxe_arrondissement.py    # Taxes des 19 arrondissements
    └── total_taxes.py            # Synthèse annuelle et mensuelle
```

## Sources réglementaires

| Document | URL |
|----------|-----|
| Taux de taxes 2026 | [montreal.ca](https://montreal.ca/articles/taux-de-taxes-pour-2026-106147) |
| Comment sont calculées les taxes | [montreal.ca](https://montreal.ca/articles/comment-sont-calculees-les-taxes-municipales-8962) |
| Budget 2026 | [montreal.ca](https://montreal.ca/actualites/montreal-presente-son-budget-2026-et-son-pdi-2026-2035-105890) |
| Rôle d'évaluation 2026-2028 | [montreal.ca](https://montreal.ca/evaluation-fonciere) |

## Licence

[AGPL-3.0](LICENSE) — Conformément à la licence d'OpenFisca Core.

## Contribuer

Les contributions sont bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md).

Pour mettre à jour les taux lors du prochain budget :
1. Mettre à jour les fichiers YAML dans `parameters/`
2. Ajouter une nouvelle entrée de date (ex: `2027-01-01`)
3. Exécuter les tests pour valider
