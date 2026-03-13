"""
extract_jio_numbers.py
======================
Reads a CSV or Excel file that contains names and multiple mobile numbers,
identifies which numbers belong to the Jio network, and writes the FIRST
Jio number found for each name into a single output column.

Input format (CSV or Excel):
  - First column  : Name
  - Other columns : Mobile numbers (one number per cell, or multiple
                    numbers separated by commas/spaces in a single cell)

Output:
  - A CSV file with two columns: Name, First_Jio_Number

Usage:
  python extract_jio_numbers.py                       # uses sample_data.csv
  python extract_jio_numbers.py --input my_file.csv
  python extract_jio_numbers.py --input my_file.xlsx
"""

import csv
import re
import argparse
import os
import sys

# ---------------------------------------------------------------------------
# Jio number identification
# ---------------------------------------------------------------------------
# In India, Reliance Jio mobile numbers are 10-digit numbers.
# The full set of Jio number-series prefixes (first 4 digits) published by
# TRAI / DoT.  Numbers whose first 4 digits appear in this set are Jio.
# Numbers starting with the digit 6 are exclusively allocated to Jio.
# ---------------------------------------------------------------------------

# Build the Jio prefix set from the known allocated ranges.
def _build_jio_prefixes():
    prefixes = set()

    # All 6xxx series belong to Jio
    for x in range(6000, 7000):
        prefixes.add(str(x))

    # 7xxx Jio sub-ranges
    jio_7xxx = [
        range(7000, 7100),   # 7000-7099
        range(7200, 7400),   # 7200-7399
        range(7700, 7900),   # 7700-7899
        range(7900, 8000),   # 7900-7999
    ]
    for r in jio_7xxx:
        for x in r:
            prefixes.add(str(x))

    # 8xxx Jio sub-ranges
    jio_8xxx = [
        range(8200, 8500),   # 8200-8499
    ]
    for r in jio_8xxx:
        for x in r:
            prefixes.add(str(x))

    # 9xxx Jio sub-ranges
    jio_9xxx = [
        range(9600, 9900),   # 9600-9899
    ]
    for r in jio_9xxx:
        for x in r:
            prefixes.add(str(x))

    return prefixes


JIO_PREFIXES = _build_jio_prefixes()


def is_jio_number(number: str) -> bool:
    """Return True if *number* is a Jio mobile number."""
    digits = re.sub(r'\D', '', number)  # strip non-digits
    # Indian mobile numbers are 10 digits; with country code they are 12
    if len(digits) == 12 and digits.startswith('91'):
        digits = digits[2:]
    if len(digits) != 10:
        return False
    return digits[:4] in JIO_PREFIXES


def extract_numbers_from_cell(cell_value: str) -> list:
    """Return all 10-digit (or +91 prefixed) mobile numbers found in a cell."""
    if not cell_value:
        return []
    # Match 10-digit numbers optionally preceded by +91 or 91
    pattern = r'(?:(?:\+91|91)?[6-9]\d{9})'
    return re.findall(pattern, str(cell_value))


# ---------------------------------------------------------------------------
# File reading helpers
# ---------------------------------------------------------------------------

def read_csv(filepath: str) -> list:
    """Return list of rows (each row is a list of strings)."""
    rows = []
    with open(filepath, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
    return rows


def read_excel(filepath: str) -> list:
    """Return list of rows from the first sheet of an Excel file."""
    try:
        import openpyxl
    except ImportError:
        print("openpyxl is required to read Excel files.  "
              "Install it with:  pip install openpyxl")
        sys.exit(1)
    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    ws = wb.active
    rows = []
    for row in ws.iter_rows(values_only=True):
        rows.append([str(cell) if cell is not None else '' for cell in row])
    wb.close()
    return rows


def load_file(filepath: str) -> list:
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ('.xlsx', '.xls', '.xlsm'):
        return read_excel(filepath)
    return read_csv(filepath)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def process(rows: list) -> list:
    """
    Given a list of rows (first column = name, remaining columns = numbers),
    return a list of (name, first_jio_number) tuples.

    The header row (if present) is detected automatically and skipped.
    If no Jio number is found for a name, first_jio_number is empty string.
    """
    results = []
    header_skipped = False

    for row in rows:
        if not any(cell.strip() for cell in row):
            continue  # skip blank rows

        name_cell = row[0].strip() if row else ''
        if not name_cell:
            continue

        # Skip the header row
        if not header_skipped and re.match(r'(?i)^name', name_cell):
            header_skipped = True
            continue

        # Gather all numbers from the remaining columns
        all_numbers = []
        for cell in row[1:]:
            all_numbers.extend(extract_numbers_from_cell(cell))

        # Find the first Jio number
        first_jio = ''
        for num in all_numbers:
            digits = re.sub(r'\D', '', num)
            if len(digits) == 12 and digits.startswith('91'):
                digits = digits[2:]
            if is_jio_number(digits):
                first_jio = digits
                break

        results.append((name_cell, first_jio))

    return results


def write_output(results: list, output_path: str):
    """Write (name, first_jio_number) pairs to a CSV file."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'First_Jio_Number'])
        for name, jio_num in results:
            writer.writerow([name, jio_num])
    print(f"Output written to: {output_path}")
    print(f"Total names processed: {len(results)}")
    found = sum(1 for _, n in results if n)
    print(f"Names with a Jio number: {found}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Extract the first Jio mobile number for each name.')
    parser.add_argument(
        '--input', '-i',
        default='sample_data.csv',
        help='Input CSV or Excel file (default: sample_data.csv)')
    parser.add_argument(
        '--output', '-o',
        default='',
        help='Output CSV file (default: <input>_jio_numbers.csv)')
    args = parser.parse_args()

    input_path = args.input
    if not os.path.isfile(input_path):
        print(f"Error: input file not found: {input_path}")
        sys.exit(1)

    output_path = args.output or (
        os.path.splitext(input_path)[0] + '_jio_numbers.csv')

    rows = load_file(input_path)
    results = process(rows)
    write_output(results, output_path)

    # Print the single-column result so it can be copied directly
    print("\n--- First Jio Number (one per name) ---")
    print("First_Jio_Number")
    for _, jio_num in results:
        print(jio_num if jio_num else '(none)')


if __name__ == '__main__':
    main()
