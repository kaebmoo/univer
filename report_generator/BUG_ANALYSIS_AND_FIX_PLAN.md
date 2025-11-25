# Bug Analysis and Fix Plan

**Date:** 2025-11-25

**Subject:** Incorrect Sub-Group Data Mapping in Costtype Report

---

## 1. Bug Summary

The program incorrectly maps data for sub-groups (`sub_group`) when generating `costtype` reports. Sub-group items under "4.ค่าใช้จ่ายขายและการตลาด :" and "6.ค่าใช้จ่ายบริหารและสนับสนุน :" are being populated with data belonging to "2.ต้นทุนบริการและต้นทุนขาย :".

This happens because when a sub-group has the same name in different main groups (e.g., "- ค่าใช้จ่ายตอบแทนแรงงาน"), the program always retrieves the data associated with main group "02.ต้นทุนบริการและต้นทุนขาย :".

## 2. Root Cause Analysis

The investigation of `config/data_mapping.py`, `src/data_loader/data_aggregator.py`, and `src/excel_generator/excel_generator.py` confirms that the issue stems from a design flaw in how data is mapped. The system lacks context awareness.

### Key Files Involved:

1.  **`config/data_mapping.py` (Primary Cause):**
    -   The `ROW_TO_CSV_MAPPING` is a flat Python dictionary that maps a row label (e.g., `"- ค่าใช้จ่ายตอบแทนแรงงาน"`) to a single `(GROUP, SUB_GROUP)` tuple.
    -   Since dictionary keys must be unique, there can only be one entry for `"- ค่าใช้จ่ายตอบแทนแรงงาน"`. In the current implementation, it's hardcoded to the values for group `02`:
        ```python
        # from config/data_mapping.py
        ROW_TO_CSV_MAPPING = {
            ...
            "- ค่าใช้จ่ายตอบแทนแรงงาน": ("02.ต้นทุนบริการและต้นทุนขาย :", "01.ค่าใช้จ่ายตอบแทนแรงงาน"),
            ...
        }
        ```
    -   The function `get_group_sub_group(row_label: str)` only accepts the row label as an argument. It has no information about which main group (02, 04, or 06) it is currently processing, so it always returns the same hardcoded tuple from the map.

2.  **`src/excel_generator/excel_generator.py`:**
    -   The `_write_data_rows` method iterates through the report structure defined in `config/row_order.py`.
    -   While looping, it correctly processes main groups (level 0) and sub-items (level 1), but it does **not** keep track of the current main group's context.
    -   When it calls `aggregator.get_row_data(label, ...)` for a sub-item, it only passes the sub-item's label, without telling the aggregator which main group it belongs to.

3.  **`src/data_loader/data_aggregator.py`:**
    -   The `get_row_data` method receives the sub-item label and calls `get_group_sub_group(row_label)`.
    -   As established, this function returns incorrect `GROUP` information for items under groups 04 and 06.
    -   Consequently, `get_row_data` requests data from the database lookup using the correct `SUB_GROUP` name but the wrong `GROUP` ID, resulting in the bug.

---

## 3. Proposed Fix

To fix this, we must introduce "context" (the current main group) into the data retrieval process. This requires changes in three files.

### Step 1: Modify `excel_generator/excel_generator.py`

In the `_write_data_rows` method, we need to track the current main group while iterating through the rows.

**File:** `src/excel_generator/excel_generator.py`
**Method:** `_write_data_rows`

**Current Logic (Simplified):**
```python
        all_row_data = {}

        for row_def in rows:
            label = row_def['label']
            ...
            # No context of the main group is tracked or passed
            if is_calculated_row(label):
                ...
            else:
                row_data = aggregator.get_row_data(label, bu_list, service_group_dict)
```

**Proposed Change:**
Track the current level 0 group and pass its label to the aggregator.
```python
        all_row_data = {}
        current_main_group_label = None # <-- ADD: Variable to track context

        for row_def in rows:
            label = row_def['label']

            # ADD: Update context when a main group is found
            if row_def['level'] == 0:
                current_main_group_label = label

            ...
            if is_calculated_row(label):
                ...
            else:
                # MODIFIED: Pass the main group context to the aggregator
                row_data = aggregator.get_row_data(label, current_main_group_label, bu_list, service_group_dict)
```

### Step 2: Modify `data_loader/data_aggregator.py`

Update `get_row_data` to accept the new context and pass it to the mapping function.

**File:** `src/data_loader/data_aggregator.py`
**Method:** `get_row_data`

**Current Signature:**
```python
    def get_row_data(
        self,
        row_label: str,
        bu_list: List[str],
        service_group_dict: Dict[str, List[str]]
    ) -> Dict[str, float]:
```

