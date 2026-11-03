# Hungary Election Data Analysis

An internship portfolio project analysing how turnout, party support, electoral geography, and constituency competitiveness changed in Hungarian parliamentary elections from 1990 to 2026.

## Research questions

1. How has national parliamentary-election turnout changed since 1990?
2. How has major-party and coalition support changed over time?
3. Which counties have persistently high or low turnout?
4. Which counties experienced the largest shifts in party support, especially from 2022 to 2026?
5. How competitive were parliamentary constituencies in 2014, 2018, 2022, and 2026?

## Headline findings

- National final turnout was lowest in 1998 (56.3%) and highest in 2002 (70.5%).
- The supplied 2026 party-list result records TISZA at 53.5% and FIDESZ-KDNP at 38.9%.
- FIDESZ-KDNP’s comparable party-list share declined in all 20 county-level units from 2022 to 2026.
- Average winner–runner-up constituency margin peaked at 19.5 percentage points in 2022 across the 2014–2026 series.

Read the definitions, caveats, and full descriptive results in [docs/findings.md](docs/findings.md).

## Tools

- Python and JupyterLab for extraction, cleaning, validation, and analysis
- Tableau Public for interactive dashboards
- GitHub and GitHub Pages for reproducibility and the public portfolio site

## Data sources

The project uses official results published by Hungary's National Election Office (NVI). The original files are not committed to Git; see [docs/data-sources.md](docs/data-sources.md) for source links and the local-data setup.

## Status

The first portfolio release is complete: national turnout (1990–2022), national party-list results (1990–2026), comparable county party shares (2022–2026), and constituency competitiveness (2014–2026).

## Portfolio site

The static source for the GitHub Pages portfolio is in [`site/`](site/). A GitHub Actions workflow publishes that folder whenever it changes. After enabling **Settings → Pages → Source: GitHub Actions**, it will be available at:

`https://daavud1.github.io/hungary-election-data-analysis/`

## Local setup

1. Copy `config/source_paths.example.json` to `config/source_paths.json` and update the local file paths if necessary.
2. Create a virtual environment: `python -m venv .venv`
3. Install dependencies: `.venv\\Scripts\\python -m pip install -r requirements.txt`
4. Create the source inventory: `.venv\\Scripts\\python src/election_analysis/inventory.py`
5. Extract the 2026 tables: `.venv\\Scripts\\python src/election_analysis/clean_2026.py`

The generated tables are intentionally ignored by Git. See [docs/tableau-data-dictionary.md](docs/tableau-data-dictionary.md) for the inputs to the first dashboard.

## Repository layout

```text
config/       local source-path template
data/         ignored raw, interim, and processed data
docs/         methodology and source notes
notebooks/    reproducible analysis notebooks
src/          reusable Python code
tableau/      Tableau workbook and dashboard assets
site/         GitHub Pages source
```
