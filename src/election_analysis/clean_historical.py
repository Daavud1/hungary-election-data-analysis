"""Extract comparable first-round parliamentary list votes and turnout, 1990–2010."""

from __future__ import annotations

import csv
import json
import zipfile
from io import TextIOWrapper
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCES = json.loads((PROJECT_ROOT / "config" / "source_paths.json").read_text(encoding="utf-8"))
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
ARCHIVE_DIR = Path(SOURCES["historical_archive_dir"])

PRE_2002 = {1990, 1994, 1998}
YEARS = [1990, 1994, 1998, 2002, 2006, 2010]


def read_pipe_rows(archive: zipfile.ZipFile, member: str) -> list[list[str]]:
    with archive.open(member) as binary:
        reader = csv.reader(TextIOWrapper(binary, encoding="cp1250"), delimiter="|")
        return [[value.strip() for value in row] for row in reader if row]


def members(year: int) -> tuple[str, str, str]:
    if year in PRE_2002:
        root = f"{year}_parlamenti"
        return f"{root}/lis_szkt.txt", f"{root}/szkf.txt", ""
    if year == 2002:
        root = "2002_parlamenti/1_ford"
    elif year == 2006:
        root = "2006_parlamenti/txt_1ford"
    else:
        root = "2010_parlamenti/txt_1ford"
    return f"{root}/lis_ert.txt", f"{root}/lis_erf.txt", ""


def extract_pre_2002(year: int, archive: zipfile.ZipFile, list_member: str, turnout_member: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    vote_rows = []
    for row in read_pipe_rows(archive, list_member):
        if row[0] != "1":
            continue
        vote_rows.append(
            {
                "election_year": year,
                "county_code": row[1],
                "party_raw": row[-2],
                "votes": int(row[-1]),
            }
        )
    turnout_rows = []
    for row in read_pipe_rows(archive, turnout_member):
        if row[0].lower() != "listás" or row[1] != "1":
            continue
        turnout_rows.append(
            {
                "election_year": year,
                "county_code": row[2],
                "county_name_raw": row[5],
                "registered_voters": int(row[11]),
                "voters_cast": int(row[12]),
            }
        )
    return pd.DataFrame(vote_rows), pd.DataFrame(turnout_rows)


def extract_2002_plus(year: int, archive: zipfile.ZipFile, list_member: str, turnout_member: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    vote_rows = []
    for row in read_pipe_rows(archive, list_member):
        vote_rows.append(
            {
                "election_year": year,
                "county_code": row[0],
                "party_raw": row[2],
                "votes": int(row[3]),
            }
        )
    turnout_rows = []
    for row in read_pipe_rows(archive, turnout_member):
        # The 2006 protocol added an extra intermediate register field.
        registered_index = 7 if year >= 2006 else 6
        voters_index = 9 if year == 2006 else 8
        turnout_rows.append(
            {
                "election_year": year,
                "county_code": row[0],
                "county_name_raw": row[1],
                "registered_voters": int(row[registered_index]),
                "voters_cast": int(row[voters_index]),
            }
        )
    return pd.DataFrame(vote_rows), pd.DataFrame(turnout_rows)


def main() -> None:
    all_votes: list[pd.DataFrame] = []
    all_turnout: list[pd.DataFrame] = []
    for year in YEARS:
        zip_path = ARCHIVE_DIR / f"{year}_parlamenti.zip"
        list_member, turnout_member, _ = members(year)
        with zipfile.ZipFile(zip_path) as archive:
            if year in PRE_2002:
                votes, turnout = extract_pre_2002(year, archive, list_member, turnout_member)
            else:
                votes, turnout = extract_2002_plus(year, archive, list_member, turnout_member)
        all_votes.append(votes)
        all_turnout.append(turnout)

    votes = pd.concat(all_votes, ignore_index=True)
    turnout = pd.concat(all_turnout, ignore_index=True)
    county_votes = votes.groupby(["election_year", "county_code", "party_raw"], as_index=False)["votes"].sum()
    national_votes = county_votes.groupby(["election_year", "party_raw"], as_index=False)["votes"].sum()
    national_votes["vote_share"] = national_votes["votes"] / national_votes.groupby("election_year")["votes"].transform("sum")
    county_turnout = turnout.groupby(["election_year", "county_code", "county_name_raw"], as_index=False)[["registered_voters", "voters_cast"]].sum()
    county_turnout["turnout_rate"] = county_turnout["voters_cast"] / county_turnout["registered_voters"]
    national_turnout = county_turnout.groupby("election_year", as_index=False)[["registered_voters", "voters_cast"]].sum()
    national_turnout["turnout_rate"] = national_turnout["voters_cast"] / national_turnout["registered_voters"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {
        "historical_county_list_votes_1990_2010.csv": county_votes,
        "historical_national_list_votes_1990_2010.csv": national_votes,
        "historical_county_turnout_1990_2010.csv": county_turnout,
        "historical_national_turnout_1990_2010.csv": national_turnout,
    }
    for name, frame in outputs.items():
        frame.to_csv(OUTPUT_DIR / name, index=False, encoding="utf-8-sig")
        print(f"{name}: {len(frame):,} rows")


if __name__ == "__main__":
    main()
