# Findings: Hungary parliamentary elections

This page summarises descriptive results from the version-1 pipeline. These are not causal claims about voter behaviour.

## 1. National turnout, 1990–2022

Final national turnout varied by 14.2 percentage points across the nine parliamentary elections in the series. It was lowest in 1998 (56.3%) and highest in 2002 (70.5%). Turnout was 69.7% in 2018 and 69.6% in 2022.

The supplied 2026 turnout workbook is a 19:00 participation snapshot rather than a final result. It is therefore excluded from this chart rather than being compared as if it were final turnout.

## 2. Party-list results

The national results table records each list exactly as named in the corresponding official result. In the supplied 2026 output, TISZA received 53.5% of party-list votes and FIDESZ-KDNP received 38.9%.

Historical party names, coalitions, and ballot arrangements change over time. Trend interpretation must therefore distinguish a stable party label from a coalition or renamed list. In particular, the 2022 opposition competed as a joint list, so its share is not a direct single-party comparison with 2026 TISZA.

## 3. Comparable county shifts, 2022–2026

The county comparison uses the full party-list vote denominator and only lists that appeared separately in both 2022 and 2026: FIDESZ-KDNP, MKKP, and Mi Hazánk. FIDESZ-KDNP’s share fell in all 20 county-level units; the estimated change ran from −12.5 percentage points in Budapest to −18.9 points in Hajdú-Bihar.

This measures a change in party share. It does not identify the destination of votes or establish a causal explanation.

## 4. Constituency competitiveness, 2014–2026

Competitiveness is calculated as the winner’s vote-share margin over the runner-up in each of the 106 single-member constituencies. The average margin was 16.6 points in 2014, 18.2 in 2018, 19.5 in 2022, and 18.2 in 2026.

The series begins in 2014 because constituency boundaries and electoral rules changed before that election. Earlier results need a documented boundary crosswalk before constituency-level comparisons can be made responsibly.

## Reproduction

Run the scripts in `src/election_analysis/` after configuring the local source paths. See [data sources](data-sources.md) and [project scope](project-scope.md) for provenance and limitations.
