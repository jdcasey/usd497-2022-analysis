#!/usr/bin/env python

import csv
import locale
import click
from ruamel.yaml import YAML

locale.setlocale(locale.LC_ALL, '')


@click.command()
@click.argument("positions")  #List of positions in admin office (from District Payroll CSV)
@click.argument("payroll")  #District Payroll CSV file (from KansasOpenGov.org)
@click.option("-c", "--category", default="Administration", help="Which category of payroll to produce")
@click.option("-o", "--output", default="Payroll.csv", help="Output CSV file")
def run(positions, payroll, category, output):
    with open(positions, 'r') as f:
        position_types = YAML().load(f)

    by_year = {}
    with open(payroll, newline='') as csvfile:
        reader = csv.reader(csvfile)
        header_passed = False
        for row in reader:
            if header_passed:
                salary = int(row[-1].replace("$", "").replace(",", ""))
                position = row[-2]
                year = int(row[0])

                for section, position_names in position_types.items():
                    for pos in position_names:
                        if pos in position:
                            year_data = by_year.get(year)
                            if year_data is None:
                                year_data = {}
                                by_year[year] = year_data

                            pos_data = year_data.get(section)
                            if pos_data is None:
                                pos_data = []
                                year_data[section] = pos_data

                            pos_data.append({'position': position, 'salary': salary})
            else:
                header_passed = True

    last_payrolls = {}
    last_counts = {}
    with open(output, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        header_row = ["Year"]
        for section in position_types.keys():
            header_row.append(f"# Positions, {section}")
            header_row.append(f"% Headcount Increase YoY, {section}")
            header_row.append(f"Payroll, {section}")
            header_row.append(f"% Payroll Increase YoY, {section}")

        csvwriter.writerow(header_row)

        for year in sorted(by_year.keys()):
            row = [str(year)]
            payrolls = {}
            counts = {}
            for section, data in by_year[year].items():

                for pos in sorted(data, key=lambda x: x['salary'], reverse=True):
                    print(f"{year}, {pos['position']}, {locale.currency(pos['salary'], grouping=True)}")

                payroll = sum([d['salary'] for d in data])
                count = len(data)

                last_payroll = last_payrolls.get(section)
                if last_payroll:
                    pct_increase = "%.2f" % ((payroll - last_payroll) / last_payroll * 100) + "%"
                else:
                    pct_increase = "0.00%"

                last_count = last_counts.get(section)
                if last_count:
                    pct_headcount_increase = "%.2f" % ((count - last_count) / last_count * 100) + "%"
                else:
                    pct_headcount_increase = "0.00%"

                row.append(locale.currency(payroll, grouping=True))
                row.append(pct_increase)
                row.append(str(count))
                row.append(pct_headcount_increase)

                payrolls[section] = payroll
                counts[section] = count

            csvwriter.writerow(row)
            print("=" * 40)

            print(row)
            row_fmt = ", ".join(row)
            print(row_fmt)
            print("\n\n")

            last_payroll = payrolls
            last_counts = counts


if __name__ == "__main__":
    run()
