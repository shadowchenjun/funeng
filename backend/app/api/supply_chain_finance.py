"""
供应链金融API

所有数据来自数据库（见 app/models/supply_chain_finance.py），统计接口均由数据行实时汇总。
路由级登录校验在 main.py 中通过 ``dependencies=`` 统一挂载。
"""
import calendar
import uuid
from datetime import date, timedelta
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database import get_db
from app.models.supply_chain_finance import (
    FinancingOrder, Receivable, InsurancePolicy, CreditAssessment,
)
from app.models.user import User

router = APIRouter()

# ---------------------------------------------------------------------------
# 常量 / 业务规则
# ---------------------------------------------------------------------------

FINANCING_STATUSES = ["审核中", "已批准", "放款中", "已放款", "已结清", "已拒绝"]
FinancingStatus = Literal["审核中", "已批准", "放款中", "已放款", "已结清", "已拒绝"]
# 允许的状态流转（终态：已结清 / 已拒绝）
FINANCING_TRANSITIONS: dict[str, set[str]] = {
    "审核中": {"已批准", "已拒绝"},
    "已批准": {"放款中", "已拒绝"},
    "放款中": {"已放款"},
    "已放款": {"已结清"},
    "已结清": set(),
    "已拒绝": set(),
}
ACTIVE_FINANCING_STATUSES = {"审核中", "已批准", "放款中", "已放款"}
DISBURSED_STATUSES = {"放款中", "已放款", "已结清"}

RECEIVABLE_STATUSES = ["未到期", "即将到期", "已逾期", "已收回", "坏账"]
INSURANCE_TYPES = ["种植保险", "养殖保险", "价格保险", "气象指数保险", "质量保险"]
InsuranceType = Literal["种植保险", "养殖保险", "价格保险", "气象指数保险", "质量保险"]
# 各险种保费费率
INSURANCE_PREMIUM_RATES = {
    "种植保险": 0.035, "养殖保险": 0.055, "价格保险": 0.040,
    "气象指数保险": 0.045, "质量保险": 0.030,
}

# 融资定价：基准利率 + 期限加点 + 担保方式加点
BASE_RATE = 4.5
TERM_SPREAD = {30: 0.3, 60: 0.6, 90: 0.9, 120: 1.2, 180: 1.6}
COLLATERAL_SPREAD = {"订单质押": 0.5, "存货质押": 0.8, "应收账款质押": 0.4, "质押": 0.6, "抵押": 0.2, "信用": 1.8}
COLLATERAL_RISK = {"抵押": "低", "订单质押": "低", "应收账款质押": "低", "质押": "中", "存货质押": "中", "信用": "高"}

CREDIT_FACTOR_WEIGHTS = {"financial": 0.3, "operation": 0.25, "management": 0.25, "industry": 0.2}
CREDIT_FACTOR_LABELS = {"financial": "财务状况", "operation": "经营状况", "management": "管理水平", "industry": "行业前景"}

FINANCE_PRODUCTS = [
    {
        "id": "P001", "name": "订单贷", "type": "融资",
        "description": "基于采购订单的短期融资",
        "min_amount": 50000, "max_amount": 500000,
        "rate_range": "4.5%-8.5%", "term_range": "30-180天",
        "requirements": ["有效订单", "稳定经营", "良好信用"],
    },
    {
        "id": "P002", "name": "应收账款保理", "type": "融资",
        "description": "应收账款转让融资",
        "min_amount": 100000, "max_amount": 1000000,
        "rate_range": "5%-9%", "term_range": "30-90天",
        "requirements": ["真实贸易背景", "核心企业确认", "无争议账款"],
    },
    {
        "id": "P003", "name": "种植保险", "type": "保险",
        "description": "农作物种植风险保障",
        "coverage_range": "10万-200万", "premium_rate": "2%-6%",
        "coverage": ["自然灾害", "病虫害", "价格波动"],
        "requirements": ["合法种植", "符合技术规范"],
    },
    {
        "id": "P004", "name": "信用评估服务", "type": "服务",
        "description": "企业/农户信用评估",
        "price": 500, "turnaround": "3-5工作日",
        "deliverables": ["信用报告", "评分", "建议"],
        "requirements": ["完整资料", "配合调查"],
    },
]


# ---------------------------------------------------------------------------
# 请求模型
# ---------------------------------------------------------------------------

