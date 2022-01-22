#!/usr/bin/env python

import csv
import sys
import locale

locale.setlocale(locale.LC_ALL, '')

DATA_FILE = sys.argv[1]
CUTOFF = 100000
EXCEPT_POSITIONS = ["Principal", "Director Virtual"]

by_year = {}

with open(DATA_FILE, newline='') as csvfile:
    reader = csv.reader(csvfile)
    header_passed = False
    for row in reader:
        if header_passed:
            salary = int(row[-1].replace("$", "").replace(",", ""))
            position = row[-2]
            year = int(row[0])

            if salary >= CUTOFF:
                exempt = False
                for key in EXCEPT_POSITIONS:
                    if key in position:
                        exempt = True

                if not exempt:
                    year_data = by_year.get(year)
                    if year_data is None:
                        year_data = []
                        by_year[year] = year_data

                    year_data.append({'position': position, 'salary': salary})

        else:
            header_passed = True


last_payroll = None
with open("Non-Principal Payroll Over 100k.csv", "w", newline='') as csvfile:
    csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
    csvwriter.writerow(["Year", "# Positions", "Total Salary", "% Increase YoY"])
    
    for year in sorted(by_year.keys()):
        data = by_year[year]

        for pos in sorted(data, key=lambda x:x['salary'], reverse=True):
            print(f"{year}, {pos['position']}, {locale.currency(pos['salary'], grouping=True)}")

        payroll = sum([d['salary'] for d in data])
        positions = len(data)

        if last_payroll:
            pct_increase = "%.2f" % ((payroll-last_payroll) / last_payroll * 100) + "%"
        else:
            pct_increase = "0.00%"

        csvwriter.writerow([year, positions, locale.currency(payroll, grouping=True), pct_increase])
        print("="*40)
        print(f"{year}, {positions}, {locale.currency(payroll, grouping=True)}, {pct_increase}")
        print("\n\n")

        last_payroll = payroll

