# Tableau data dictionary: 2026 extraction

Run `src/election_analysis/clean_2026.py` to create the following files in `data/processed/`. These tables are all at polling-station or vote-option level and are suitable for Tableau Public.

| File | Grain | Purpose |
| --- | --- | --- |
| `turnout_2026.csv` | Polling station | Registered voters, voters who cast a ballot, transfer/foreign-mission counts, and `turnout_rate`. |
| `individual_polling_metrics_2026.csv` | Polling station | Official individual-ballot protocol fields, including valid and invalid ballots. |
| `individual_votes_2026.csv` | Polling station × candidate | Candidate votes, readable candidate name, county, and OEVK. |
| `candidate_lookup_2026.csv` | OEVK × candidate | Candidate ballot-number to name mapping. |
| `list_polling_metrics_2026.csv` | Polling station | Official list-ballot protocol fields. |
| `list_votes_2026.csv` | Polling station × party | Party-list votes with party name, county, and polling-station ID. |
| `postal_votes_2026.csv` | National | Official aggregated postal-vote counts by party. |

## Important field definitions

- **OEVK**: single-member parliamentary constituency. It is reliable for comparisons within the 2014–2026 electoral-boundary regime.
- **Polling-station ID**: official NVI identifier, retained as text because it is an identifier rather than a number.
- **Votes**: votes credited to one candidate or party at one polling station.
- **Turnout rate**: voters casting their ballot divided by registered voters. The source turnout workbook separates regular-register voters from voters transferred from another polling station or voting at a foreign mission; the dashboard will label which denominator it uses.

## First Tableau data model

Use `list_votes_2026.csv` as the primary 2026 party-performance fact table. Use `individual_votes_2026.csv` for constituency competitiveness. Join/relate turnout only after creating a stable shared polling-station key; do not join directly on municipality names.

The 2026 boundary GeoJSON is a separate spatial file. Use it at OEVK level after aggregating candidate votes to OEVK, rather than attempting a polling-station boundary map.
