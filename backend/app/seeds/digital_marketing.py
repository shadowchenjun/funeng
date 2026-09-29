"""
数字营销默认数据（固定数据集，不使用随机数）

- marketing_orders: 最近 14 天的电商订单，商品名称/单价取自 products 表（缺失时使用备用值）
- marketing_traffic_daily: 最近 14 天的渠道流量（访客/粉丝/推送/直播）

注意：main.py 不直接调用本模块，由 app/seeds/smart_agriculture.py 的
seed_smart_agriculture() 调用。仅在对应表为空时写入。
"""
import math
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.smart_agriculture import MarketingOrder, MarketingTrafficDaily

DAYS = 14
CHANNELS = ["APP", "小程序", "网页", "直播间"]
CUSTOMERS = ["王丽", "李强", "张敏", "刘洋", "陈静", "杨帆", "赵磊", "黄婷", "周杰", "吴芳",
             "徐明", "孙悦", "马超", "朱琳", "胡斌", "郭燕"]
# 备用商品（products 表缺失对应商品时使用）
FALLBACK_PRODUCTS = [
    ("有机西红柿", 12.8), ("红富士苹果", 15.0), ("东北大米", 55.0), ("新鲜草莓", 35.0),
    ("高山茶叶", 128.0), ("土鸡蛋", 2.5), ("农家腊肉", 68.0), ("赣南脐橙", 18.0),
]
# 每天的订单数（下标 0 = 13 天前，最后一个 = 今天）
ORDERS_PER_DAY = [3, 4, 3, 5, 4, 6, 5, 4, 6, 7, 5, 6, 8, 5]


def _status(days_ago: int, k: int) -> str:
    if days_ago >= 4:
        return "已取消" if k % 9 == 4 else "已完成"
    if days_ago >= 2:
        return ["配送中", "已完成", "配送中", "已取消"][k % 4]
    return ["待付款", "待发货", "待发货", "配送中", "待付款"][k % 5]


def seed_digital_marketing(db: Session) -> bool:
    """写入默认数据；有新数据写入时返回 True"""
    changed = False
    now = datetime.now().replace(second=0, microsecond=0)
    today = now.replace(hour=0, minute=0)

    if db.query(MarketingOrder).first() is None:
        existing = {p.name: p for p in db.query(Product).all()}
        products = []
        for name, price in FALLBACK_PRODUCTS:
            p = existing.get(name)
            products.append((p.id if p else None, name, float(p.price) if p else price))
        k = 0
        for d, count in enumerate(ORDERS_PER_DAY):
            days_ago = DAYS - 1 - d
            day_start = today - timedelta(days=days_ago)
            for j in range(count):
                pid, pname, price = products[k % len(products)]
                qty = 1 + (k * 7) % 6
                if price < 5:
                    qty *= 10  # 鸡蛋等低价商品按盒/批量购买
                if days_ago == 0:
                    # 今天的订单均匀分布在 0 点到当前时刻之间，避免出现未来时间
                    created = day_start + (now - day_start) * (j + 1) / (count + 1)
                    created = created.replace(second=0, microsecond=0)
                else:
                    created = day_start + timedelta(hours=8 + (j * 5 + d) % 14, minutes=(k * 13) % 60)
                db.add(MarketingOrder(
                    order_no=f"ORD{day_start:%Y%m%d}{j + 1:04d}",
                    customer_name=CUSTOMERS[k % len(CUSTOMERS)],
                    product_id=pid, product_name=pname, quantity=qty,
                    unit_price=price, amount=round(price * qty, 2),
                    status=_status(days_ago, k),
                    channel=CHANNELS[(k + d) % len(CHANNELS)],
                    created_at=created,
                ))
                k += 1
        changed = True

    if db.query(MarketingTrafficDaily).first() is None:
        followers = 27000
        for d in range(DAYS):
            day = today - timedelta(days=DAYS - 1 - d)
            weekend = day.weekday() >= 5
            new_followers = int(600 + 200 * math.sin(d / 2) + (150 if weekend else 0))
            followers += new_followers
            sent = 1200 + 40 * (d % 5)
            db.add(MarketingTrafficDaily(
                date=day.strftime("%Y-%m-%d"),
                visitors=int(150 + 20 * math.sin(d / 3) + (30 if weekend else 0)),
                followers_total=followers,
                new_followers=new_followers,
                push_sent=sent,
                push_opened=int(sent * (0.62 + 0.05 * math.cos(d))),
                live_sessions=2 + (d % 3) + (1 if weekend else 0),
            ))
        changed = True

    if changed:
        db.commit()
    return changed
