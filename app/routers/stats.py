from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.link import Link
from app.models.click import Click
from app.schemas.link import LinkStats, DailyStat
from app.utils.security import get_current_user
from app.models.user import User
from datetime import datetime, timedelta
from typing import List

router = APIRouter()


# 获取某个短链接的统计数据
@router.get("/links/{link_id}/stats")
def get_link_stats(
        link_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    # 先确认链接存在且属于当前用户
    link = db.query(Link).filter(
        Link.id == link_id,
        Link.user_id == current_user.id
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="链接不存在")
    # 总访问量
    total_clicks = db.query(func.count(Click.id)).filter(
        Click.link_id == link_id
    ).scalar()
    # 今日访问量
    today = datetime.now().date()
    today_clicks = db.query(func.count(Click.id)).filter(
        Click.link_id == link_id,
        func.date(Click.clicked_at) == today
    ).scalar()
    # 最近7天按天统计
    seven_days_ago = today - timedelta(days=6)
    daily_stats = db.query(
        func.date(Click.clicked_at).label("date"),
        func.count(Click.id).label("count")
    ).filter(
        Click.link_id == link_id,
        func.date(Click.clicked_at) >= seven_days_ago
    ).group_by(
        func.date(Click.clicked_at)
    ).order_by(
        func.date(Click.clicked_at)
    ).all()
    # 补全没有访问量的日期（显示为0）
    daily_dict = {str(row.date): row.count for row in daily_stats}
    result = []
    for i in range(7):
        date = seven_days_ago + timedelta(days=i)
        count = daily_dict.get(str(date), 0)
        result.append({"date": str(date), "count": count})

    return LinkStats(
        total_clicks=total_clicks or 0,
        today_clicks=today_clicks or 0,
        daily_stats=result
    )
