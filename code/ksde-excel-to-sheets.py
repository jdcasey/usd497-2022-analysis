#!/usr/bin/env python

import pandas as pd
import click
import csv
from glob import glob
import os.path as path
import datetime as dt

## Headers look like this (7 lines):
# D0497 Lawrence									ORG. #: D0497
#
# 2020-2021
#  DISTRICT HEADCOUNT ENROLLMENT
# BY  GRADE, RACE AND GENDER
# 	TOTAL	TOTAL 		WHITE 		BLACK 				HISPANIC		AMER. INDIAN OR ALASKA NATIVE		...
# GRADE	ALL	MALE	FEMALE	MALE	FEMALE	MALE	FEMALE			MALE	FEMALE	MALE	FEMALE	MALE	...
## ---------------------------------------
# The headers counter is 0-indexed, so 7 lines is a value of 6
SPREADSHEET_HEADER_LINES = 6

# Once again, columns are 0-index, but the first one happens to correspond to Kindergarten, making the others align
# to the actual grade level. So, we don't discard column 0.
# The other columns discarded here are mangled totals, and economic subdivisions that, if included, would result
# in over-counting economically disadvantaged kids in the enrollment stats.
DISCARD_COLS = [
    1, 2, 3, 4,                 # garbage semi-complete "totals"
    9, 10,                      # blank / hidden columns, just for fun
    19, 20, 21, 22, 23, 24  # duplicate counts of the economically disadvantaged
]


def parse_year(excel, year, end_grade):
    df = pd.read_excel(excel, sheet_name=0, header=SPREADSHEET_HEADER_LINES)

    sums = []
    guesses = 0
    for tp in df.itertuples(name=None):
        if tp[0] > end_grade:
            break

        rd = [val for idx, val in enumerate(tp) if idx not in DISCARD_COLS]
        for idx, val in enumerate(rd):
            if isinstance(val, float):
                rd[idx] = 0
            elif val == "<10*":
                rd[idx] = 1
                guesses += 1
            elif isinstance(val, str):
                rd[idx] = int(val)

        # sums index 0-8, where 0 is Kindergarten
        sums.append(sum(rd[1:]))

    # Minimum total, after de-fuzzing KDHE's PII obfuscator
    min_total = sum(sums)
    sums.append(min_total)

    # Maximum total, after de-fuzzing KDHE's PII obfuscator
    sums.append(min_total + 9*guesses)
    sums.insert(0, year)

    return sums


@click.command()
@click.argument("directory")
@click.option("-e", "--end-grade", default=8, help="Highest grade to aggregate")
@click.option("-o", "--output", default=None, help="output path")
def run(directory, end_grade, output):
    this_year = dt.datetime.now().year
    start_year = this_year - 20

    if not output:
        output = path.join(directory, f"K-{end_grade} Total Enrollment {start_year}-{this_year}.csv")

    with open(output, 'w') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(
            ["Year", "Kindergarten"] +
            [f"Grade {i}" for i in range(1, end_grade+1)] +
            ["Minimum Total", "Maximum Total"]
        )

        years = []
        for year in range(start_year, this_year):
            fpath = path.join(directory, f"aggregate-enrollment-{year}.xls")
            if path.exists(fpath):
                writer.writerow(parse_year(fpath, year, int(end_grade)))
                years.append(year)

    print(f"Wrote years: {years} to: {output}")


if __name__ == "__main__":
    run()
