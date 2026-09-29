"""
管理后台（/api/admin/*）写接口的请求体 Schema

约定：
- 所有写接口字段通过 JSON body 传递（不再使用 query 参数，避免密码/描述/配置出现在 URL 与日志中）。
- Create 模型：必填字段 + 合理的默认值与校验。
- Update 模型：全部字段可省略，端点使用 ``model_dump(exclude_unset=True)`` 只更新传入的字段。
  对数据库非空列，Update 模型的字段类型写成非 Optional（默认值 None 不参与校验），
  因此“省略”合法，但显式传 null 会返回 422。
- 空字符串统一视为 null（管理后台表单未填写的输入框会提交 ""）；
  若字段有非空默认值（如 group="general"），空字符串视为未填写并使用默认值。
- 未声明的字段一律拒绝（extra="forbid"），防止前端字段名拼错被静默忽略。
- 以 JSON 字符串入库的字段（benefits / images / rules / config ...）既可传字符串，
  也可直接传数组/对象，统一序列化为 JSON 字符串。
"""
import json
from datetime import datetime
from typing import Annotated, Any, ClassVar, FrozenSet, List, Literal, Optional, Union

from pydantic import (
    BaseModel, BeforeValidator, ConfigDict, EmailStr, Field, model_validator,
)


# ============ 通用类型 ============

def _to_json_text(value: Any) -> Any:
    """数组/对象 -> JSON 字符串；字符串必须是合法 JSON（读取端会 json.loads）"""
    if value is None:
        return None
    if isinstance(value, str):
        try:
            json.loads(value)
        except ValueError:
            raise ValueError("必须是合法的 JSON 字符串")
        return value
    return json.dumps(value, ensure_ascii=False)


def _to_text_or_json(value: Any) -> Any:
    """字符串原样保留；数组/对象序列化为 JSON 字符串（不强制 JSON 格式）"""
    if value is None or isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


JsonText = Annotated[Optional[str], BeforeValidator(_to_json_text)]
LooseText = Annotated[Optional[str], BeforeValidator(_to_text_or_json)]

Code = Annotated[str, Field(min_length=1, max_length=50)]
Name100 = Annotated[str, Field(min_length=1, max_length=100)]
Name50 = Annotated[str, Field(min_length=1, max_length=50)]
Url = Annotated[str, Field(max_length=500)]
Icon = Annotated[str, Field(max_length=50)]
Password = Annotated[str, Field(min_length=6, max_length=128)]

OrderStatus = Literal["pending", "paid", "active", "completed", "cancelled", "refunded"]
LandType = Literal["farm", "orchard", "greenhouse"]
LandStatus = Literal["available", "rented", "reserved"]
AdoptionUnit = Literal["year", "month", "season"]
DeviceStatus = Literal["online", "offline", "error", "maintenance"]
NodeType = Literal["planting", "growing", "harvesting", "processing", "packaging", "transport"]
CouponType = Literal["discount", "cash"]
ActivityStatus = Literal["pending", "active", "ended", "cancelled"]
ConfigType = Literal["string", "number", "boolean", "json"]


