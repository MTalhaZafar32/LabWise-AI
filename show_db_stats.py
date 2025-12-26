import sqlite3

conn = sqlite3.connect('data/labwise.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print('=== DATABASE STRUCTURE ===\n')
print(f'Total Tables: {len(tables)}\n')

total_rows = 0
for table in tables:
    table_name = table[0]
    
    # Get row count
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cursor.fetchone()[0]
    total_rows += count
    
    # Get column info
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    
    print(f'Table: {table_name}')
    print(f'  Rows: {count}')
    print(f'  Columns: {len(columns)}')
    print(f'  Column names: {[col[1] for col in columns]}')
    print()

print(f'=== TOTAL ROWS ACROSS ALL TABLES: {total_rows} ===')

conn.close()
