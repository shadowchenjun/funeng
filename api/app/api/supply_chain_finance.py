"""
供应链金融API
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import random

router = APIRouter()

# 订单融资模型
class OrderFinancing(BaseModel):
    id: str
    order_no: str
    applicant: str
    amount: float
    rate: float
    term: int
    status: str
    apply_date: str

# 应收账款模型
class AccountReceivable(BaseModel):
    id: str
    invoice_no: str
    creditor: str
    debtor: str
    amount: float
    due_date: str
    status: str

# 农业保险模型
class AgriculturalInsurance(BaseModel):
    id: str
    policy_no: str
    holder: str
    type: str
    coverage: float
    premium: float
    status: str

# 信用评估模型
class CreditAssessment(BaseModel):
    id: str
    entity_name: str
    credit_score: int
    level: str
    factors: list

@router.get("/financing/orders")
def get_financing_orders():
    """获取订单融资列表"""
    statuses = ["审核中", "已批准", "放款中", "已放款", "已结清", "已拒绝"]
    products = ["有机大米订单", "蔬菜批发订单", "水果出口订单", "畜牧产品订单"]
    
    orders = []
    for i in range(15):
        apply_date = datetime.now() - timedelta(days=random.randint(1, 60))
        amount = random.randint(50000, 500000)
        
        orders.append({
            "id": f"F{i+1:04d}",
            "order_no": f"ORD{datetime.now().strftime('%Y%m')}{i+1:04d}",
            "applicant": f"企业{random.randint(1, 50)}",
            "product": random.choice(products),
            "amount": amount,
            "financed_amount": round(amount * random.uniform(0.5, 0.9), 2),
            "rate": round(random.uniform(3.5, 8.5), 2),
            "term": random.choice([30, 60, 90, 120, 180]),
            "status": random.choice(statuses),
            "apply_date": apply_date.strftime("%Y-%m-%d"),
            "expected_return": (apply_date + timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%d"),
            "collateral": random.choice(["订单质押", "存货质押", "应收账款质押"]),
            "risk_level": random.choice(["低", "中", "高"])
        })
    return orders

@router.get("/financing/stats")
def get_financing_stats():
    """获取融资统计数据"""
    return {
        "total_financed": round(random.uniform(10000000, 50000000), 2),
        "active_orders": random.randint(50, 200),
        "total_amount": round(random.uniform(5000000, 20000000), 2),
        "avg_rate": round(random.uniform(4.5, 7.5), 2),
        "approval_rate": round(random.uniform(75, 95), 1),
        "overdue_rate": round(random.uniform(0.5, 3), 2),
        "by_status": {
            "审核中": random.randint(10, 30),
            "已批准": random.randint(20, 50),
            "放款中": random.randint(5, 15),
            "已放款": random.randint(30, 100),
            "已结清": random.randint(100, 500)
        }
    }

@router.get("/receivables")
def get_receivables():
    """获取应收账款列表"""
    statuses = ["未到期", "即将到期", "已逾期", "已收回", "坏账"]
    companies = [f"公司{i}" for i in range(1, 30)]
    
    receivables = []
    for i in range(20):
        issue_date = datetime.now() - timedelta(days=random.randint(30, 180))
        due_date = issue_date + timedelta(days=random.randint(30, 90))
        amount = random.randint(10000, 500000)
        
        if due_date < datetime.now():
            status = random.choice(["已逾期", "已收回", "坏账"])
        else:
            days_to_due = (due_date - datetime.now()).days
            if days_to_due <= 7:
                status = "即将到期"
            else:
                status = "未到期"
        
        receivables.append({
            "id": f"AR{i+1:04d}",
            "invoice_no": f"INV{datetime.now().strftime('%Y%m')}{i+1:04d}",
            "creditor": random.choice(companies),
            "debtor": random.choice(companies),
            "amount": amount,
            "paid_amount": amount if status == "已收回" else random.randint(0, int(amount * 0.5)),
            "issue_date": issue_date.strftime("%Y-%m-%d"),
            "due_date": due_date.strftime("%Y-%m-%d"),
            "status": status,
            "overdue_days": max(0, (datetime.now() - due_date).days),
            "risk_level": "高" if status == "已逾期" else ("中" if status == "即将到期" else "低")
        })
    return receivables

@router.get("/receivables/stats")
def get_receivables_stats():
    """获取应收账款统计"""
    return {
        "total_amount": round(random.uniform(5000000, 20000000), 2),
        "collected": round(random.uniform(3000000, 15000000), 2),
        "outstanding": round(random.uniform(2000000, 8000000), 2),
        "overdue": round(random.uniform(100000, 1000000), 2),
        "collection_rate": round(random.uniform(70, 95), 1),
        "avg_days": random.randint(30, 60),
        "by_status": {
            "未到期": round(random.uniform(2000000, 8000000), 2),
            "即将到期": round(random.uniform(500000, 2000000), 2),
            "已逾期": round(random.uniform(100000, 1000000), 2),
            "已收回": round(random.uniform(3000000, 15000000), 2)
        }
    }

@router.get("/insurance")
def get_insurance():
    """获取农业保险列表"""
    types = ["种植保险", "养殖保险", "价格保险", "气象指数保险", "质量保险"]
    statuses = ["生效中", "待生效", "已到期", "已理赔", "已退保"]
    crops = ["水稻", "小麦", "玉米", "蔬菜", "水果", "生猪", "奶牛"]
    
    insurance_list = []
    for i in range(15):
        start_date = datetime.now() - timedelta(days=random.randint(30, 365))
        end_date = start_date + timedelta(days=random.randint(180, 365))
        coverage = random.randint(100000, 2000000)
        
        insurance_list.append({
            "id": f"INS{i+1:04d}",
            "policy_no": f"POL{datetime.now().strftime('%Y')}{i+1:06d}",
            "holder": f"农户/企业{random.randint(1, 100)}",
            "type": random.choice(types),
            "crop": random.choice(crops),
            "area": round(random.uniform(10, 500), 1),
            "coverage": coverage,
            "premium": round(coverage * random.uniform(0.02, 0.08), 2),
            "deductible": round(coverage * random.uniform(0.05, 0.15), 2),
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "status": random.choice(statuses),
            "claims_count": random.randint(0, 5),
            "claims_amount": round(random.uniform(0, 500000), 2)
        })
    return insurance_list

@router.get("/insurance/stats")
def get_insurance_stats():
    """获取农业保险统计"""
    return {
        "total_policies": random.randint(500, 2000),
        "active_policies": random.randint(300, 1500),
        "total_coverage": round(random.uniform(100000000, 500000000), 2),
        "total_premium": round(random.uniform(2000000, 10000000), 2),
        "claims_count": random.randint(50, 300),
        "claims_amount": round(random.uniform(500000, 5000000), 2),
        "claims_ratio": round(random.uniform(10, 40), 1),
        "by_type": {
            "种植保险": random.randint(200, 800),
            "养殖保险": random.randint(100, 400),
            "价格保险": random.randint(50, 200),
            "气象指数保险": random.randint(30, 150),
            "质量保险": random.randint(20, 100)
        }
    }

@router.get("/credit/assessment")
def get_credit_assessments():
    """获取信用评估列表"""
    levels = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]
    entities = [f"企业/农户{i}" for i in range(1, 30)]
    
    assessments = []
    for i in range(20):
        score = random.randint(300, 850)
        if score >= 750:
            level = "AAA"
        elif score >= 700:
            level = "AA"
        elif score >= 650:
            level = "A"
        elif score >= 600:
            level = "BBB"
        elif score >= 550:
            level = "BB"
        elif score >= 500:
            level = "B"
        else:
            level = "CCC"
        
        assessments.append({
            "id": f"CR{i+1:04d}",
            "entity_name": random.choice(entities),
            "entity_type": random.choice(["企业", "合作社", "农户"]),
            "credit_score": score,
            "level": level,
            "assessment_date": (datetime.now() - timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d"),
            "next_review": (datetime.now() + timedelta(days=random.randint(90, 365))).strftime("%Y-%m-%d"),
            "factors": {
                "financial": round(random.uniform(60, 95), 1),
                "operation": round(random.uniform(60, 95), 1),
                "management": round(random.uniform(60, 95), 1),
                "industry": round(random.uniform(60, 95), 1)
            },
            "risk_indicators": {
                "overdue_count": random.randint(0, 5),
                "debt_ratio": round(random.uniform(20, 80), 1),
                "cash_flow": random.choice(["良好", "一般", "紧张"])
            }
        })
    return assessments

@router.get("/credit/{entity_id}")
def get_credit_detail(entity_id: str):
    """获取信用详情"""
    return {
        "entity_id": entity_id,
        "entity_name": "企业示例",
        "entity_type": "农业企业",
        "credit_score": 720,
        "level": "AA",
        "assessment_date": "2026-01-15",
        "valid_until": "2027-01-15",
        "factors": {
            "financial": {"score": 75, "weight": 0.3, "detail": "财务状况良好"},
            "operation": {"score": 80, "weight": 0.25, "detail": "经营稳定"},
            "management": {"score": 70, "weight": 0.25, "detail": "管理规范"},
            "industry": {"score": 65, "weight": 0.2, "detail": "行业前景一般"}
        },
        "history": [
            {"date": "2026-01-15", "score": 720, "level": "AA", "event": "年度评估"},
            {"date": "2025-07-15", "score": 710, "level": "AA", "event": "半年度评估"},
            {"date": "2025-01-15", "score": 695, "level": "A", "event": "年度评估"}
        ],
        "recommendations": [
            "建议降低负债率至50%以下",
            "加强现金流管理",
            "扩大经营规模提升抗风险能力"
        ]
    }

@router.get("/analytics")
def get_finance_analytics():
    """获取金融分析数据"""
    return {
        "overview": {
            "total_assets": round(random.uniform(50000000, 200000000), 2),
            "total_liabilities": round(random.uniform(20000000, 80000000), 2),
            "net_assets": round(random.uniform(30000000, 120000000), 2),
            "roi": round(random.uniform(5, 15), 2)
        },
        "risk": {
            "overall_risk": "中低",
            "risk_score": round(random.uniform(20, 50), 1),
            "npL_ratio": round(random.uniform(1, 5), 2),
            "provision_coverage": round(random.uniform(100, 200), 1)
        },
        "growth": {
            "financing_growth": round(random.uniform(10, 40), 1),
            "insurance_growth": round(random.uniform(15, 50), 1),
            "receivables_growth": round(random.uniform(-5, 20), 1)
        },
        "portfolio": {
            "financing": round(random.uniform(40, 60), 1),
            "insurance": round(random.uniform(20, 35), 1),
            "receivables": round(random.uniform(15, 30), 1)
        }
    }

@router.get("/products")
def get_finance_products():
    """获取金融产品列表"""
    products = [
        {
            "id": "P001",
            "name": "订单贷",
            "type": "融资",
            "description": "基于采购订单的短期融资",
            "min_amount": 50000,
            "max_amount": 500000,
            "rate_range": "4.5%-8.5%",
            "term_range": "30-180天",
            "requirements": ["有效订单", "稳定经营", "良好信用"]
        },
        {
            "id": "P002",
            "name": "应收账款保理",
            "type": "融资",
            "description": "应收账款转让融资",
            "min_amount": 100000,
            "max_amount": 1000000,
            "rate_range": "5%-9%",
            "term_range": "30-90天",
            "requirements": ["真实贸易背景", "核心企业确认", "无争议账款"]
        },
        {
            "id": "P003",
            "name": "种植保险",
            "type": "保险",
            "description": "农作物种植风险保障",
            "coverage_range": "10万-200万",
            "premium_rate": "2%-6%",
            "coverage": ["自然灾害", "病虫害", "价格波动"],
            "requirements": ["合法种植", "符合技术规范"]
        },
        {
            "id": "P004",
            "name": "信用评估服务",
            "type": "服务",
            "description": "企业/农户信用评估",
            "price": 500,
            "turnaround": "3-5工作日",
            "deliverables": ["信用报告", "评分", "建议"],
            "requirements": ["完整资料", "配合调查"]
        }
    ]
    return products
