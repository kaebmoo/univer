"""
Pytest configuration and fixtures
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.auth_service import AuthService
from app.services.data_loader import DataLoader
from app.services.report_calculator import ReportCalculator
from app.services.univer_converter import UniverConverter


@pytest.fixture
def auth_service():
    """Create a fresh AuthService instance for each test"""
    return AuthService()


@pytest.fixture
def data_loader():
    """Create a DataLoader instance"""
    return DataLoader()


@pytest.fixture
def report_calculator():
    """Create a ReportCalculator instance"""
    return ReportCalculator()


@pytest.fixture
def univer_converter():
    """Create a UniverConverter instance"""
    return UniverConverter()


@pytest.fixture
def mock_otp_session():
    """Create a mock OTP session"""
    from app.models.auth import OTPSession
    from app.utils.otp import generate_secret, generate_totp

    # Generate a real TOTP secret and code for testing
    secret = generate_secret()
    otp_code, _ = generate_totp(secret, interval=300)

    return OTPSession(
        email="test@example.com",
        secret=secret,
        otp_code=otp_code,
        created_at=datetime.utcnow(),
        attempts=0,
        is_verified=False
    )


@pytest.fixture
def expired_otp_session():
    """Create an expired OTP session"""
    from app.models.auth import OTPSession
    from app.utils.otp import generate_secret, generate_totp

    # Generate a real TOTP secret and code for testing
    secret = generate_secret()
    otp_code, _ = generate_totp(secret, interval=300)

    return OTPSession(
        email="test@example.com",
        secret=secret,
        otp_code=otp_code,
        created_at=datetime.utcnow() - timedelta(minutes=10),
        attempts=0,
        is_verified=False
    )


@pytest.fixture
def mock_report_data():
    """Create mock report data for testing"""
    return {
        'data': {
            'revenue': {
                'Infrastructure': 1000000.00,
                'Fixed Line & Broadband': 2000000.00,
                'Mobile': 3000000.00,
                'International Circuit': 500000.00,
                'Digital': 750000.00,
                'ICT Solution': 1250000.00,
                'Non-Telecom Service': 300000.00,
                'Sale of Goods': 200000.00,
                'Total': 9000000.00
            },
            'cost_of_service': {
                'ค่าใช้จ่ายตอบแทนแรงงาน': 2000000.00,
                'ค่าสวัสดิการ': 500000.00,
                'ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร': 100000.00,
                'ค่าซ่อมแซมและบำรุงรักษาและวัสดุใช้ไป': 750000.00,
                'ค่าสาธารณูปโภค': 400000.00,
                'ค่าใช้จ่ายเกี่ยวกับการกำกับดูแลของ กสทช.': 200000.00,
                'ค่าส่วนแบ่งบริการโทรคมนาคม': 800000.00,
                'ค่าใช้จ่ายบริการโทรคมนาคม': 600000.00,
                'ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์': 1000000.00,
                'ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า': 250000.00,
                'ค่าเช่าและค่าใช้สินทรัพย์': 200000.00,
                'ต้นทุนขาย': 150000.00,
                'ค่าใช้จ่ายบริการอื่น': 100000.00,
                'ค่าใช้จ่ายดำเนินงานอื่น': 50000.00,
                'Total': 7100000.00
            },
            'metrics': {
                'gross_profit': 1900000.00,
                'ebit': 1500000.00,
                'ebitda': 2750000.00,
                'gross_margin': 21.11,
                'ebit_margin': 16.67,
                'ebitda_margin': 30.56
            }
        }
    }


@pytest.fixture
def mock_negative_report_data():
    """Create mock report data with negative values for testing"""
    return {
        'data': {
            'revenue': {
                'Infrastructure': 1000000.00,
                'Mobile': -500000.00,  # Negative revenue
                'Total': 500000.00
            },
            'cost_of_service': {
                'ค่าใช้จ่ายตอบแทนแรงงาน': 800000.00,
                'Total': 800000.00
            },
            'metrics': {
                'gross_profit': -300000.00,  # Negative profit
                'ebit': -500000.00,  # Negative EBIT
                'ebitda': -200000.00,  # Negative EBITDA
            }
        }
    }
