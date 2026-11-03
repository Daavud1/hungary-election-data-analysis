# Tableau companion dashboard guide

The portfolio site is the primary published dashboard. This guide recreates the companion Tableau workbook from the generated CSV files in `data/processed/`.

## Data connections

Connect each file separately as a text/CSV data source. Do not join them: they have different geographic levels and denominators.

| Worksheet | File | Core fields |
| --- | --- | --- |
| Turnout trend | `national_turnout_1990_2022.csv` | `election_year`, `turnout_rate` |
| Party-list result | `national_party_list_results_1990_2026.csv` | `election_year`, `party_raw`, `vote_share` |
| County shifts | `county_comparable_party_shares_2022_2026.csv` | `county`, `party`, `election_year`, `vote_share` |
| Competitiveness | `oevk_competitiveness_2014_2026.csv` | `election_year`, `county`, `oevk`, `winner`, `runner_up`, `margin_share` |

## Worksheet 1: turnout trend

1. Put `election_year` on **Columns** and set it to continuous.
2. Put `turnout_rate` on **Rows** and use `AVG`.
3. Set the Marks type to **Line** and format `turnout_rate` as a percentage with one decimal place.
4. Name the sheet `Turnout trend`.

Title: **Hungarian Parliamentary Election Turnout (1990–2022)**.

Do not add 2026 to this chart: the supplied 2026 turnout file is a 19:00 snapshot rather than final turnout.

## Worksheet 2: national party-list results

1. Put `election_year` on **Columns** and `vote_share` on **Rows**.
2. Put `party_raw` on **Color**.
3. Filter to a small, stated selection of lists (for example, the top five in 2026) to keep the chart readable.
4. Add `party_raw` and `vote_share` to Tooltip; format shares as percentages.

Title: **National Party-List Results by Election Year**.

Add a visible note: party names, coalitions, and ballot arrangements change across elections; do not treat unlike lists as direct continuations.

## Worksheet 3: comparable county party-share shifts

Pivot the data in Tableau (or use a table calculation) so each county and party has a 2022 share and a 2026 share in the same row. Then calculate **Share change (pp)** as `2026 share - 2022 share`.

Create a horizontal bar chart:

- `county` on Rows
- share-change calculation on Columns
- `party` on Color and Filter
- sort by the change

Title: **County Party-List Share Change, 2022–2026**.

Only use FIDESZ-KDNP, MKKP, and Mi Hazánk in this comparable view. The 2022 opposition ran on a joint list and is not a direct single-party comparison with 2026 TISZA.

## Worksheet 4: constituency competitiveness

1. Put `election_year` on Columns and `margin_share` on Rows.
2. Use a **Box-and-Whisker Plot** or a dot plot by `oevk`.
3. Add `county`, `oevk`, `winner`, `runner_up`, and `margin_share` to Tooltip.
4. Format the margin as a percentage with one decimal place.

Title: **Single-Member Constituency Winning Margins (2014–2026)**.

The margin is the winner’s share minus the runner-up’s share. The time series begins in 2014 because constituency boundaries changed before that election.

## Dashboard layout

Build one dashboard named `Hungary election overview`:

1. Top row: dashboard title and a short source statement.
2. Middle row: turnout trend (wide) and party-list result (wide).
3. Bottom row: county shifts and competitiveness.
4. Add a text box called **Interpretation and caveats** using the comparability notes above.
5. Add the NVI source URL and repository URL in the footer.

Before publishing to Tableau Public, check the data source names, the 2026 turnout caveat, and every chart title’s geographic level and denominator.
