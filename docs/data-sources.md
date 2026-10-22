# Data sources

All election-result data used in this project comes from Hungary's National Election Office (NVI).

## Supplied historical archive

- [Processable results from previous elections, 1990–2024](https://www.valasztas.hu/en/korabbi-valasztasok-feldolgozhato-adatai)
- Local archive supplied by the project owner: `valasztasi_eredmenyek_1990-2024`

## Supplied 2026 parliamentary-election data

The following files are stored locally and deliberately excluded from Git:

- list polling-station results, by county
- individual-constituency polling-station results, by county
- postal-voting results
- 19:00 turnout data
- parliamentary single-member constituency GeoJSON

Official download page: [2026 downloadable and processable parliamentary-election data](https://www.valasztas.hu/ogy2026-letoltheto-es-tovabbfeldolgozhato-adatok).

## Reproducibility policy

Raw official data can be downloaded again from NVI and may be too large or unsuitable to commit. The repository will contain source URLs, file names, extraction scripts, validation checks, clean schemas, and small derived tables needed for the public dashboard.

## Key comparability note

Parliamentary constituency boundaries and electoral rules changed before the 2014 election. National and county-level trends can be compared across the full period, but constituency-level analysis in the first release is restricted to 2014–2026 unless a documented historical boundary crosswalk is added.
