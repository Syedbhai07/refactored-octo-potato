# Jio Mobile Number Extractor

Extract the **first Jio mobile number** for every name in a CSV or Excel file and copy them all into a single output column.

## Files

| File | Description |
|---|---|
| `extract_jio_numbers.py` | Main Python script |
| `sample_data.csv` | Sample input file with names and multiple mobile numbers |

## Requirements

```
python 3.7+
openpyxl   # only needed for .xlsx / .xls input files
```

Install optional dependency:

```bash
pip install openpyxl
```

## Input format

The input file must have:

- **Column 1** – Name
- **Remaining columns** – Mobile numbers (one per cell, or several numbers comma-/space-separated in the same cell)

Example (`sample_data.csv`):

```
Name,Number1,Number2,Number3,Number4
Ali Ahmed,9876543210,6234567890,8765432109,7012345678
Sara Khan,6398765432,9845671230,7234567891,8345678901
...
```

## Usage

```bash
# Use the bundled sample file
python extract_jio_numbers.py

# Specify your own CSV file
python extract_jio_numbers.py --input your_file.csv

# Specify your own Excel file
python extract_jio_numbers.py --input your_file.xlsx

# Choose a custom output path
python extract_jio_numbers.py --input your_file.csv --output result.csv
```

## Output

A CSV file with two columns – **Name** and **First\_Jio\_Number** – is created next to your input file.  
The script also prints the single column of Jio numbers directly to the terminal so you can copy-paste it instantly.

Example terminal output:

```
Output written to: sample_data_jio_numbers.csv
Total names processed: 10
Names with a Jio number: 10

--- First Jio Number (one per name) ---
First_Jio_Number
9876543210
6398765432
6512345678
...
```

## How Jio numbers are identified

The script checks the first **4 digits** of every 10-digit mobile number against the Jio number series allocated by TRAI / DoT:

| Series | Range |
|---|---|
| 6xxx | 6000 – 6999 (all Jio) |
| 7xxx | 7000–7099, 7200–7399, 7700–7899, 7900–7999 |
| 8xxx | 8200–8499 |
| 9xxx | 9600–9899 |

To add or remove prefixes, edit the `_build_jio_prefixes()` function in `extract_jio_numbers.py`.
