"""
Base Column Builder
Abstract base class for all column builders
"""
from abc import ABC, abstractmethod
from typing import List, Dict
import pandas as pd


class ColumnDef:
    """
    Column definition
    
    Attributes:
        name: Column display name
        col_type: Column type (label, grand_total, bu_total, sg_total, product)
        bu: Business unit (if applicable)
        service_group: Service group (if applicable)
        product_key: Product key (if applicable)
        product_name: Product name (if applicable)
        width: Column width
        color: Background color (hex without #)
    """
    
    def __init__(
        self,
        name: str,
        col_type: str,
        bu: str = None,
        service_group: str = None,
        product_key: str = None,
        product_name: str = None,
        width: int = 18,
        color: str = 'FFFFFF'
    ):
        self.name = name
        self.col_type = col_type
        self.bu = bu
        self.service_group = service_group
        self.product_key = product_key
        self.product_name = product_name
        self.width = width
        self.color = color
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'type': self.col_type,
            'bu': self.bu,
            'service_group': self.service_group,
            'product_key': self.product_key,
            'product_name': self.product_name,
            'width': self.width,
            'color': self.color
        }
    
    def __repr__(self) -> str:
        return f"ColumnDef(name='{self.name}', type='{self.col_type}')"


class BaseColumnBuilder(ABC):
    """
    Abstract base class for column builders
    
    Subclasses must implement build_columns() method
    """
    
    def __init__(self, config):
        """
        Initialize column builder
        
        Args:
            config: ReportConfig instance
        """
        self.config = config
    
    @abstractmethod
    def build_columns(self, data: pd.DataFrame) -> List[ColumnDef]:
        """
        Build column structure
        
        Args:
            data: Input dataframe
        
        Returns:
            List of ColumnDef objects
        """
        pass
    
    def _create_label_column(self) -> ColumnDef:
        """Create the label column (รายละเอียด)"""
        return ColumnDef(
            name='รายละเอียด',
            col_type='label',
            width=50,
            color=self.config.row_colors.get('detail_label', 'F4DEDC')
        )
    
    def _create_grand_total_column(self) -> ColumnDef:
        """Create the grand total column (รวมทั้งสิ้น)"""
        return ColumnDef(
            name='รวมทั้งสิ้น',
            col_type='grand_total',
            width=20,
            color=self.config.row_colors.get('grand_total', 'FFD966')
        )
    
    def _create_bu_total_column(self, bu: str) -> ColumnDef:
        """
        Create BU total column
        
        Args:
            bu: Business unit name
        
        Returns:
            ColumnDef for BU total
        """
        return ColumnDef(
            name=f'รวม {bu}',
            col_type='bu_total',
            bu=bu,
            width=18,
            color=self.config.bu_colors.get(bu, 'FFFFFF')
        )
    
    def _create_sg_total_column(self, bu: str, sg: str) -> ColumnDef:
        """
        Create Service Group total column
        
        Args:
            bu: Business unit name
            sg: Service group name
        
        Returns:
            ColumnDef for SG total
        """
        return ColumnDef(
            name=f'รวม {sg}',
            col_type='sg_total',
            bu=bu,
            service_group=sg,
            width=18,
            color=self.config.bu_colors.get(bu, 'FFFFFF')
        )
    
    def _create_product_column(
        self,
        bu: str,
        sg: str,
        product_key: str,
        product_name: str
    ) -> ColumnDef:
        """
        Create product column
        
        Args:
            bu: Business unit name
            sg: Service group name
            product_key: Product key
            product_name: Product name
        
        Returns:
            ColumnDef for product
        """
        return ColumnDef(
            name=product_name,
            col_type='product',
            bu=bu,
            service_group=sg,
            product_key=product_key,
            product_name=product_name,
            width=18,
            color=self.config.bu_colors.get(bu, 'FFFFFF')
        )
    
    def _create_common_size_column(self, bu: str = None) -> ColumnDef:
        """
        Create Common Size column
        
        Args:
            bu: Business unit name (optional, for BU-specific common size)
        
        Returns:
            ColumnDef for Common Size
        """
        return ColumnDef(
            name='Common Size',
            col_type='common_size',
            bu=bu,
            width=12,
            color=self.config.bu_colors.get(bu, 'FFFFFF') if bu else 'FFFFFF'
        )