class FinancingOrderCreate(BaseModel):
    """订单融资申请"""
    amount: float = Field(..., gt=0, le=10_000_000, description="申请融资金额(元)")
    order_amount: Optional[float] = Field(None, gt=0, le=50_000_000, description="订单金额(元)，缺省等于融资金额")
    term: Literal[30, 60, 90, 120, 180] = Field(..., description="融资期限(天)")
    collateral: Literal["信用", "质押", "抵押", "订单质押", "存货质押", "应收账款质押"] = Field("信用", description="担保方式")
    product: str = Field("订单融资", min_length=1, max_length=100, description="订单标的")
    applicant: Optional[str] = Field(None, min_length=1, max_length=100, description="申请主体，缺省为当前用户")

    @model_validator(mode="after")
    def _check_amounts(self):
        if self.order_amount is not None and self.amount > self.order_amount:
            raise ValueError("融资金额不能超过订单金额")
        return self


class ReceivableTransfer(BaseModel):
    """应收账款转让（以应收账款质押申请融资）"""
    amount: Optional[float] = Field(None, gt=0, description="融资金额(元)，缺省为未回款金额的 80%")
    term: Literal[30, 60, 90, 120, 180] = Field(90, description="融资期限(天)")


class FinancingStatusUpdate(BaseModel):
    """融资订单状态变更"""
    status: FinancingStatus


class InsurancePolicyCreate(BaseModel):
    """农业保险投保"""
    type: InsuranceType = Field(..., description="险种")
    crop: str = Field(..., min_length=1, max_length=50, description="保险标的(作物/畜禽)")
    coverage: float = Field(..., gt=0, le=50_000_000, description="保额(元)")
    term_months: Literal[3, 6, 12] = Field(12, description="保险期限(月)")
    area: float = Field(0, ge=0, le=100_000, description="投保面积(亩)")
    start_date: Optional[date] = Field(None, description="起保日期，缺省为今天")
    holder: Optional[str] = Field(None, min_length=1, max_length=100, description="投保人，缺省为当前用户")


# ---------------------------------------------------------------------------
# 序列化 / 工具函数
# ---------------------------------------------------------------------------

def _fmt(d: Optional[date]) -> Optional[str]:
    return d.isoformat() if d else None


def _parse_code(code: str, prefix: str) -> Optional[int]:
    """把 'F0001' / '1' 形式的对外 ID 解析为整数主键，无法解析时返回 None"""
    raw = code[len(prefix):] if code.upper().startswith(prefix) else code
    return int(raw) if raw.isdigit() else None


def _pct(part: float, whole: float, digits: int = 1) -> float:
    return round(part / whole * 100, digits) if whole else 0.0


def _serialize_order(o: FinancingOrder) -> dict:
    return {
        "id": o.code,
        "order_no": o.order_no,
        "applicant": o.applicant,
        "product": o.product,
        "amount": o.amount,
        "financed_amount": o.financed_amount,
        "rate": o.rate,
        "term": o.term,
        "status": o.status,
        "apply_date": _fmt(o.apply_date),
        "expected_return": _fmt(o.expected_return),
        "collateral": o.collateral,
        "risk_level": o.risk_level,
    }


def _receivable_overdue_days(r: Receivable, today: date) -> int:
    if r.status in ("已逾期", "坏账"):
        return max(0, (today - r.due_date).days)
    return 0


def _serialize_receivable(r: Receivable, today: date) -> dict:
    return {
        "id": r.code,
        "invoice_no": r.invoice_no,
        "creditor": r.creditor,
        "debtor": r.debtor,
        "amount": r.amount,
        "paid_amount": r.paid_amount,
        "issue_date": _fmt(r.issue_date),
        "due_date": _fmt(r.due_date),
        "status": r.status,
        "overdue_days": _receivable_overdue_days(r, today),
        "risk_level": r.risk_level,
        "financing_order_id": f"{FinancingOrder.PREFIX}{r.financing_order_id:04d}" if r.financing_order_id else None,
    }


def _serialize_policy(p: InsurancePolicy) -> dict:
    return {
        "id": p.code,
        "policy_no": p.policy_no,
        "holder": p.holder,
        "type": p.type,
        "crop": p.crop,
        "area": p.area,
        "coverage": p.coverage,
        "premium": p.premium,
        "deductible": p.deductible,
        "start_date": _fmt(p.start_date),
        "end_date": _fmt(p.end_date),
        "status": p.status,
        "claims_count": p.claims_count,
        "claims_amount": p.claims_amount,
    }


