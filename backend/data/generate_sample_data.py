"""
Generate sample P&L data for testing
"""

import pandas as pd
import random
from datetime import datetime, timedelta

# Business groups และ services
business_services = {
    "1 Hard Infrastructure": [
        "1.1 กลุ่มบริการท่อร้อยสาย",
        "1.2 กลุ่มบริการ Dark Fiber",
        "1.3 กลุ่มบริการเสาโทรคมนาคม (Tower)",
        "1.4 กลุ่มบริการพัฒนาสินทรัพย์"
    ],
    "2 International": [
        "2.1 กลุ่มบริการ IIG",
        "2.3 กลุ่มบริการ Connectivity",
        "2.4 กลุ่มบริการเคเบิลใต้น้ำ",
        "2.5 กลุ่มบริการ IDD"
    ],
    "3 Mobile": [
        "3.1 บริการโทรคมนาคมสื่อสารไร้สาย - Wholesale",
        "3.2 บริการโทรคมนาคมสื่อสารไร้สาย - Retail",
        "3.5 บริการ IoT Connectivity",
        "3.6 บริการ 5G Solutions"
    ],
    "4 Fixed Line & Broadband": [
        "4.2 กลุ่มบริการ Internet Retail",
        "4.3 กลุ่มบริการวงจรเช่า",
        "4.4 บริการโทรศัพท์ประจำที่",
        "4.5 กลุ่มบริการ Satellite NT"
    ],
    "5 Digital": [
        "5.1 กลุ่มบริการ Cloud & BigData",
        "5.2 กลุ่มบริการ Data Center & IX",
        "5.3 กลุ่มบริการ Cybersecurity",
        "5.4 กลุ่มบริการ Application"
    ],
    "6 ICT Solution": [
        "6.1 กลุ่มบริการ Solution",
        "6.2 กลุ่มบริการ Contact Center",
        "6.3 กลุ่มบริการ ICT Solution"
    ]
}

# หมวดบัญชี
account_categories = [
    ("C01", "ค่าใช้จ่ายตอบแทนแรงงาน"),
    ("C02", "ค่าสวัสดิการ"),
    ("C03", "ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร"),
    ("C04", "ค่าซ่อมแซมและบำรุงรักษาและวัสดุใช้ไป"),
    ("C05", "ค่าสาธารณูปโภค"),
    ("C06", "ค่าใช้จ่ายการตลาดและส่งเสริมการขาย"),
    ("C07", "ค่าใช้จ่ายเผยแพร่ประชาสัมพันธ์"),
    ("C08", "ค่าใช้จ่ายเกี่ยวกับการกำกับดูแลของ กสทช."),
    ("C09", "ค่าส่วนแบ่งบริการโทรคมนาคม"),
    ("C10", "ค่าใช้จ่ายบริการโทรคมนาคม"),
    ("C11", "ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์"),
    ("C12", "ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า"),
    ("C13", "ค่าเช่าและค่าใช้สินทรัพย์"),
    ("C14", "ต้นทุนขาย"),
    ("C15", "ค่าใช้จ่ายบริการอื่น"),
    ("C16", "ค่าใช้จ่ายดำเนินงานอื่น"),
]

# Types
types = [
    "02 ต้นทุนบริการ",
    "03 ค่าใช้จ่ายขายและการตลาด",
    "04 ค่าใช้จ่ายสนับสนุน"
]

