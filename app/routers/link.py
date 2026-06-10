from app.utils.ai_analyzer import analyze_url_safety, fetch_page_title
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.models.link import Link
from starlette.requests import Request
from app.models.click import Click
from datetime import datetime
from app.schemas.link import LinkCreate, LinkResponse
from app.utils.security import get_current_user
from app.models.user import User
from app.utils.short_code import generate_short_code
from app.config import get_settings
from starlette.responses import RedirectResponse

settings = get_settings()

router = APIRouter()


# 生成短码链接
@router.post('/links')
def create_link(
        link_data: LinkCreate,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # 生成短码
    short_code = generate_short_code()
    # 创建 Link 对象
    new_link = Link(
        short_code=short_code,
        original_url=link_data.original_url,
        user_id=current_user.id  # 关联当前用户
    )
    # 6. 存入数据库
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    # ★ 新增：后台触发AI安全分析
    background_tasks.add_task(analyze_and_update_link, new_link.id,
                              new_link.original_url)
    short_url = f"{settings.BASE_URL}/{short_code}"
    return LinkResponse(
        id=new_link.id,
        short_code=new_link.short_code,
        original_url=new_link.original_url,
        short_url=short_url,
        title=new_link.title or "",
        safety_level=new_link.safety_level or "待分析",
        safety_score=new_link.safety_score,
        safety_reason=new_link.safety_reason or "",
        created_at=new_link.created_at
    )


# 查看当前用户的所有短链接
@router.get("/links")
def list_my_links(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # 查询当前用户的链接总数
    total = db.query(Link).filter(Link.user_id == current_user.id).count()
    # 查询当前用户的链接列表（按创建时间倒序）
    links = (
        db.query(Link)
        .filter(Link.user_id == current_user.id)
        .order_by(Link.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    # 转换成响应格式
    link_responses = [
        LinkResponse(
            id=link.id,
            short_code=link.short_code,
            original_url=link.original_url,
            short_url=f"{settings.BASE_URL}/{link.short_code}",
            title=link.title or "",
            safety_level=link.safety_level or "待分析",
            safety_score=link.safety_score,
            safety_reason=link.safety_reason or "",
            created_at=link.created_at
        )
        for link in links
    ]
    return {"total": total, "links": link_responses}


@router.get("/{short_code}")
def redirect_to_url(
        short_code: str,
        request: Request,  # 获取请求信息
        db: Session = Depends(get_db)
):
    #  根据短码查数据库
    link = db.query(Link).filter(Link.short_code == short_code).first()
    # 找不到就 404
    if not link:
        raise HTTPException(status_code=404, detail="链接不存在")
    #  检查是否过期
    #  记录这次访问
    click = Click(
        link_id=link.id,
        clicked_at=datetime.now(),
        ip_address=request.client.host,  # 访问者IP
        user_agent=request.headers.get("user-agent", ""),  # 浏览器信息
        referer=request.headers.get("referer", ""),  # 从哪来的
    )
    db.add(click)
    db.commit()
    # 302 重定向
    return RedirectResponse(url=link.original_url, status_code=302)


# 查看单个链接详情
@router.get("/links/{link_id}")
def get_link_detail(
        link_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    link = db.query(Link).filter(
        Link.id == link_id,
        Link.user_id == current_user.id
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="链接不存在")
    return LinkResponse(
        id=link.id,
        short_code=link.short_code,
        original_url=link.original_url,
        short_url=f"{settings.BASE_URL}/{link.short_code}",
        title=link.title or "",
        safety_level=link.safety_level or "待分析",
        safety_score=link.safety_score,
        safety_reason=link.safety_reason or "",
        created_at=link.created_at
    )


# 删除链接
@router.delete("/links/{link_id}")
def delete_link(
        link_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    link = db.query(Link).filter(
        Link.id == link_id,
        Link.user_id == current_user.id
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="链接不存在")

    db.delete(link)
    db.commit()
    return {"detail": "删除成功"}


def analyze_and_update_link(link_id: int, url: str):
    """
    后台任务：抓取网页标题 + AI分析安全性 → 更新数据库
    """
    db = SessionLocal()
    try:
        # 1. 抓取网页标题
        title = fetch_page_title(url)
        # 2. AI分析安全性
        result = analyze_url_safety(url, title)
        # 3. 更新数据库
        link = db.query(Link).filter(Link.id == link_id).first()
        if link:
            link.title = title
            link.safety_score = result["score"]
            link.safety_level = result["level"]
            link.safety_reason = result["reason"]
            db.commit()
    finally:
        db.close()
