"""
Tests for extract_jio_numbers.py
"""
import csv
import os
import tempfile
import pytest

from extract_jio_numbers import (
    is_jio_number,
    extract_numbers_from_cell,
    process,
    write_output,
)


# ---------------------------------------------------------------------------
# is_jio_number
# ---------------------------------------------------------------------------

class TestIsJioNumber:
    def test_6xxx_series_is_jio(self):
        assert is_jio_number('6234567890')
        assert is_jio_number('6000000000')
        assert is_jio_number('6999999999')

    def test_7xxx_jio_sub_ranges(self):
        assert is_jio_number('7012345678')   # 7000-7099
        assert is_jio_number('7234567891')   # 7200-7399
        assert is_jio_number('7712345678')   # 7700-7799
        assert is_jio_number('7845612390')   # 7800-7899
        assert is_jio_number('7912345678')   # 7900-7999

    def test_8xxx_jio_sub_ranges(self):
        assert is_jio_number('8234567890')   # 8200-8499

    def test_9xxx_jio_sub_ranges(self):
        assert is_jio_number('9634567890')   # 9600-9699
        assert is_jio_number('9712345678')   # 9700-9799
        assert is_jio_number('9812345678')   # 9800-9899

    def test_non_jio_numbers(self):
        assert not is_jio_number('9123456789')   # 9100 not Jio
        assert not is_jio_number('8901234567')   # 8900 not Jio
        assert not is_jio_number('7512345678')   # 7500 not Jio
        assert not is_jio_number('5000000000')   # 5xxx not mobile

    def test_country_code_stripped(self):
        assert is_jio_number('916234567890')   # 91 + 10 digits
        assert is_jio_number('+916234567890')

    def test_short_number_returns_false(self):
        assert not is_jio_number('12345')
        assert not is_jio_number('')


# ---------------------------------------------------------------------------
# extract_numbers_from_cell
# ---------------------------------------------------------------------------

class TestExtractNumbersFromCell:
    def test_single_number(self):
        assert extract_numbers_from_cell('6234567890') == ['6234567890']

    def test_multiple_numbers_comma_separated(self):
        nums = extract_numbers_from_cell('6234567890, 9876543210')
        assert '6234567890' in nums
        assert '9876543210' in nums

    def test_with_country_code(self):
        nums = extract_numbers_from_cell('+916234567890')
        assert len(nums) == 1

    def test_empty_cell(self):
        assert extract_numbers_from_cell('') == []
        assert extract_numbers_from_cell(None) == []


# ---------------------------------------------------------------------------
# process
# ---------------------------------------------------------------------------

class TestProcess:
    def _make_rows(self, data):
        """Helper: prepend header row."""
        return [['Name', 'Num1', 'Num2', 'Num3']] + data

    def test_returns_first_jio_number(self):
        rows = self._make_rows([
            ['Alice', '9001234567', '6234567890', '8901234567'],
        ])
        results = process(rows)
        assert results == [('Alice', '6234567890')]

    def test_no_jio_number_gives_empty_string(self):
        rows = self._make_rows([
            ['Bob', '9001234567', '8901234567'],
        ])
        results = process(rows)
        assert results == [('Bob', '')]

    def test_first_jio_not_later_one(self):
        rows = self._make_rows([
            ['Carol', '6712345678', '6888888888'],
        ])
        results = process(rows)
        # First Jio number must be returned, not the second
        assert results[0][1] == '6712345678'

    def test_header_row_skipped(self):
        rows = [
            ['Name', 'Number1'],
            ['Dave', '6234567890'],
        ]
        results = process(rows)
        assert len(results) == 1
        assert results[0][0] == 'Dave'

    def test_blank_rows_skipped(self):
        rows = [
            ['Name', 'Number1'],
            ['', ''],
            ['Eve', '6234567890'],
        ]
        results = process(rows)
        assert len(results) == 1

    def test_multiple_names(self):
        rows = self._make_rows([
            ['Alice', '9001234567', '6234567890'],
            ['Bob',   '6712345678', '8901234567'],
            ['Carol', '9001234567', '9001234568'],
        ])
        results = process(rows)
        assert results[0] == ('Alice', '6234567890')
        assert results[1] == ('Bob',   '6712345678')
        assert results[2] == ('Carol', '')


# ---------------------------------------------------------------------------
# write_output
# ---------------------------------------------------------------------------

class TestWriteOutput:
    def test_csv_written_correctly(self, tmp_path):
        results = [('Alice', '6234567890'), ('Bob', '')]
        out = str(tmp_path / 'out.csv')
        write_output(results, out)

        assert os.path.isfile(out)
        with open(out, newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))

        assert rows[0] == ['Name', 'First_Jio_Number']
        assert rows[1] == ['Alice', '6234567890']
        assert rows[2] == ['Bob', '']
