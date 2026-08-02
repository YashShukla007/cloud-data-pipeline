"""
Unit Tests for Cloud Data Pipeline
====================================
Tests the clean_data() function independently from AWS.

WHY TESTS MATTER (say this in interview):
"I wrote unit tests to ensure the cleaning logic works correctly
in isolation, before deploying to AWS. This way I could catch bugs
locally without wasting Lambda invocations."

HOW TO RUN:
    pip install pytest
    pytest local_test/test_pipeline.py -v
"""

import pytest
import pandas as pd
import sys
import os

# Import our function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))
from lambda_function import clean_data


class TestCleanData:
    """Group all tests for clean_data() function."""

    def test_removes_duplicate_rows(self):
        """Duplicate rows should be removed, keeping only one."""
        df = pd.DataFrame({
            'name': ['Alice', 'Alice', 'Bob'],
            'age':  [21, 21, 22]
        })
        cleaned, report = clean_data(df)
        assert len(cleaned) == 2, "Should have 2 rows after removing 1 duplicate"
        assert report['duplicates_removed'] == 1

    def test_strips_column_name_whitespace(self):
        """Column names with spaces/caps should be normalized."""
        df = pd.DataFrame({' Name ': ['Alice'], 'AGE': [21], ' Score': [90]})
        cleaned, report = clean_data(df)
        assert 'name' in cleaned.columns
        assert 'age' in cleaned.columns
        assert 'score' in cleaned.columns

    def test_strips_string_value_whitespace(self):
        """String values with leading/trailing spaces should be stripped."""
        df = pd.DataFrame({'name': ['  Alice  ', ' Bob'], 'age': [21, 22]})
        cleaned, report = clean_data(df)
        assert cleaned['name'].iloc[0] == 'Alice'
        assert cleaned['name'].iloc[1] == 'Bob'

    def test_fills_missing_numeric_with_median(self):
        """Missing numeric values should be filled with column median."""
        df = pd.DataFrame({
            'name':  ['Alice', 'Bob', 'Charlie'],
            'score': [80.0, None, 90.0]   # median = 85
        })
        cleaned, report = clean_data(df)
        assert cleaned['score'].isnull().sum() == 0, "No nulls should remain"
        assert cleaned['score'].iloc[1] == 85.0, "Should be filled with median (85)"

    def test_fills_missing_text_with_unknown(self):
        """Missing text values should be filled with 'Unknown'."""
        df = pd.DataFrame({
            'name':       ['Alice', None, 'Charlie'],
            'department': ['CS', 'ECE', None]
        })
        cleaned, report = clean_data(df)
        assert cleaned['name'].iloc[1] == 'Unknown'
        assert cleaned['department'].iloc[2] == 'Unknown'

    def test_removes_fully_empty_rows(self):
        """Rows where every column is NaN should be removed."""
        df = pd.DataFrame({
            'name':  ['Alice', None, 'Bob'],
            'age':   [21, None, 22],
            'score': [85, None, 90]
        })
        cleaned, report = clean_data(df)
        # The all-None row should be removed
        assert len(cleaned) == 2

    def test_clean_data_returns_report(self):
        """clean_data should always return a report dict."""
        df = pd.DataFrame({'name': ['Alice'], 'age': [21]})
        cleaned, report = clean_data(df)
        assert isinstance(report, dict)
        assert 'duplicates_removed' in report
        assert 'cleaning_steps' in report

    def test_empty_dataframe(self):
        """Should handle empty DataFrames without crashing."""
        df = pd.DataFrame({'name': [], 'age': []})
        cleaned, report = clean_data(df)
        assert len(cleaned) == 0

    def test_all_clean_data_unchanged(self):
        """Perfectly clean data should pass through unchanged."""
        df = pd.DataFrame({
            'name':  ['Alice', 'Bob'],
            'age':   [21, 22],
            'score': [85.0, 90.0]
        })
        cleaned, report = clean_data(df)
        assert len(cleaned) == 2
        assert report['duplicates_removed'] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