def _serialize_assessment(c: CreditAssessment) -> dict:
    return {
        "id": c.code,
        "entity_name": c.entity_name,
        "entity_type": c.entity_type,
        "credit_score": c.credit_score,
        "level": c.level,
        "assessment_date": _fmt(c.assessment_date),
        "next_review": _fmt(c.next_review),
        "factors": {
            "financial": c.factor_financial,
            "operation": c.factor_operation,
            "management": c.factor_management,
            "industry": c.factor_industry,
        },
        "risk_indicators": {
            "overdue_count": c.overdue_count,
            "debt_ratio": c.debt_ratio,
            "cash_flow": c.cash_flow,
        },
    }


def _factor_detail(label: str, score: float) -> str:
    if score >= 85:
        return f"{label}优秀"
    if score >= 75:
        return f"{label}良好"
    if score >= 65:
        return f"{label}一般"
    return f"{label}较弱"


def _add_months(d: date, months: int) -> date:
    """日期加 months 个月，目标月天数不足时对齐到月末"""
    month_index = d.month - 1 + months
    year, month = d.year + month_index // 12, month_index % 12 + 1
    return date(year, month, min(d.day, calendar.monthrange(year, month)[1]))


def _temp_no() -> str:
    """插入时占位的唯一编号，flush 后替换为基于主键的正式编号"""
    return f"TMP{uuid.uuid4().hex[:16]}"


# ---------------------------------------------------------------------------
# 订单融资
# ---------------------------------------------------------------------------

@router.get("/financing/orders")
def get_financing_orders(db: Session = Depends(get_db)):
    """获取订单融资列表（按申请日期倒序）"""
    orders = (db.query(FinancingOrder)
              .order_by(FinancingOrder.apply_date.desc(), FinancingOrder.id.desc())
              .all())
    return [_serialize_order(o) for o in orders]


@router.get("/financing/stats")
def get_financing_stats(db: Session = Depends(get_db)):
    """
    获取融资统计数据（由融资订单实时汇总）

    - total_financed: 已放款（放款中/已放款/已结清）订单的融资金额合计
    - total_amount: 全部订单金额合计
    - active_orders: 在途订单数（审核中/已批准/放款中/已放款）
    - avg_rate: 全部订单平均利率
    - approval_rate: 已审结订单中获批比例(%)
    - overdue_rate: 已放款未结清订单中超过预计还款日的比例(%)
    """
    orders = db.query(FinancingOrder).all()
    today = date.today()
    decided = [o for o in orders if o.status != "审核中"]
    approved = [o for o in decided if o.status != "已拒绝"]
    outstanding = [o for o in orders if o.status == "已放款"]
    overdue = [o for o in outstanding if o.expected_return and o.expected_return < today]
    return {
        "total_financed": round(sum(o.financed_amount for o in orders if o.status in DISBURSED_STATUSES), 2),
        "active_orders": sum(1 for o in orders if o.status in ACTIVE_FINANCING_STATUSES),
        "total_amount": round(sum(o.amount for o in orders), 2),
        "avg_rate": round(sum(o.rate for o in orders) / len(orders), 2) if orders else 0.0,
        "approval_rate": _pct(len(approved), len(decided)),
        "overdue_rate": _pct(len(overdue), len(outstanding), 2),
        "by_status": {s: sum(1 for o in orders if o.status == s) for s in FINANCING_STATUSES},
    }


