# Contribuer à OpenFisca Montréal

Merci de votre intérêt pour ce projet de *Rules as Code* municipal !

## Comment contribuer

### Mettre à jour les taux annuels

Chaque année, le conseil municipal et les arrondissements adoptent de
nouveaux taux. Pour les mettre à jour :

1. Consulter les [taux officiels](https://montreal.ca/taxes-municipales)
2. Ajouter une nouvelle entrée datée dans les fichiers YAML sous `parameters/`
3. Exécuter les tests : `openfisca test tests/ --country-package openfisca_country_template --extensions openfisca_montreal`
4. Soumettre un *pull request*

### Ajouter une nouvelle variable

1. Créer un fichier Python dans `src/openfisca_montreal/variables/`
2. Documenter la source réglementaire dans `reference`
3. Ajouter des tests YAML dans `tests/`

### Conventions

- Les variables sont nommées en `snake_case` français
- Chaque variable référence sa source réglementaire
- Les taux sont exprimés en $ par 100 $ de valeur d'évaluation
- Les montants sont en dollars canadiens (CAD)

## Code de conduite

Ce projet suit le [code de conduite d'OpenFisca](https://openfisca.org/doc/contribute/guidelines.html).
