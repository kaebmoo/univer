"""
SATELLITE Service Group Configuration
Configuration for splitting SATELLITE service group into sub-groups
"""

# Feature toggle - set to False to disable SATELLITE splitting
ENABLE_SATELLITE_SPLIT = True

# SATELLITE service group name in source data
SATELLITE_SOURCE_NAME = '4.5 กลุ่มบริการ SATELLITE'

# Sub-group definitions with PRODUCT_KEY mapping
SATELLITE_GROUPS = {
    'NT': {
        'name': '4.5.1 กลุ่มบริการ SATELLITE-NT',
        'product_keys': [
            '102010401',  # บริการ NT TV Transmission
            '102010402',  # บริการ NT GlobeSat
            '102010403',  # บริการ INMARSAT
            '102010404',  # บริการ NT iP Star
            '102010406',  # บริการ NT Satellite Platform
            '102010407',  # บริการ Ground Segment as a Service (GSaaS)
            '102010413',  # บริการ DTH Platform
            '102010414',  # Foreign Satellite Transponder
            '102010415',  # บริการ NT nexConnect
            '103010016',  # บริการ NT e-Entertainment
            '204060002',  # บริการสื่อสัญญาณถ่ายทอดภาพและเสียง (TV Encoder Decoder)
            '204070003',  # บริการ iP Star
        ]
    },
    'THAICOM': {
        'name': '4.5.2 กลุ่มบริการ SATELLITE-ไทยคม',
        'product_keys': [
            '102010409',  # Thaicom 4 Satellite Wholesale Transponder
            '102010410',  # Thaicom 4 Satellite Ratail Transponder
            '102010411',  # Thaicom 6 Satellite Wholesale Transponder
            '102010412',  # Thaicom 6 Satellite Ratail Transponder
        ]
    }
}

# Summary column name
SATELLITE_SUMMARY_NAME = 'รวม 4.5 SATELLITE'
SATELLITE_SUMMARY_ID = '4.5_SUMMARY'


def get_satellite_service_group_names():
    """
    Get list of satellite service group names

    Returns:
        List of service group names (e.g., ['4.5.1 ...', '4.5.2 ...'])
    """
    if not ENABLE_SATELLITE_SPLIT:
        return []
    return [group['name'] for group in SATELLITE_GROUPS.values()]


def get_satellite_product_keys():
    """
    Get mapping of service group names to their product keys

    Returns:
        Dict mapping SG name to list of product keys
    """
    if not ENABLE_SATELLITE_SPLIT:
        return {}

    mapping = {}
    for group_config in SATELLITE_GROUPS.values():
        mapping[group_config['name']] = group_config['product_keys']
    return mapping


def get_service_group_for_product_key(product_key: str):
    """
    Get service group name for a given product key

    Args:
        product_key: PRODUCT_KEY value (may be string or float like 102010401.0)

    Returns:
        Service group name or None if not found
    """
    if not ENABLE_SATELLITE_SPLIT:
        return None

    # Convert to string and handle float format (e.g., '102010401.0' -> '102010401')
    product_key_str = str(product_key).strip()

    # Remove .0 suffix if present (pandas may convert to float)
    if product_key_str.endswith('.0'):
        product_key_str = product_key_str[:-2]

    for group_config in SATELLITE_GROUPS.values():
        if product_key_str in group_config['product_keys']:
            return group_config['name']

    return None
