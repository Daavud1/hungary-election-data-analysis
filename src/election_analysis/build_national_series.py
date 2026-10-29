"""Combine official parliamentary-election national series for the version-1 analysis."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCES = json.loads((PROJECT_ROOT / "config" / "source_paths.json").read_text(encoding="utf-8"))
ARCHIVE_DIR = Path(SOURCES["historical_archive_dir"])
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def read_zip_excel(zip_name: str, member: str) -> pd.DataFrame:
    with zipfile.ZipFile(ARCHIVE_DIR / zip_name) as archive:
        return pd.read_excel(io.BytesIO(archive.read(member)))


def modern_2014() -> tuple[pd.DataFrame, pd.DataFrame]:
    with zipfile.ZipFile(ARCHIVE_DIR / "2014_parlamenti.zip") as archive:
        source = pd.read_csv(io.BytesIO(archive.read("2014_parlamenti/Listás-szavazás-jkv.csv")), encoding="cp1250")
    votes = source.dropna(subset=["LISTA", "SZAVAZAT"]).groupby("LISTA", as_index=False)["SZAVAZAT"].sum()
    votes.columns = ["party_raw", "votes"]
    votes["election_year"] = 2014
    parent_rows = source[source["'LISTÁS'"].notna()]
    turnout = pd.DataFrame(
        {
            "election_year": [2014],
            "registered_voters": [parent_rows["VÁLASZTÓPOLGÁR"].sum()],
            "voters_cast": [parent_rows["MEGJELENTEK"].sum()],
        }
    )
    return votes, turnout


def modern_national_xlsx(year: int, zip_name: str, member: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    source = read_zip_excel(zip_name, member)
    first = source.iloc[0]
    party_rows = source.dropna(subset=["PÁRT_LISTA", "PÁRT_LISTA_SZAVAZAT"])
    votes = party_rows[["PÁRT_LISTA", "PÁRT_LISTA_SZAVAZAT"]].copy()
    votes.columns = ["party_raw", "votes"]
    votes["election_year"] = year
    turnout = pd.DataFrame(
        {
            "election_year": [year],
            "registered_voters": [first["VÁLASZTÓPOLGÁR"]],
            "voters_cast": [first["MEGJELENTEK"]],
        }
    )
    return votes, turnout


def results_2026() -> pd.DataFrame:
    source = pd.read_csv(SOURCES["party_lists_2026_10_19"])
    votes = source[["List name", "Total number of party-list votes"]].copy()
    votes.columns = ["party_raw", "votes"]
    votes["votes"] = votes["votes"].str.replace(",", "", regex=False).astype(int)
    votes["election_year"] = 2026
    return votes


def main() -> None:
    historical_votes = pd.read_csv(PROCESSED_DIR / "historical_national_list_votes_1990_2010.csv")
    historical_turnout = pd.read_csv(PROCESSED_DIR / "historical_national_turnout_1990_2010.csv")

    parts = [historical_votes[["election_year", "party_raw", "votes"]]]
    turnout_parts = [historical_turnout[["election_year", "registered_voters", "voters_cast"]]]
    for args in [
        (2014, "2014_parlamenti.zip", "2014_parlamenti/Listás-szavazás-jkv.xlsx"),
        (2018, "2018_parlamenti.zip", "2018_parlamenti/Orsz_listás_erjkv1.xlsx"),
        (2022, "2022_parlamenti.zip", "Országos_listás_eredmény.xlsx"),
    ]:
        if args[0] == 2014:
            votes, turnout = modern_2014()
        else:
            votes, turnout = modern_national_xlsx(*args)
        parts.append(votes)
        turnout_parts.append(turnout)
    parts.append(results_2026())

    national_votes = pd.concat(parts, ignore_index=True)
    national_votes["votes"] = pd.to_numeric(national_votes["votes"])
    national_votes["vote_share"] = national_votes["votes"] / national_votes.groupby("election_year")["votes"].transform("sum")
    national_turnout = pd.concat(turnout_parts, ignore_index=True)
    national_turnout["turnout_rate"] = national_turnout["voters_cast"] / national_turnout["registered_voters"]
    national_votes.to_csv(PROCESSED_DIR / "national_party_list_results_1990_2026.csv", index=False, encoding="utf-8-sig")
    national_turnout.to_csv(PROCESSED_DIR / "national_turnout_1990_2022.csv", index=False, encoding="utf-8-sig")
    print(f"national_party_list_results_1990_2026.csv: {len(national_votes):,} rows")
    print(f"national_turnout_1990_2022.csv: {len(national_turnout):,} rows")


if __name__ == "__main__":
    main()