def generate_profit_loss_data():
    """Generate sample P&L data"""
    data = []

    # สร้างข้อมูล 3 เดือน (Jan, Feb, Mar 2025)
    for month in range(1, 4):
        date = f"2025-{month:02d}-01"

        # สำหรับแต่ละ business group
        for business, services in business_services.items():
            # สำหรับแต่ละ service
            for service in services[:2]:  # เอาแค่ 2 services แรกเพื่อไม่ให้ข้อมูลเยอะเกินไป

                # สร้างรายได้
                product_key = f"{random.randint(100000000, 199999999)}"
                revenue_amount = random.uniform(50000, 500000) * (1 + month * 0.05)

                data.append({
                    'YEAR': 2025,
                    'MONTH': month,
                    'DATE': date,
                    'PRODUCT_KEY': product_key,
                    'หมวดบัญชี': f"R0{list(business_services.keys()).index(business) + 1} รายได้{business}",
                    'TYPE': "01 รายได้",
                    'NT': 'NT',
                    'PRODUCT_NAME': service,
                    'ITEM': business.split()[0],
                    'BUSINESS_GROUP': business,
                    'SUB_ITEM': service.split()[0],
                    'SERVICE_GROUP': service,
                    'BUSINESS': business,
                    'SERVICE': service,
                    'PRODUCT': f"{product_key} {service}",
                    'REPORT_CODE': f"R0{list(business_services.keys()).index(business) + 1}",
                    'GL_GROUP': f"รายได้{business}",
                    'CUSTOMER_GROUP_KEY': '',
                    'EXPENSE_VALUE': 0,
                    'AMOUNT': 0,
                    'REVENUE_VALUE': revenue_amount
                })

                # สร้างค่าใช้จ่าย
                for type_name in types:
                    # สุ่ม 3-5 หมวดบัญชี
                    selected_accounts = random.sample(account_categories, random.randint(3, 5))

                    for code, name in selected_accounts:
                        expense_amount = random.uniform(5000, 50000) * (1 + month * 0.03)

                        # บางรายการอาจเป็นลบ (refund)
                        if random.random() < 0.05:
                            expense_amount = -expense_amount

                        data.append({
                            'YEAR': 2025,
                            'MONTH': month,
                            'DATE': date,
                            'PRODUCT_KEY': product_key,
                            'หมวดบัญชี': f"{code} {name}",
                            'TYPE': type_name,
                            'NT': 'NT',
                            'PRODUCT_NAME': service,
                            'ITEM': business.split()[0],
                            'BUSINESS_GROUP': business,
                            'SUB_ITEM': service.split()[0],
                            'SERVICE_GROUP': service,
                            'BUSINESS': business,
                            'SERVICE': service,
                            'PRODUCT': f"{product_key} {service}",
                            'REPORT_CODE': code,
                            'GL_GROUP': name,
                            'CUSTOMER_GROUP_KEY': '',
                            'EXPENSE_VALUE': expense_amount,
                            'AMOUNT': expense_amount,
                            'REVENUE_VALUE': 0
                        })

    df = pd.DataFrame(data)
    return df

def generate_other_income_expense():
    """Generate other income/expense data"""
    data = []

    # สร้างข้อมูล 3 เดือน
    for month in range(1, 4):
        # Other income
        other_income_month = random.uniform(80000, 120000)
        other_income_ytd = sum([random.uniform(80000, 120000) for m in range(1, month + 1)])

        # Other expense
        other_expense_month = random.uniform(20000, 40000)
        other_expense_ytd = sum([random.uniform(20000, 40000) for m in range(1, month + 1)])

        # Financial income
        financial_income_month = random.uniform(40000, 60000)
        financial_income_ytd = sum([random.uniform(40000, 60000) for m in range(1, month + 1)])

        # Financial cost
        financial_cost_month = random.uniform(15000, 25000)
        financial_cost_ytd = sum([random.uniform(15000, 25000) for m in range(1, month + 1)])

        # Corporate tax
        corporate_tax_month = random.uniform(100000, 200000)
        corporate_tax_ytd = sum([random.uniform(100000, 200000) for m in range(1, month + 1)])

        data.append({
            'YEAR': 2025,
            'MONTH': month,
            'financial_income_month': financial_income_month,
            'financial_income_ytd': financial_income_ytd,
            'other_income_month': other_income_month,
            'other_income_ytd': other_income_ytd,
            'other_expense_month': other_expense_month,
            'other_expense_ytd': other_expense_ytd,
            'financial_cost_month': financial_cost_month,
            'financial_cost_ytd': financial_cost_ytd,
            'corporate_tax_month': corporate_tax_month,
            'corporate_tax_ytd': corporate_tax_ytd
        })

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    print("Generating sample P&L data...")

    # Generate profit & loss data
    df_pl = generate_profit_loss_data()
    df_pl.to_csv('profit_loss.csv', index=False, encoding='utf-8-sig')
    print(f"✓ Created profit_loss.csv ({len(df_pl)} rows)")

    # Generate other income/expense data
    df_other = generate_other_income_expense()
    df_other.to_csv('other_income_expense.csv', index=False, encoding='utf-8-sig')
    print(f"✓ Created other_income_expense.csv ({len(df_other)} rows)")

    print("\nSample data summary:")
    print(f"- Total revenue: {df_pl[df_pl['REVENUE_VALUE'] > 0]['REVENUE_VALUE'].sum():,.2f}")
    print(f"- Total expense: {df_pl[df_pl['EXPENSE_VALUE'] > 0]['EXPENSE_VALUE'].sum():,.2f}")
    print(f"- Business groups: {df_pl['BUSINESS_GROUP'].nunique()}")
    print(f"- Months: {df_pl['MONTH'].nunique()}")
    print("\nDone!")
