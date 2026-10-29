"""Prepare a cautious county-level comparison for parties present in 2022 and 2026."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCES = json.loads((PROJECT_ROOT / "config" / "source_paths.json").read_text(encoding="utf-8"))
ARCHIVE = Path(SOURCES["historical_archive_dir"]) / "2022_parlamenti.zip"
PROCESSED = PROJECT_ROOT / "data" / "processed"


def party_key(label: str) -> str | None:
    label = str(label).upper()
    if "FIDESZ" in label:
        return "FIDESZ-KDNP"
    if "KÉTFARKÚ" in label:
        return "MKKP"
    if "MI HAZÁNK" in label:
        return "Mi Hazánk"
    return None


def county_2022() -> pd.DataFrame:
    with zipfile.ZipFile(ARCHIVE) as archive:
        raw = pd.read_excel(io.BytesIO(archive.read("Területi_listás_részerjkv.xlsx")))
    raw[["MEGYEKÓD", "MEGYE MEGNEVEZÉSE"]] = raw[["MEGYEKÓD", "MEGYE MEGNEVEZÉSE"]].ffill()
    rows = raw.dropna(subset=["PÁRT_LISTA", "PÁRT_LISTA_SZAVAZAT"]).copy()
    rows["total_party_votes"] = rows.groupby("MEGYE MEGNEVEZÉSE")["PÁRT_LISTA_SZAVAZAT"].transform("sum")
    rows["party"] = rows["PÁRT_LISTA"].map(party_key)
    rows = rows.dropna(subset=["party"])
    result = rows[["MEGYEKÓD", "MEGYE MEGNEVEZÉSE", "party", "PÁRT_LISTA_SZAVAZAT"]].copy()
    result.columns = ["county_code", "county", "party", "votes"]
    result["total_party_votes"] = rows.loc[result.index, "total_party_votes"]
    result["election_year"] = 2022
    return result


def county_2026() -> pd.DataFrame:
    raw = pd.read_csv(PROCESSED / "list_votes_2026.csv")
    result = raw.groupby(["county", "party"], as_index=False)["votes"].sum()
    result["total_party_votes"] = result.groupby("county")["votes"].transform("sum")
    result = result[result["party"].isin(["FIDESZ-KDNP", "MKKP", "Mi Hazánk"])]
    result["county_code"] = pd.NA
    result["election_year"] = 2026
    return result[["county_code", "county", "party", "votes", "total_party_votes", "election_year"]]


def main() -> None:
    result = pd.concat([county_2022(), county_2026()], ignore_index=True)
    result["vote_share"] = result["votes"] / result["total_party_votes"]
    result.to_csv(PROCESSED / "county_comparable_party_shares_2022_2026.csv", index=False, encoding="utf-8-sig")
    print(f"county_comparable_party_shares_2022_2026.csv: {len(result):,} rows")


if __name__ == "__main__":
    main()
