import pandas as pd

# Load the CSV files
ranges_df = pd.read_csv('Knowladge-base/LabWise AI KB - test_ranges.csv')
tests_df = pd.read_csv('Knowladge-base/LabWise AI KB - tests.csv')

print(f"Total rows in test_ranges.csv: {len(ranges_df)}")
print(f"Rows with NA test_id: {ranges_df['test_id'].isna().sum()}")
print(f"Rows with valid test_id: {ranges_df['test_id'].notna().sum()}")

print("\n=== Sample rows with NA test_id ===")
na_rows = ranges_df[ranges_df['test_id'].isna()][['range_id', 'test_id', 'canonical_name', 'unit', 'source_id']].head(10)
print(na_rows.to_string())

print("\n=== Tests in tests.csv ===")
print(f"Total tests: {len(tests_df)}")
print(f"Test IDs range: {tests_df['test_id'].min()} to {tests_df['test_id'].max()}")

print("\n=== Unique canonical names in ranges with NA test_id ===")
na_canonical = ranges_df[ranges_df['test_id'].isna()]['canonical_name'].unique()
print(f"Count: {len(na_canonical)}")
print(na_canonical[:20])
