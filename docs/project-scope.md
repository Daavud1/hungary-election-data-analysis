# Project scope: version 1

## Goal

Create a reproducible academic data-analysis portfolio project using official Hungarian election results. The project will show data cleaning, validation, exploratory analysis, geographic analysis, dashboard design, and clear communication of limitations.

## Version-1 analytical scope

| Question | Geographic level | Years | Intended output |
| --- | --- | --- | --- |
| Turnout change | National | 1990–2026 | Trend chart with election annotations |
| Party support change | National | 1990–2026 | Major-party / coalition vote-share trends |
| Turnout patterns | County | Available parliamentary cycles | Heatmap, ranking, map |
| Party-support swings | County | 2022–2026 | Change map and ranked table |
| Constituency competitiveness | OEVK | 2014–2026 | Winner-margin distribution and map |

## Deliverables

1. Clean, documented Tableau-ready data tables.
2. Reproducible Jupyter notebooks for inventory, cleaning, validation, and analysis.
3. Tableau Public dashboard.
4. Public GitHub repository with a readable README.
5. GitHub Pages project website embedding or linking the Tableau dashboard.

## Current data status

- National party-list results: 1990–2026 complete for the registered party lists in each official national result.
- Final national turnout: 1990–2022 complete.
- County-level shares for FIDESZ-KDNP, MKKP, and Mi Hazánk: comparable 2022–2026 table complete. Other 2022 opposition parties stood on a joint list, so they are not presented as direct party-to-party swings.
- 2026 turnout: the supplied workbook reports 19:00 participation rather than final participation, so it is retained for later intraday analysis and excluded from the final-turnout trend.

## Non-goals for version 1

- Causal claims about voter behaviour.
- Demographic or economic correlations without a compatible external dataset.
- Direct constituency comparisons before 2014.
- A comprehensive treatment of local elections, EP elections, and referendums.

## Quality rules

- Preserve raw source files without modification.
- Record the official source and original file name for every derived table.
- Validate vote totals against official totals where source layouts allow.
- Treat coalitions and renamed parties through a documented crosswalk.
- State denominator and geographic level on every chart.
