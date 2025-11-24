"""
Tests for UniverConverter
"""

import pytest
from app.services.univer_converter import UniverConverter


@pytest.mark.unit
class TestUniverConverter:
    """Test cases for UniverConverter"""

    def test_converter_initialization(self, univer_converter):
        """Test converter initialization"""
        assert univer_converter is not None
        assert univer_converter.styles_registry == {}
        assert univer_converter.next_style_id == 0

    def test_register_style(self, univer_converter):
        """Test style registration"""
        style_def = {
            "bg": {"rgb": "#FF0000"},
            "bl": 1
        }

        style_id = univer_converter._register_style(style_def)

        assert style_id is not None
        assert style_id in univer_converter.styles_registry.values()

    def test_register_style_reuse(self, univer_converter):
        """Test that same style gets same ID"""
        style_def = {
            "bg": {"rgb": "#FF0000"},
            "bl": 1
        }

        style_id1 = univer_converter._register_style(style_def)
        style_id2 = univer_converter._register_style(style_def)

        assert style_id1 == style_id2

    def test_create_header_style(self, univer_converter):
        """Test header style creation"""
        style = univer_converter._create_header_style(
            bg_color="#4472C4",
            bold=True,
            font_color="#FFFFFF"
        )

        assert style is not None
        assert style["bg"]["rgb"] == "#4472C4"
        assert style["bl"] == 1
        assert style["fc"]["rgb"] == "#FFFFFF"

    def test_create_number_style(self, univer_converter):
        """Test number style creation"""
        style = univer_converter._create_number_style(
            number_format="#,##0.00",
            bg_color="#E7E6E6",
            bold=False
        )

        assert style is not None
        assert style["n"]["pattern"] == "#,##0.00"
        assert style["bg"]["rgb"] == "#E7E6E6"
        assert style["bl"] == 0

    def test_create_number_style_smart_positive(self, univer_converter):
        """Test smart number style with positive value"""
        style = univer_converter._create_number_style_smart(
            value=1000.50,
            bg_color="#FFFFFF",
            bold=False
        )

        assert style is not None
        assert "n" in style
        # Positive values should not have red color
        assert style.get("fc", {}).get("rgb") != univer_converter.COLORS["negative"]

    def test_create_number_style_smart_negative(self, univer_converter):
        """Test smart number style with negative value"""
        style = univer_converter._create_number_style_smart(
            value=-1000.50,
            bg_color="#FFFFFF",
            bold=False
        )

        assert style is not None
        assert "n" in style
        # Negative values should have red color
        assert style.get("fc", {}).get("rgb") == univer_converter.COLORS["negative"]

    def test_create_cell_with_string_value(self, univer_converter):
        """Test cell creation with string value"""
        cell = univer_converter._create_cell(
            row=0,
            col=0,
            value="Test String"
        )

        assert cell is not None
        assert cell["r"] == 0
        assert cell["c"] == 0
        assert cell["v"]["v"] == "Test String"
        assert cell["v"]["t"] == "s"

    def test_create_cell_with_numeric_value(self, univer_converter):
        """Test cell creation with numeric value"""
        cell = univer_converter._create_cell(
            row=1,
            col=1,
            value=12345.67
        )

        assert cell is not None
        assert cell["r"] == 1
        assert cell["c"] == 1
        assert cell["v"]["v"] == 12345.67
        assert cell["v"]["t"] == "n"

    def test_create_cell_with_style(self, univer_converter):
        """Test cell creation with style"""
        style = {"bg": {"rgb": "#FF0000"}}
        cell = univer_converter._create_cell(
            row=0,
            col=0,
            value="Styled Text",
            style=style
        )

        assert cell is not None
        assert "s" in cell["v"]  # Has style ID

    def test_convert_to_snapshot(self, univer_converter, mock_report_data):
        """Test conversion to Univer snapshot"""
        snapshot = univer_converter.convert_to_snapshot(
            report_data=mock_report_data,
            workbook_name="Test Report"
        )

        assert snapshot is not None
        assert "id" in snapshot
        assert snapshot["name"] == "Test Report"
        assert "styles" in snapshot
        assert "sheets" in snapshot

        # Check sheets
        assert "sheet-01" in snapshot["sheets"]
        sheet = snapshot["sheets"]["sheet-01"]

        assert "cellData" in sheet
        assert "rowCount" in sheet
        assert "columnCount" in sheet

    def test_convert_to_snapshot_with_negative_values(self, univer_converter, mock_negative_report_data):
        """Test conversion with negative values"""
        snapshot = univer_converter.convert_to_snapshot(
            report_data=mock_negative_report_data,
            workbook_name="Negative Test"
        )

        assert snapshot is not None

        # Find cells with negative values and check they have red styling
        sheet = snapshot["sheets"]["sheet-01"]
        cell_data = sheet["cellData"]

        negative_cells_found = False
        for row_idx, row_cells in cell_data.items():
            for col_idx, cell in row_cells.items():
                if "v" in cell and isinstance(cell.get("v"), (int, float)) and cell["v"] < 0:
                    negative_cells_found = True
                    # Check if cell has style
                    style_id = cell.get("s")
                    if style_id:
                        style = snapshot["styles"].get(style_id, {})
                        # Should have red font color or red format
                        has_red = (
                            style.get("fc", {}).get("rgb") == "#FF0000" or
                            "Red" in style.get("n", {}).get("pattern", "")
                        )
                        assert has_red, "Negative value should have red styling"

        # We should have found at least one negative cell in mock data
        assert negative_cells_found, "Test data should contain negative values"

    def test_build_cell_data(self, univer_converter):
        """Test building cell data structure"""
        cells = [
            {"r": 0, "c": 0, "v": {"v": "A1", "t": "s"}},
            {"r": 0, "c": 1, "v": {"v": "B1", "t": "s"}},
            {"r": 1, "c": 0, "v": {"v": "A2", "t": "s"}},
        ]

        cell_data = univer_converter._build_cell_data(cells)

        assert cell_data is not None
        assert 0 in cell_data
        assert 1 in cell_data
        assert 0 in cell_data[0]
        assert 1 in cell_data[0]
        assert 0 in cell_data[1]

    def test_build_styles_object(self, univer_converter):
        """Test building styles object"""
        # Register some styles
        style1 = {"bg": {"rgb": "#FF0000"}}
        style2 = {"bg": {"rgb": "#00FF00"}}

        univer_converter._register_style(style1)
        univer_converter._register_style(style2)

        styles = univer_converter._build_styles_object()

        assert styles is not None
        assert len(styles) == 2

    def test_color_constants(self, univer_converter):
        """Test that color constants are defined"""
        assert "header" in univer_converter.COLORS
        assert "revenue" in univer_converter.COLORS
        assert "cost_header" in univer_converter.COLORS
        assert "ebit" in univer_converter.COLORS
        assert "ebitda" in univer_converter.COLORS
        assert "negative" in univer_converter.COLORS

        # Check negative color is red
        assert univer_converter.COLORS["negative"] == "#FF0000"

    def test_number_format_constants(self, univer_converter):
        """Test that number format constants are defined"""
        assert "currency" in univer_converter.NUMBER_FORMATS
        assert "currency_negative" in univer_converter.NUMBER_FORMATS
        assert "currency_parentheses" in univer_converter.NUMBER_FORMATS
        assert "percentage" in univer_converter.NUMBER_FORMATS
        assert "percentage_negative" in univer_converter.NUMBER_FORMATS

        # Check negative formats contain [Red]
        assert "[Red]" in univer_converter.NUMBER_FORMATS["currency_negative"]
        assert "[Red]" in univer_converter.NUMBER_FORMATS["currency_parentheses"]

    def test_snapshot_structure_completeness(self, univer_converter, mock_report_data):
        """Test that snapshot contains all required revenue and cost items"""
        snapshot = univer_converter.convert_to_snapshot(
            report_data=mock_report_data,
            workbook_name="Complete Test"
        )

        sheet = snapshot["sheets"]["sheet-01"]
        cell_data = sheet["cellData"]

        # Count revenue items (should find Infrastructure, Mobile, etc.)
        revenue_items_found = 0
        for row_idx, row_cells in cell_data.items():
            if 0 in row_cells:
                cell_value = row_cells[0].get("v", "")
                if isinstance(cell_value, str):
                    if "โครงสร้างพื้นฐาน" in cell_value or "Infrastructure" in cell_value:
                        revenue_items_found += 1
                    elif "โทรศัพท์เคลื่อนที่" in cell_value or "Mobile" in cell_value:
                        revenue_items_found += 1

        # Should have some revenue items
        assert revenue_items_found > 0

    def test_indentation_in_cells(self, univer_converter, mock_report_data):
        """Test that sub-items have indentation"""
        snapshot = univer_converter.convert_to_snapshot(
            report_data=mock_report_data,
            workbook_name="Indentation Test"
        )

        sheet = snapshot["sheets"]["sheet-01"]
        cell_data = sheet["cellData"]

        # Find cells with indentation (4 spaces)
        indented_count = 0
        for row_idx, row_cells in cell_data.items():
            if 0 in row_cells:
                cell_value = row_cells[0].get("v", "")
                if isinstance(cell_value, str) and cell_value.startswith("    "):
                    indented_count += 1

        # Should have some indented items
        assert indented_count > 0
