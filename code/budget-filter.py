#!/usr/bin/env python

import csv
import click
import locale

locale.setlocale(locale.LC_ALL, '')


@click.command()
@click.argument("budget")
@click.argument("output")
@click.option("-m", "--min-value", default=100000, help="Minimum line value for inclusion in output")
@click.option("-c", "--filter-column", default=6, help="1-based index of the column to filter on")
def run(budget, min_value, filter_column, output):
    row_col = filter_column-1
    output_rows = []
    header = None
    with open(budget, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if not header:
                header = row
            elif not all([i == j for i, j in zip(header, row)]):
                if "Total" not in row[0]:
                    val = row[row_col].replace("$", "").replace(",", "")
                    if len(val) > 0:
                        val = int(val)
                        if val >= min_value:
                            row[row_col] = val
                            output_rows.append(row)

    output_rows = sorted(output_rows, key=lambda x: x[row_col], reverse=True)
    for row in output_rows:
        for idx in range(row_col, len(row)):
            val = row[idx]
            if isinstance(val, int):
                row[idx] = locale.currency(val, grouping=True)
            else:
                val = val.replace("$", "").replace(",", "")

                if len(val) > 0:
                    row[idx] = locale.currency(int(val), grouping=True)


        print(row[row_col])

    with open(output, 'w') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        for row in output_rows:
            writer.writerow(row)


if __name__ == "__main__":
    run()