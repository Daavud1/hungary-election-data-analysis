"""Create constituency winner-margin data for 2014–2026."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCES = json.loads((PROJECT_ROOT / "config" / "source_paths.json").read_text(encoding="utf-8"))
ARCHIVE_DIR = Path(SOURCES["historical_archive_dir"])
PROCESSED = PROJECT_ROOT / "data" / "processed"


def read_zip_excel(zip_path: Path, member: str) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as archive:
        return pd.read_excel(io.BytesIO(archive.read(member)))


def official_oevk(year: int, zip_name: str, member: str) -> pd.DataFrame:
    raw = read_zip_excel(ARCHIVE_DIR / zip_name, member)
    raw[["MEGYEKÓD", "MEGYE", "OEVK", "SZÉKHELY"]] = raw[["MEGYEKÓD", "MEGYE", "OEVK", "SZÉKHELY"]].ffill()
    candidates = raw.dropna(subset=["JELÖLT", "SZAVAZAT"]).copy()
    candidates["SZAVAZAT"] = pd.to_numeric(candidates["SZAVAZAT"])
    if year == 2014:
        # The 2014 workbook is polling-station-level; later workbooks are OEVK summaries.
        candidates = candidates.groupby(
            ["MEGYEKÓD", "MEGYE", "OEVK", "SZÉKHELY", "JELÖLT"], as_index=False
        )["SZAVAZAT"].sum()
    candidates = candidates.sort_values(["MEGYEKÓD", "OEVK", "SZAVAZAT"], ascending=[True, True, False])
    summary = candidates.groupby(["MEGYEKÓD", "MEGYE", "OEVK", "SZÉKHELY"], as_index=False).agg(
        winner=("JELÖLT", "first"),
        winner_votes=("SZAVAZAT", "first"),
        runner_up_votes=("SZAVAZAT", lambda value: value.iloc[1] if len(value) > 1 else 0),
        valid_votes=("SZAVAZAT", "sum"),
    )
    summary["election_year"] = year
    return summary


def results_2026() -> pd.DataFrame:
    raw = pd.read_csv(PROCESSED / "individual_votes_2026.csv")
    grouped = raw.groupby(["county", "oevk", "candidate_name"], as_index=False)["votes"].sum()
    grouped = grouped.sort_values(["county", "oevk", "votes"], ascending=[True, True, False])
    summary = grouped.groupby(["county", "oevk"], as_index=False).agg(
        winner=("candidate_name", "first"),
        winner_votes=("votes", "first"),
        runner_up_votes=("votes", lambda value: value.iloc[1] if len(value) > 1 else 0),
        valid_votes=("votes", "sum"),
    )
    summary["election_year"] = 2026
    summary = summary.rename(columns={"county": "MEGYE", "oevk": "OEVK"})
    summary["MEGYEKÓD"] = pd.NA
    summary["SZÉKHELY"] = pd.NA
    return summary


def finalize(frame: pd.DataFrame) -> pd.DataFrame:
    frame["margin_votes"] = frame["winner_votes"] - frame["runner_up_votes"]
    frame["margin_share"] = frame["margin_votes"] / frame["valid_votes"]
    return frame[["election_year", "MEGYEKÓD", "MEGYE", "OEVK", "SZÉKHELY", "winner", "winner_votes", "runner_up_votes", "valid_votes", "margin_votes", "margin_share"]]


def main() -> None:
    frames = [
        official_oevk(2014, "2014_parlamenti.zip", "2014_parlamenti/Egyéni-szavazás-jkv.xlsx"),
        official_oevk(2018, "2018_parlamenti.zip", "2018_parlamenti/Egyéni_szavazás_erjkv.xlsx"),
        official_oevk(2022, "2022_parlamenti.zip", "Egyéni_szavazás_erjkv.xlsx"),
        results_2026(),
    ]
    result = finalize(pd.concat(frames, ignore_index=True))
    result.to_csv(PROCESSED / "oevk_competitiveness_2014_2026.csv", index=False, encoding="utf-8-sig")
    print(f"oevk_competitiveness_2014_2026.csv: {len(result):,} rows")


if __name__ == "__main__":
    main()