**Proposed Change:**
```python
    def get_row_data(
        self,
        row_label: str,
        main_group_label: str, # <-- ADD: New parameter for context
        bu_list: List[str],
        service_group_dict: Dict[str, List[str]]
    ) -> Dict[str, float]:
```
Then, inside this method, modify the call to `get_group_sub_group`.

**Current Call:**
```python
        # Get GROUP and SUB_GROUP for this row
        group, sub_group = get_group_sub_group(row_label)
```

**Proposed Change:**
```python
        # Get GROUP and SUB_GROUP for this row, providing context
        group, sub_group = get_group_sub_group(row_label, main_group_label)
```

### Step 3: Modify `config/data_mapping.py` (The Core Fix)

The data structure and lookup function must be fundamentally changed.

**File:** `config/data_mapping.py`

**Proposed Change 1: Restructure the mapping.**
The `ROW_TO_CSV_MAPPING` is not flexible enough. It should be replaced with a nested structure that understands parent-child relationships. This is the cleanest solution.

**Example of New Structure:**
```python
# A new, more structured mapping
CONTEXTUAL_MAPPING = {
    "2.ต้นทุนบริการและต้นทุนขาย :": {
        "GROUP_ID": "02.ต้นทุนบริการและต้นทุนขาย :",
        "SUB_GROUPS": {
            "- ค่าใช้จ่ายตอบแทนแรงงาน": "01.ค่าใช้จ่ายตอบแทนแรงงาน",
            "- ค่าสวัสดิการ": "03.ค่าสวัสดิการ",
            # ...and so on for group 02
        }
    },
    "4.ค่าใช้จ่ายขายและการตลาด :": {
        "GROUP_ID": "04.ค่าใช้จ่ายขายและการตลาด :",
        "SUB_GROUPS": {
            "- ค่าใช้จ่ายตอบแทนแรงงาน": "01.ค่าใช้จ่ายตอบแทนแรงงาน",
            "- ค่าสวัสดิการ": "03.ค่าสวัสดิการ",
            "- ค่าใช้จ่ายการตลาดและส่งเสริมการขาย": "07.ค่าใช้จ่ายการตลาดและส่งเสริมการขาย",
            # ...and so on for group 04
        }
    },
    "6.ค่าใช้จ่ายบริหารและสนับสนุน :": {
        "GROUP_ID": "06.ค่าใช้จ่ายบริหารและสนับสนุน :",
        "SUB_GROUPS": {
            "- ค่าใช้จ่ายตอบแทนแรงงาน": "01.ค่าใช้จ่ายตอบแทนแรงงาน",
            "- ค่าสวัสดิการ": "03.ค่าสวัสดิการ",
            "- ค่าใช้จ่ายเผยแพร่ประชาสัมพันธ์": "08.ค่าใช้จ่ายเผยแพร่ประชาสัมพันธ์",
            # ...and so on for group 06
        }
    },
    # Other main groups that don't have sub-items can be mapped directly
    "7.ต้นทุนทางการเงิน-ด้านการดำเนินงาน": {
        "GROUP_ID": "07.ต้นทุนทางการเงิน-ด้านการดำเนินงาน",
        "SUB_GROUPS": {} # No sub-groups
    }
}
```

**Proposed Change 2: Re-implement the lookup function.**
The `get_group_sub_group` function needs to be rewritten to use this new structure and accept the context.

**Current Function:**
```python
def get_group_sub_group(row_label: str) -> tuple:
    if row_label in ROW_TO_CSV_MAPPING:
        return ROW_TO_CSV_MAPPING[row_label]
    ...
```

**Proposed New Function:**
```python
def get_group_sub_group(row_label: str, main_group_label: str) -> tuple:
    """
    Get GROUP and SUB_GROUP for a row label using context.
    """
    if not main_group_label:
        # Could be a main group itself or a row without a parent
        mapping = CONTEXTUAL_MAPPING.get(row_label)
        if mapping:
            # This is a main group, it has no sub_group in this context
            return (mapping["GROUP_ID"], None)
        else:
            return (None, None) # Or handle other cases

    # This is a sub-item, look inside its main group's context
    main_group_mapping = CONTEXTUAL_MAPPING.get(main_group_label)
    if main_group_mapping:
        group_id = main_group_mapping["GROUP_ID"]
        sub_group_id = main_group_mapping["SUB_GROUPS"].get(row_label)
        if sub_group_id:
            return (group_id, sub_group_id)

    return (None, None) # Fallback
```

---
**Disclaimer:** This report outlines the analysis and a detailed plan for fixing the bug. As per your instructions, **no changes have been made to the source code.** The proposed changes are ready for your review.
