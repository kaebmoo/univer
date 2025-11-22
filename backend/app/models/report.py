"""
Report Models
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ReportFilter(BaseModel):
    """Report filter parameters"""
    year: int = Field(..., ge=2020, le=2030, description="Report year")
    months: List[int] = Field(
        ...,
        min_length=1,
        max_length=12,
        description="List of months (1-12)"
    )
    business_groups: Optional[List[str]] = Field(
        default=None,
        description="List of business groups to filter (None = all groups)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2025,
                "months": [1, 2, 3],
                "business_groups": ["1 Hard Infrastructure", "2 International"]
            }
        }


class ReportMetrics(BaseModel):
    """Report metrics summary"""
    total_revenue: float = Field(..., description="Total revenue")
    total_cost_of_service: float = Field(..., description="Total cost of service")
    total_selling_cost: float = Field(..., description="Total selling & marketing cost")
    total_support_cost: float = Field(..., description="Total support cost")
    total_cost: float = Field(..., description="Total cost")
    ebit: float = Field(..., description="EBIT")
    ebitda: float = Field(..., description="EBITDA")
    gross_profit: float = Field(..., description="Gross profit")
    gross_profit_margin: float = Field(..., description="Gross profit margin %")
    ebit_margin: float = Field(..., description="EBIT margin %")
    ebitda_margin: float = Field(..., description="EBITDA margin %")


class ReportRow(BaseModel):
    """Single row in report"""
    row_number: int = Field(..., description="Row number in report")
    label: str = Field(..., description="Row label")
    month_value: float = Field(..., description="Month value")
    ytd_value: float = Field(..., description="YTD value")
    month_common_size: Optional[float] = Field(None, description="Month common size %")
    ytd_common_size: Optional[float] = Field(None, description="YTD common size %")
    is_header: bool = Field(default=False, description="Is this a header row")
    is_subtotal: bool = Field(default=False, description="Is this a subtotal row")
    is_total: bool = Field(default=False, description="Is this a total row")
    indent_level: int = Field(default=0, description="Indentation level")


class ReportData(BaseModel):
    """Complete report data"""
    filter: ReportFilter = Field(..., description="Filter used to generate report")
    metrics: ReportMetrics = Field(..., description="Summary metrics")
    rows: List[ReportRow] = Field(..., description="Report rows")
    generated_at: str = Field(..., description="Generation timestamp")


class UniverCell(BaseModel):
    """Single cell in Univer format"""
    v: Any = Field(..., description="Cell value")
    s: Optional[str] = Field(None, description="Style ID")
    f: Optional[str] = Field(None, description="Formula")


class UniverSheet(BaseModel):
    """Univer sheet data"""
    id: str = Field(..., description="Sheet ID")
    name: str = Field(..., description="Sheet name")
    cellData: Dict[int, Dict[int, UniverCell]] = Field(..., description="Cell data")
    rowCount: int = Field(default=100, description="Number of rows")
    columnCount: int = Field(default=20, description="Number of columns")
    mergeData: Optional[List[Dict[str, int]]] = Field(default=None, description="Merged cells")


class UniverWorkbook(BaseModel):
    """Univer workbook snapshot"""
    id: str = Field(..., description="Workbook ID")
    name: str = Field(..., description="Workbook name")
    appVersion: str = Field(default="0.1.0", description="App version")
    sheets: Dict[str, UniverSheet] = Field(..., description="Sheets in workbook")
    styles: Optional[Dict[str, Any]] = Field(default=None, description="Style definitions")


class ExportFormat(BaseModel):
    """Export format options"""
    format: str = Field(
        default="xlsx",
        description="Export format (xlsx, csv, pdf)"
    )
    include_formulas: bool = Field(
        default=False,
        description="Include formulas in export"
    )
    include_styles: bool = Field(
        default=True,
        description="Include cell styles"
    )


class FilterOptions(BaseModel):
    """Available filter options"""
    available_years: List[int] = Field(..., description="Available years")
    available_business_groups: List[str] = Field(..., description="Available business groups")
    available_services: List[str] = Field(..., description="Available services")
    min_date: str = Field(..., description="Minimum date in data")
    max_date: str = Field(..., description="Maximum date in data")
