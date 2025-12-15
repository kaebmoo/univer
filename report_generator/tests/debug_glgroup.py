#!/usr/bin/env python3
"""Debug GLGROUP SATELLITE values"""
import pandas as pd
from pathlib import Path
from src.data_loader import CSVLoader, DataProcessor, DataAggregator

# Load and process GLGROUP data
loader = CSVLoader(encoding='tis-620')
df = loader.load_csv(Path('data/TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv'))

print("Before processing:")
satellite_before = df[df['SERVICE_GROUP'].str.contains('SATELLITE', na=False)]['SERVICE_GROUP'].value_counts()
print(satellite_before)

processor = DataProcessor()
df = processor.process_data(df)

print("\nAfter processing:")
satellite_after = df[df['SERVICE_GROUP'].str.contains('SATELLITE|Satellite', na=False)]['SERVICE_GROUP'].value_counts()
print(satellite_after)

# Build aggregator
aggregator = DataAggregator(df)

# Test getting SATELLITE summary
print("\n" + "="*80)
print("Testing aggregator.get_satellite_summary():")
print("="*80)

# For row "รายได้" (first row in GLGROUP)
# GROUP = "01.รายได้", SUB_GROUP = None
group = "01.รายได้"
sub_group = None
bu = "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND"

print(f"\nGroup: {group}")
print(f"Sub_group: {sub_group}")
print(f"BU: {bu}")

# Test individual SG values
from config.satellite_config import get_satellite_service_group_names
satellite_sgs = get_satellite_service_group_names()

print(f"\nIndividual SERVICE_GROUP values:")
for sg in satellite_sgs:
    value = aggregator.get_value(group, sub_group, bu, sg)
    print(f"  {sg:50s}: {value:,.2f}")

# Test summary
summary = aggregator.get_satellite_summary(group, sub_group, bu)
print(f"\nSummary (get_satellite_summary): {summary:,.2f}")

# Check data directly
print("\n" + "="*80)
print("Raw data check:")
print("="*80)

# Filter for SATELLITE rows
sat_df = df[df['SERVICE_GROUP'].str.contains('Satellite', na=False)]
sat_df_bu = sat_df[sat_df['BU'] == bu]
sat_df_group = sat_df_bu[sat_df_bu['GROUP'] == group]

print(f"\nSATELLITE rows matching GROUP='{group}' and BU='{bu}':")
print(f"Total rows: {len(sat_df_group)}")
print(f"Total VALUE: {sat_df_group['VALUE'].sum():,.2f}")

if len(sat_df_group) > 0:
    print(f"\nBreakdown by SERVICE_GROUP:")
    for sg in sat_df_group['SERVICE_GROUP'].unique():
        sg_sum = sat_df_group[sat_df_group['SERVICE_GROUP'] == sg]['VALUE'].sum()
        print(f"  {sg:50s}: {sg_sum:,.2f}")
