"""
供应链金融相关数据模型

对外 ID 采用带前缀的字符串（如 F0001 / AR0001 / INS0001 / CR0001），
由整数主键派生，见各模型的 ``code`` 属性。
"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base


class FinancingOrder(Base):
    """订单融资模型"""
    __tablename__ = "scf_financing_orders"

    PREFIX = "F"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, nullable=False, comment="订单号")
    applicant = Column(String(100), nullable=False, comment="申请主体")
    product = Column(String(100), comment="订单标的")
    amount = Column(Float, nullable=False, comment="订单金额(元)")
    financed_amount = Column(Float, nullable=False, comment="融资金额(元)")
    rate = Column(Float, nullable=False, comment="年化利率(%)")
    term = Column(Integer, nullable=False, comment="期限(天)")
    status = Column(String(20), default="审核中", index=True,
                    comment="状态: 审核中/已批准/放款中/已放款/已结清/已拒绝")
    apply_date = Column(Date, nullable=False, comment="申请日期")
    expected_return = Column(Date, comment="预计还款日")
    collateral = Column(String(50), comment="担保方式")
    risk_level = Column(String(10), default="中", comment="风险等级: 低/中/高")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @property
    def code(self) -> str:
        return f"{self.PREFIX}{self.id:04d}"


class Receivable(Base):
    """应收账款模型"""
    __tablename__ = "scf_receivables"

    PREFIX = "AR"

    id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(String(50), unique=True, nullable=False, comment="发票号")
    creditor = Column(String(100), nullable=False, comment="债权人(卖方)")
    debtor = Column(String(100), nullable=False, comment="债务人(买方)")
    amount = Column(Float, nullable=False, comment="账款金额(元)")
    paid_amount = Column(Float, default=0, comment="已回款金额(元)")
    issue_date = Column(Date, nullable=False, comment="开票日期")
    due_date = Column(Date, nullable=False, comment="到期日期")
    status = Column(String(20), default="未到期", index=True,
                    comment="状态: 未到期/即将到期/已逾期/已收回/坏账")
    risk_level = Column(String(10), default="低", comment="风险等级: 低/中/高")
    financing_order_id = Column(Integer, ForeignKey("scf_financing_orders.id"), nullable=True,
                                comment="转让(质押融资)生成的融资订单")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @property
    def code(self) -> str:
        return f"{self.PREFIX}{self.id:04d}"


class InsurancePolicy(Base):
    """农业保险保单模型"""
    __tablename__ = "scf_insurance_policies"

    PREFIX = "INS"

    id = Column(Integer, primary_key=True, index=True)
    policy_no = Column(String(50), unique=True, nullable=False, comment="保单号")
    holder = Column(String(100), nullable=False, comment="投保人")
    type = Column(String(50), nullable=False, comment="险种")
    crop = Column(String(50), comment="保险标的(作物/畜禽)")
    area = Column(Float, default=0, comment="投保面积(亩)")
    coverage = Column(Float, nullable=False, comment="保额(元)")
    premium = Column(Float, nullable=False, comment="保费(元)")
    deductible = Column(Float, default=0, comment="免赔额(元)")
    start_date = Column(Date, nullable=False, comment="起保日期")
    end_date = Column(Date, nullable=False, comment="终保日期")
    status = Column(String(20), default="生效中", index=True,
                    comment="状态: 生效中/待生效/已到期/已理赔/已退保")
    claims_count = Column(Integer, default=0, comment="理赔次数")
    claims_amount = Column(Float, default=0, comment="理赔金额(元)")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @property
    def code(self) -> str:
        return f"{self.PREFIX}{self.id:04d}"


class CreditAssessment(Base):
    """信用评估模型"""
    __tablename__ = "scf_credit_assessments"

    PREFIX = "CR"

    id = Column(Integer, primary_key=True, index=True)
    entity_name = Column(String(100), nullable=False, comment="评估主体")
    entity_type = Column(String(20), comment="主体类型: 企业/合作社/农户")
    credit_score = Column(Integer, nullable=False, comment="信用分(300-850)")
    level = Column(String(10), nullable=False, comment="信用等级: AAA/AA/A/BBB/BB/B/CCC")
    assessment_date = Column(Date, nullable=False, comment="评估日期")
    next_review = Column(Date, comment="下次复评日期")
    factor_financial = Column(Float, default=0, comment="财务得分")
    factor_operation = Column(Float, default=0, comment="经营得分")
    factor_management = Column(Float, default=0, comment="管理得分")
    factor_industry = Column(Float, default=0, comment="行业得分")
    overdue_count = Column(Integer, default=0, comment="逾期次数")
    debt_ratio = Column(Float, default=0, comment="资产负债率(%)")
    cash_flow = Column(String(10), default="一般", comment="现金流: 良好/一般/紧张")
    history = Column(JSON, default=list, comment="历史评估 [{date, score, level, event}]")
    recommendations = Column(JSON, default=list, comment="改进建议 [str]")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @property
    def code(self) -> str:
        return f"{self.PREFIX}{self.id:04d}"


# 信用分 → 等级 映射（分数下限, 等级），按分数从高到低
CREDIT_LEVEL_THRESHOLDS = [
    (750, "AAA"), (700, "AA"), (650, "A"), (600, "BBB"), (550, "BB"), (500, "B"),
]


def credit_level(score: int) -> str:
    """根据信用分(300-850)返回信用等级"""
    for threshold, level in CREDIT_LEVEL_THRESHOLDS:
        if score >= threshold:
            return level
    return "CCC"