class AdminBody(BaseModel):
    """管理后台请求体基类"""
    model_config = ConfigDict(extra="forbid")

    # 这些字段的空字符串是合法值，不转换为 None
    keep_blank_fields: ClassVar[FrozenSet[str]] = frozenset()

    @model_validator(mode="before")
    @classmethod
    def _blank_to_none(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        out = {}
        for k, v in data.items():
            if isinstance(v, str) and v.strip() == "" and k not in cls.keep_blank_fields:
                field = cls.model_fields.get(k)
                if field is not None and not field.is_required() and field.default is not None:
                    continue  # 有非空默认值的字段（如 group="general"）：空串视为未填写，使用默认值
                v = None
            out[k] = v
        return out


class StatusUpdate(AdminBody):
    """订单状态变更（认养订单 / 租地订单）"""
    status: OrderStatus
    remark: Optional[str] = Field(None, max_length=1000)


# ============ 认证 / 个人信息 ============

class ProfileUpdate(AdminBody):
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    avatar: Optional[Url] = None


class PasswordChange(AdminBody):
    keep_blank_fields = frozenset({"old_password", "new_password"})
    old_password: str = Field(min_length=1, max_length=128)
    new_password: Password


# ============ 管理员 / 角色 ============

class AdminCreate(AdminBody):
    username: Annotated[str, Field(min_length=3, max_length=50)]
    password: Password
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role_id: Optional[int] = Field(None, gt=0)


class AdminUpdate(AdminBody):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    avatar: Optional[Url] = None
    role_id: Optional[int] = Field(None, gt=0)
    is_active: bool = None  # type: ignore[assignment]


class PasswordReset(AdminBody):
    keep_blank_fields = frozenset({"password"})
    password: Password


class RoleCreate(AdminBody):
    name: Name50
    code: Code
    description: Optional[str] = Field(None, max_length=1000)
    permissions: LooseText = None


class RoleUpdate(AdminBody):
    name: Name50 = None  # type: ignore[assignment]
    description: Optional[str] = Field(None, max_length=1000)
    permissions: LooseText = None
    is_active: bool = None  # type: ignore[assignment]


# ============ 认养 ============

class AdoptionCategoryCreate(AdminBody):
    name: Name100
    code: Code
    icon: Optional[Icon] = None
    description: Optional[str] = Field(None, max_length=2000)
    sort_order: int = Field(0, ge=0)


class AdoptionCategoryUpdate(AdminBody):
    name: Name100 = None  # type: ignore[assignment]
    icon: Optional[Icon] = None
    description: Optional[str] = Field(None, max_length=2000)
    sort_order: int = Field(None, ge=0)  # type: ignore[assignment]
    is_active: bool = None  # type: ignore[assignment]


class AdoptionConfigCreate(AdminBody):
    category_id: int = Field(gt=0)
    name: Name100
    price: float = Field(gt=0)
    duration_days: int = Field(gt=0)
    description: Optional[str] = Field(None, max_length=5000)
    unit: AdoptionUnit = "year"
    benefits: JsonText = None
    images: JsonText = None
    stock: int = Field(0, ge=0)


class AdoptionConfigUpdate(AdminBody):
    name: Name100 = None  # type: ignore[assignment]
    price: float = Field(None, gt=0)  # type: ignore[assignment]
    duration_days: int = Field(None, gt=0)  # type: ignore[assignment]
    description: Optional[str] = Field(None, max_length=5000)
    unit: AdoptionUnit = None  # type: ignore[assignment]
    benefits: JsonText = None
    images: JsonText = None
    stock: int = Field(None, ge=0)  # type: ignore[assignment]
    is_active: bool = None  # type: ignore[assignment]


class LandAllocate(AdminBody):
    land_parcel_id: int = Field(gt=0)


# ============ 土地 ============

class LandParcelCreate(AdminBody):
    name: Name100
    code: Code
    area: float = Field(gt=0)
    location: Optional[str] = Field(None, max_length=200)
    type: LandType = "farm"
    description: Optional[str] = Field(None, max_length=5000)
    image_url: Optional[Url] = None


class LandParcelUpdate(AdminBody):
    name: Name100 = None  # type: ignore[assignment]
    area: float = Field(None, gt=0)  # type: ignore[assignment]
    location: Optional[str] = Field(None, max_length=200)
    type: LandType = None  # type: ignore[assignment]
    description: Optional[str] = Field(None, max_length=5000)
    image_url: Optional[Url] = None
    status: LandStatus = None  # type: ignore[assignment]


# ============ 设备 ============

class DeviceTypeCreate(AdminBody):
    name: Name100
    code: Code
    icon: Optional[Icon] = None
    description: Optional[str] = Field(None, max_length=2000)
    specifications: JsonText = None


class DeviceTypeUpdate(AdminBody):
    name: Name100 = None  # type: ignore[assignment]
    icon: Optional[Icon] = None
    description: Optional[str] = Field(None, max_length=2000)
    specifications: JsonText = None
    is_active: bool = None  # type: ignore[assignment]


class DeviceCreate(AdminBody):
    name: Name100
    code: Code
    device_type_id: int = Field(gt=0)
    location: Optional[str] = Field(None, max_length=200)
    land_parcel_id: Optional[int] = Field(None, gt=0)
    config: JsonText = None
    firmware_version: Optional[str] = Field(None, max_length=50)


class DeviceUpdate(AdminBody):
    name: Name100 = None  # type: ignore[assignment]
    location: Optional[str] = Field(None, max_length=200)
    land_parcel_id: Optional[int] = Field(None, gt=0)
    config: JsonText = None
    firmware_version: Optional[str] = Field(None, max_length=50)
    status: DeviceStatus = None  # type: ignore[assignment]


def _check_thresholds(lo: Optional[float], hi: Optional[float]) -> None:
    if lo is not None and hi is not None and lo > hi:
        raise ValueError("threshold_min 不能大于 threshold_max")


class MonitoringPointCreate(AdminBody):
    device_id: int = Field(gt=0)
    name: Name100
    data_type: Name50
    unit: Optional[str] = Field(None, max_length=20)
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None

    @model_validator(mode="after")
    def _thresholds(self):
        _check_thresholds(self.threshold_min, self.threshold_max)
        return self


class MonitoringPointUpdate(AdminBody):
    name: Name100 = None  # type: ignore[assignment]
    unit: Optional[str] = Field(None, max_length=20)
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    is_active: bool = None  # type: ignore[assignment]

    @model_validator(mode="after")
    def _thresholds(self):
        _check_thresholds(self.threshold_min, self.threshold_max)
        return self


# ============ 溯源 ============

class TraceabilityConfigCreate(AdminBody):
    name: Name100
    code: Code
    description: Optional[str] = Field(None, max_length=2000)
    land_parcel_id: Optional[int] = Field(None, gt=0)


class TraceabilityConfigUpdate(AdminBody):
    name: Name100 = None  # type: ignore[assignment]
    description: Optional[str] = Field(None, max_length=2000)
    land_parcel_id: Optional[int] = Field(None, gt=0)
    is_active: bool = None  # type: ignore[assignment]


# data_fields：JSON 数组、JSON 字符串或逗号分隔文本，端点统一规范化为 JSON 数组字符串
DataFields = Annotated[Optional[Union[List[str], str]], Field(None)]


class TraceabilityNodeCreate(AdminBody):
    config_id: int = Field(gt=0)
    name: Name100
    node_type: NodeType
    icon: Optional[Icon] = None
    description: Optional[str] = Field(None, max_length=2000)
    sort_order: int = Field(0, ge=0)
    data_fields: DataFields = None


class TraceabilityNodeUpdate(AdminBody):
    name: Name100 = None  # type: ignore[assignment]
    node_type: NodeType = None  # type: ignore[assignment]
    icon: Optional[Icon] = None
    description: Optional[str] = Field(None, max_length=2000)
    sort_order: int = Field(None, ge=0)  # type: ignore[assignment]
    data_fields: DataFields = None
    is_active: bool = None  # type: ignore[assignment]


class TraceabilityRecordCreate(AdminBody):
    node_id: int = Field(gt=0)
    data: Annotated[str, BeforeValidator(_to_json_text)]
    adoption_order_id: Optional[int] = Field(None, gt=0)
    image_url: Optional[Url] = None
    operator: Optional[str] = Field(None, max_length=100)


# ============ C 端用户 / 分组 ============

class UserStatusUpdate(AdminBody):
    is_active: bool


class UserGroupCreate(AdminBody):
    name: Name100
    code: Code
    description: Optional[str] = Field(None, max_length=2000)
    criteria: LooseText = None


class UserGroupUpdate(AdminBody):
    name: Name100 = None  # type: ignore[assignment]
    description: Optional[str] = Field(None, max_length=2000)
    criteria: LooseText = None
    is_active: bool = None  # type: ignore[assignment]


# ============ 营销 ============

class CouponCreate(AdminBody):
    name: Name100
    code: Code
    discount_value: float = Field(gt=0)
    valid_from: datetime
    valid_until: datetime
    type: CouponType = "discount"
    min_amount: float = Field(0, ge=0)
    max_discount: Optional[float] = Field(None, gt=0)
    total_count: int = Field(100, ge=0)
    per_user_limit: int = Field(1, ge=1)
    applicable_products: JsonText = None
    applicable_categories: JsonText = None

    @model_validator(mode="after")
    def _check_range(self):
        if self.valid_until <= self.valid_from:
            raise ValueError("valid_until 必须晚于 valid_from")
        return self


class CouponUpdate(AdminBody):
    name: Name100 = None  # type: ignore[assignment]
    discount_value: float = Field(None, gt=0)  # type: ignore[assignment]
    valid_from: datetime = None  # type: ignore[assignment]
    valid_until: datetime = None  # type: ignore[assignment]
    type: CouponType = None  # type: ignore[assignment]
    min_amount: float = Field(None, ge=0)  # type: ignore[assignment]
    max_discount: Optional[float] = Field(None, gt=0)
    total_count: int = Field(None, ge=0)  # type: ignore[assignment]
    per_user_limit: int = Field(None, ge=1)  # type: ignore[assignment]
    applicable_products: JsonText = None
    applicable_categories: JsonText = None
    is_active: bool = None  # type: ignore[assignment]


class ActivityCreate(AdminBody):
    name: Name100
    type: Name50
    start_time: datetime
    end_time: datetime
    description: Optional[str] = Field(None, max_length=5000)
    rules: JsonText = None
    banner_url: Optional[Url] = None

    @model_validator(mode="after")
    def _check_range(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time 必须晚于 start_time")
        return self


class ActivityUpdate(AdminBody):
    name: Name100 = None  # type: ignore[assignment]
    type: Name50 = None  # type: ignore[assignment]
    start_time: datetime = None  # type: ignore[assignment]
    end_time: datetime = None  # type: ignore[assignment]
    description: Optional[str] = Field(None, max_length=5000)
    rules: JsonText = None
    banner_url: Optional[Url] = None
    status: ActivityStatus = None  # type: ignore[assignment]


# ============ 系统配置 ============

ConfigValue = Union[str, int, float, bool, list, dict]


def config_value_to_text(value: ConfigValue, config_type: str) -> str:
    """把配置值转换为入库字符串；json 类型必须是合法 JSON"""
    if config_type == "json":
        return _to_json_text(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


class SystemConfigCreate(AdminBody):
    keep_blank_fields = frozenset({"value"})
    key: Annotated[str, Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_\-.]+$")]
    value: ConfigValue
    type: ConfigType = "string"
    group: Name50 = "general"
    description: Optional[str] = Field(None, max_length=200)
    is_public: bool = False

    @model_validator(mode="after")
    def _normalize_value(self):
        self.value = config_value_to_text(self.value, self.type)
        return self


class SystemConfigUpdate(AdminBody):
    keep_blank_fields = frozenset({"value"})
    value: ConfigValue


def apply_update(obj: Any, body: BaseModel, exclude: FrozenSet[str] = frozenset()) -> dict:
    """把 Update 模型中显式传入的字段写回 ORM 对象，返回实际应用的字段字典"""
    changes = body.model_dump(exclude_unset=True)
    for field, value in changes.items():
        if field not in exclude:
            setattr(obj, field, value)
    return changes
