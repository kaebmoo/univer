#!/usr/bin/env python3
"""Test SATELLITE splitting"""
import pandas as pd
from pathlib import Path
from src.data_loader import CSVLoader, DataProcessor

# Load data
loader = CSVLoader(encoding='tis-620')
df = loader.load_csv(Path('data/TRN_PL_COSTTYPE_NT_YTD_TABLE_20251031.csv'))

print('Before processing:')
satellite_before = df[df['SERVICE_GROUP'].str.contains('SATELLITE', na=False)]['SERVICE_GROUP'].value_counts()
print(satellite_before)
print(f'\nTotal SATELLITE rows: {satellite_before.sum()}')

# Process data
processor = DataProcessor()
df = processor.process_data(df)

print('\n' + '='*70)
print('After processing:')
satellite_after = df[df['SERVICE_GROUP'].str.contains('SATELLITE|Satellite', na=False)]['SERVICE_GROUP'].value_counts()
print(satellite_after)
print(f'\nTotal SATELLITE rows: {satellite_after.sum()}')

# Check for product keys
print('\n' + '='*70)
print('Sample SATELLITE rows after split:')
sample = df[df['SERVICE_GROUP'].str.contains('SATELLITE|Satellite', na=False)][['SERVICE_GROUP', 'PRODUCT_KEY', 'PRODUCT_NAME']].head(20)
print(sample.to_string())
