import pandas as pd

df = pd.read_csv('Knowladge-base/LabWise AI KB - tests.csv')
print('Test IDs in use:')
print(sorted(df['test_id'].tolist()))
print(f'\nMax test_id: {df["test_id"].max()}')
print(f'Min test_id: {df["test_id"].min()}')
print(f'Total tests: {len(df)}')

# Check for gaps
all_ids = set(df['test_id'].tolist())
expected_ids = set(range(1, df['test_id'].max() + 1))
gaps = expected_ids - all_ids
if gaps:
    print(f'\nGaps in test_id sequence: {sorted(gaps)}')
else:
    print('\nNo gaps in test_id sequence')