@router.post("/financing/orders", status_code=201)
def create_financing_order(
    payload: FinancingOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    申请订单融资。

    新订单状态为「审核中」；利率按「基准利率 + 期限加点 + 担保方式加点」定价，
    风险等级由担保方式决定。返回新建订单（与列表项结构一致）。
    """
    today = date.today()
    order = FinancingOrder(
        order_no=_temp_no(),
        applicant=payload.applicant or current_user.username,
        product=payload.product,
        amount=round(payload.order_amount or payload.amount, 2),
        financed_amount=round(payload.amount, 2),
        rate=round(BASE_RATE + TERM_SPREAD[payload.term] + COLLATERAL_SPREAD[payload.collateral], 2),
        term=payload.term,
        status="审核中",
        apply_date=today,
        expected_return=today + timedelta(days=payload.term),
        collateral=payload.collateral,
        risk_level=COLLATERAL_RISK[payload.collateral],
    )
    db.add(order)
    db.flush()
    order.order_no = f"ORD{today:%Y%m%d}{order.id:04d}"
    db.commit()
    db.refresh(order)
    return _serialize_order(order)


@router.patch("/financing/orders/{order_id}/status")
def update_financing_order_status(
    order_id: str,
    payload: FinancingStatusUpdate,
    db: Session = Depends(get_db),
):
    """
    更新融资订单状态。

    ``order_id`` 支持 ``F0001`` 或纯数字。状态只能按流转规则变更：
    审核中→已批准/已拒绝，已批准→放款中/已拒绝，放款中→已放款，已放款→已结清。
    非法流转返回 400，订单不存在返回 404。
    """
    pk = _parse_code(order_id, FinancingOrder.PREFIX)
    order = db.get(FinancingOrder, pk) if pk is not None else None
    if order is None:
        raise HTTPException(status_code=404, detail="融资订单不存在")
    if payload.status != order.status and payload.status not in FINANCING_TRANSITIONS[order.status]:
        raise HTTPException(status_code=400, detail=f"不允许从「{order.status}」变更为「{payload.status}」")
    order.status = payload.status
    db.commit()
    db.refresh(order)
    return _serialize_order(order)


# ---------------------------------------------------------------------------
# 应收账款
# ---------------------------------------------------------------------------

@router.get("/receivables")
def get_receivables(db: Session = Depends(get_db)):
    """获取应收账款列表（按到期日升序）"""
    today = date.today()
    rows = db.query(Receivable).order_by(Receivable.due_date.asc(), Receivable.id.asc()).all()
    return [_serialize_receivable(r, today) for r in rows]


# 可转让的应收账款状态，以及最高融资比例（占未回款金额）
TRANSFERABLE_RECEIVABLE_STATUSES = {"未到期", "即将到期"}
RECEIVABLE_MAX_FINANCING_RATIO = 0.9
RECEIVABLE_DEFAULT_FINANCING_RATIO = 0.8


@router.post("/receivables/{receivable_id}/transfer", status_code=201)
def transfer_receivable(
    receivable_id: str,
    payload: ReceivableTransfer,
    db: Session = Depends(get_db),
):
    """
    应收账款转让：以该笔应收账款质押，生成一笔「应收账款质押」融资订单（状态「审核中」）。

    仅「未到期 / 即将到期」且尚未转让的账款可转让；融资金额不超过未回款金额的 90%，
    缺省为 80%。账款不存在返回 404，不可转让或金额超限返回 400。返回新建的融资订单。
    """
    pk = _parse_code(receivable_id, Receivable.PREFIX)
    receivable = db.get(Receivable, pk) if pk is not None else None
    if receivable is None:
        raise HTTPException(status_code=404, detail="应收账款不存在")
    if receivable.financing_order_id is not None:
        raise HTTPException(status_code=400, detail="该应收账款已转让")
    if receivable.status not in TRANSFERABLE_RECEIVABLE_STATUSES:
        raise HTTPException(status_code=400, detail=f"「{receivable.status}」状态的应收账款不可转让")

    outstanding = round(receivable.amount - (receivable.paid_amount or 0), 2)
    max_amount = round(outstanding * RECEIVABLE_MAX_FINANCING_RATIO, 2)
    amount = round(payload.amount if payload.amount is not None else outstanding * RECEIVABLE_DEFAULT_FINANCING_RATIO, 2)
    if outstanding <= 0 or amount > max_amount:
        raise HTTPException(status_code=400, detail=f"融资金额不能超过未回款金额的 90%（最多 ¥{max_amount:,.2f}）")

    today = date.today()
    collateral = "应收账款质押"
    order = FinancingOrder(
        order_no=_temp_no(),
        applicant=receivable.creditor,
        product=f"应收账款 {receivable.invoice_no}",
        amount=outstanding,
        financed_amount=amount,
        rate=round(BASE_RATE + TERM_SPREAD[payload.term] + COLLATERAL_SPREAD[collateral], 2),
        term=payload.term,
        status="审核中",
        apply_date=today,
        expected_return=today + timedelta(days=payload.term),
        collateral=collateral,
        risk_level=receivable.risk_level or COLLATERAL_RISK[collateral],
    )
    db.add(order)
    db.flush()
    order.order_no = f"ORD{today:%Y%m%d}{order.id:04d}"
    receivable.financing_order_id = order.id
    db.commit()
    db.refresh(order)
    return _serialize_order(order)


@router.get("/receivables/stats")
def get_receivables_stats(db: Session = Depends(get_db)):
    """
    获取应收账款统计（由应收账款实时汇总）

    - collected: 已回款合计；outstanding: 未回款余额（金额 - 已回款）合计
    - overdue: 「已逾期」账款的未回款余额；collection_rate: 回款率(%)
    - avg_days: 平均账期(天)；by_status: 各状态账款金额合计
    """
    rows = db.query(Receivable).all()
    total = sum(r.amount for r in rows)
    collected = sum(r.paid_amount or 0 for r in rows)
    return {
        "total_amount": round(total, 2),
        "collected": round(collected, 2),
        "outstanding": round(total - collected, 2),
        "overdue": round(sum(r.amount - (r.paid_amount or 0) for r in rows if r.status == "已逾期"), 2),
        "collection_rate": _pct(collected, total),
        "avg_days": round(sum((r.due_date - r.issue_date).days for r in rows) / len(rows)) if rows else 0,
        "by_status": {s: round(sum(r.amount for r in rows if r.status == s), 2) for s in RECEIVABLE_STATUSES},
    }


# ---------------------------------------------------------------------------
# 农业保险
# ---------------------------------------------------------------------------

@router.get("/insurance")
def get_insurance(db: Session = Depends(get_db)):
    """获取农业保险列表（按起保日期倒序）"""
    rows = (db.query(InsurancePolicy)
            .order_by(InsurancePolicy.start_date.desc(), InsurancePolicy.id.desc())
            .all())
    return [_serialize_policy(p) for p in rows]


@router.get("/insurance/stats")
def get_insurance_stats(db: Session = Depends(get_db)):
    """
    获取农业保险统计（由保单实时汇总）

    - total_coverage / total_premium: 全部保单保额 / 保费合计
    - active_policies: 「生效中」保单数
    - claims_ratio: 赔付率 = 理赔金额 / 保费 (%)
    - by_type: 各险种保单数
    """
    rows = db.query(InsurancePolicy).all()
    total_premium = sum(p.premium for p in rows)
    claims_amount = sum(p.claims_amount or 0 for p in rows)
    return {
        "total_policies": len(rows),
        "active_policies": sum(1 for p in rows if p.status == "生效中"),
        "total_coverage": round(sum(p.coverage for p in rows), 2),
        "total_premium": round(total_premium, 2),
        "claims_count": sum(p.claims_count or 0 for p in rows),
        "claims_amount": round(claims_amount, 2),
        "claims_ratio": _pct(claims_amount, total_premium),
        "by_type": {t: sum(1 for p in rows if p.type == t) for t in INSURANCE_TYPES},
    }


@router.post("/insurance", status_code=201)
def create_insurance_policy(
    payload: InsurancePolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    购买农业保险。

    保费 = 保额 × 险种费率，免赔额为保额的 10%；起保日期晚于今天时状态为「待生效」，
    否则为「生效中」。返回新建保单（与列表项结构一致）。
    """
    start = payload.start_date or date.today()
    policy = InsurancePolicy(
        policy_no=_temp_no(),
        holder=payload.holder or current_user.username,
        type=payload.type,
        crop=payload.crop,
        area=payload.area,
        coverage=round(payload.coverage, 2),
        premium=round(payload.coverage * INSURANCE_PREMIUM_RATES[payload.type], 2),
        deductible=round(payload.coverage * 0.10, 2),
        start_date=start,
        end_date=_add_months(start, payload.term_months) - timedelta(days=1),
        status="待生效" if start > date.today() else "生效中",
        claims_count=0,
        claims_amount=0,
    )
    db.add(policy)
    db.flush()
    policy.policy_no = f"POL{start:%Y}{policy.id:06d}"
    db.commit()
    db.refresh(policy)
    return _serialize_policy(policy)


# ---------------------------------------------------------------------------
# 信用评估
# ---------------------------------------------------------------------------

@router.get("/credit/assessment")
def get_credit_assessments(db: Session = Depends(get_db)):
    """获取信用评估列表"""
    rows = db.query(CreditAssessment).order_by(CreditAssessment.id.asc()).all()
    return [_serialize_assessment(c) for c in rows]


@router.get("/credit/{entity_id}")
def get_credit_detail(entity_id: str, db: Session = Depends(get_db)):
    """获取信用详情（entity_id 支持 ``CR0001`` 或纯数字），不存在返回 404"""
    pk = _parse_code(entity_id, CreditAssessment.PREFIX)
    c = db.get(CreditAssessment, pk) if pk is not None else None
    if c is None:
        raise HTTPException(status_code=404, detail="信用评估主体不存在")
    scores = {
        "financial": c.factor_financial, "operation": c.factor_operation,
        "management": c.factor_management, "industry": c.factor_industry,
    }
    return {
        "entity_id": c.code,
        "entity_name": c.entity_name,
        "entity_type": c.entity_type,
        "credit_score": c.credit_score,
        "level": c.level,
        "assessment_date": _fmt(c.assessment_date),
        "valid_until": _fmt(c.next_review),
        "factors": {
            key: {
                "score": score,
                "weight": CREDIT_FACTOR_WEIGHTS[key],
                "detail": _factor_detail(CREDIT_FACTOR_LABELS[key], score),
            }
            for key, score in scores.items()
        },
        "history": c.history or [],
        "recommendations": c.recommendations or [],
    }


# ---------------------------------------------------------------------------
# 分析 / 产品
# ---------------------------------------------------------------------------

def _growth(dates: list[date], today: date, window: int = 90) -> float:
    """近 window 天数量相对前一个 window 天的增长率(%)"""
    recent = sum(1 for d in dates if today - timedelta(days=window) < d <= today)
    prev = sum(1 for d in dates if today - timedelta(days=2 * window) < d <= today - timedelta(days=window))
    return _pct(recent - prev, prev) if prev else (100.0 if recent else 0.0)


@router.get("/analytics")
def get_finance_analytics(db: Session = Depends(get_db)):
    """
    获取金融分析数据（由融资 / 应收 / 保险数据派生）

    - overview: 资产 = 在途融资余额 + 应收未收；负债 = 在途融资余额；roi = 在途融资加权利率
    - risk: 不良率 = (逾期 + 坏账)未收余额 / 应收总额；拨备覆盖率 = 已收保费 / 不良余额
    - growth: 近 90 天对比前 90 天的新增笔数增长率
    - portfolio: 融资 / 保险保额 / 应收 三类业务规模占比
    """
    today = date.today()
    orders = db.query(FinancingOrder).all()
    receivables = db.query(Receivable).all()
    policies = db.query(InsurancePolicy).all()

    live_orders = [o for o in orders if o.status in ("放款中", "已放款")]
    loan_balance = sum(o.financed_amount for o in live_orders)
    rec_outstanding = sum(r.amount - (r.paid_amount or 0) for r in receivables)
    rec_total = sum(r.amount for r in receivables)
    npl = sum(r.amount - (r.paid_amount or 0) for r in receivables if r.status in ("已逾期", "坏账"))
    premium = sum(p.premium for p in policies)
    high_risk = sum(1 for o in orders if o.risk_level == "高") + sum(1 for r in receivables if r.risk_level == "高")
    risk_items = len(orders) + len(receivables)
    risk_score = _pct(high_risk, risk_items)

    total_assets = loan_balance + rec_outstanding
    fin_scale = sum(o.financed_amount for o in orders)
    ins_scale = sum(p.coverage for p in policies)
    scale = fin_scale + ins_scale + rec_total

    return {
        "overview": {
            "total_assets": round(total_assets, 2),
            "total_liabilities": round(loan_balance, 2),
            "net_assets": round(total_assets - loan_balance, 2),
            "roi": round(sum(o.rate * o.financed_amount for o in live_orders) / loan_balance, 2) if loan_balance else 0.0,
        },
        "risk": {
            "overall_risk": "低" if risk_score < 15 else ("中低" if risk_score < 30 else ("中" if risk_score < 45 else "高")),
            "risk_score": risk_score,
            "npL_ratio": _pct(npl, rec_total, 2),
            "provision_coverage": _pct(premium, npl),
        },
        "growth": {
            "financing_growth": _growth([o.apply_date for o in orders], today),
            "insurance_growth": _growth([p.start_date for p in policies], today),
            "receivables_growth": _growth([r.issue_date for r in receivables], today),
        },
        "portfolio": {
            "financing": _pct(fin_scale, scale),
            "insurance": _pct(ins_scale, scale),
            "receivables": _pct(rec_total, scale),
        },
    }


@router.get("/products")
def get_finance_products():
    """获取金融产品列表（静态产品配置）"""
    return FINANCE_PRODUCTS
