from sqlalchemy import desc, asc, func
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.orm import selectinload, joinedload
from database.db import SessionLocal
from database.models import Users, Projects, Helpers, Donaters, Blogs

## REGISTRATION USER
def register_user(telegram_id: int, name: str, region: str, age: int, sex: str):
    with SessionLocal() as db:
        user = db.query(Users).filter_by(telegram_id=telegram_id).first()
        if not user:
            db.add(Users(telegram_id=telegram_id, name=name, region=region, age=age, sex=sex))
            db.commit()

## GET USER WITH TG_ID
def get_user_by_telegram_id(telegram_id: int) -> Users | None:
    with SessionLocal() as db:
        return db.query(Users).filter_by(telegram_id=telegram_id).first()


## GET ALL USERS
def get_all_users() -> list[Users]:
    with SessionLocal() as db:
        return db.query(Users).options(
                joinedload(Users.projects),
                joinedload(Users.blogs),
                joinedload(Users.helpers),
            ).all()
    

## GENERATE USER STATISTIC
def generate_user_stats(telegram_id: int) -> str:
    with SessionLocal() as db:
        user = db.query(Users).filter_by(telegram_id=telegram_id).first()
        if not user:
            return "❌ Foydalanuvchi topilmadi."

        projects = db.query(Projects).filter_by(user_id=user.id).all()

        if not projects:
            return "📊 Statistika: \n\nSiz hali loyiha yaratmagansiz."
        
        project_ids = [p.id for p in projects]
        total_projects = len(projects)
        finished = sum(1 for p in projects if p.status == "closed")
        active = sum(1 for p in projects if p.status == "active")
        waiting = total_projects - finished - active

        total_helpers = db.query(func.count(Helpers.id)).filter(Helpers.project_id.in_(project_ids)).scalar() or 0
        total_donated = db.query(func.sum(Donaters.amount)).filter(Donaters.project_id.in_(project_ids)).scalar() or 0

        avg_helpers = round(total_helpers / total_projects, 1) if total_projects > 0 else 0

        top_helper_project = None
        top_donated_project = None
        max_helpers = 0
        max_donated = 0

        for project in projects:
            h_count = db.query(func.count(Helpers.id)).filter(Helpers.project_id == project.id).scalar() or 0
            if h_count > max_helpers:
                max_helpers = h_count
                top_helper_project = project
            
            d_amount = db.query(func.sum(Donaters.amount)).filter(Donaters.project_id == project.id).scalar() or 0
            if d_amount > max_donated:
                max_donated = d_amount
                top_donated_project = project
            
        msg_text = (
            "📊 <b>Statistika</b>:\n\n"
            f"📁 <b>Umumiy loyihalar</b>: {total_projects} ta\n"
            f"✅ <b>Yakunlangan</b>: {finished} ta\n"
            f"🟢 <b>Faol</b>: {active} ta\n"
            f"⏳ <b>Kutilayotgan</b>: {waiting} ta\n\n"
            f"🤝 <b>Umumiy ko‘ngillilar</b>: {total_helpers} ta\n"
            f"💰 <b>Yig‘ilgan mablag‘</b>: {total_donated:_} so‘m\n"
            f"🗂 <b>O‘rtacha ko‘ngillilar soni</b>: {avg_helpers} ta\n\n"
        ) 

        if top_helper_project:
            msg_text += (
                "📈 <b>Eng ko‘p ko‘ngilliga ega loyiha</b>:\n"
                f"🌿 “{top_helper_project.name}” — <b>{max_helpers} ko‘ngilli</b>\n\n"
            )

        if top_donated_project:
            msg_text += (
                "💎 <b>Eng ko‘p homiylik yig‘gan loyiha</b>:\n"
                f"♻️ “{top_donated_project.name}” — <b>{max_donated:_} so‘m</b>"
            )

        return msg_text


## GENERATE USER NEW PROJECT
def generate_user_project(user_id: int, name: str, description: str, photo_id: str, total_quantity: int, total_amount: int) -> Projects:
    with SessionLocal() as db:
        new_project = Projects(
            user_id=user_id,
            name=name,
            description=description,
            photo_id=photo_id,
            total_quantity=total_quantity,
            total_amount=total_amount,
        )
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        return new_project


## GENERATE USER NEW BLOG
def generate_user_blog(user_id: int, title: str, content: str, photo_id: str) -> Blogs:
    with SessionLocal() as db:
        new_blog = Blogs(
            user_id=user_id,
            title=title,
            content=content,
            photo_id=photo_id
        )
        db.add(new_blog)
        db.commit()
        db.refresh(new_blog)
        return new_blog


## ADD HELPER TO PROJECT
def add_helper(user_id: int, project_id: int):
    with SessionLocal() as db:
        existing = db.query(Helpers).filter_by(user_id=user_id, project_id=project_id).first()
        if not existing:
            db.add(Helpers(user_id=user_id, project_id=project_id))
            db.commit()


## UPDATE PROJECT
def update_project_field(project_id: int, field: str, value) -> bool:
    with SessionLocal() as db:
        project = db.query(Projects).filter_by(id=project_id).first()
        if not project:
            return False

        setattr(project, field, value)
        db.commit()
        return True


## UPDATE BLOG
def update_blog_field(blog_id: int, field: str, value: str) -> None:
    with SessionLocal() as db:
        blog = db.query(Blogs).filter_by(id=blog_id).first()
        if not blog:
            return None
        setattr(blog, field, value)
        db.commit()


## GET BLOG BY ID
def get_blog_by_id(blog_id: int) -> Blogs | None:
    with SessionLocal() as db:
        return db.query(Blogs).options(
            joinedload(Blogs.user)
        ).filter(Blogs.id == blog_id).first()
    

## GET USER PROJECTS
def get_user_projects(user_id: int) -> list[Projects]:
    with SessionLocal() as db:
        return db.query(Projects).filter_by(user_id=user_id).order_by(Projects.id.desc()).all()


## GET ALL HELPER BY PROJECT
def get_all_helpers_in_project(project_id: int) -> list[int]:
    with SessionLocal() as db:
        return [
            helper.user_id for helper in db.query(Helpers).filter_by(project_id=project_id).all()
        ]


## GET PROJECT BY ID
def get_project_by_id(project_id: int) -> Projects | None:
    with SessionLocal() as db:
        return (
            db.query(Projects)
            .options(
                joinedload(Projects.helpers).joinedload(Helpers.user),
                joinedload(Projects.donaters).joinedload(Donaters.user),
            )
            .filter(Projects.id == project_id)
            .first()
        )


## GET NEW CREATED PROJECTS
def get_unverified_projects() -> list[Projects]:
    with SessionLocal() as db:
        return (
            db.query(Projects)
            .options(
                joinedload(Projects.user).joinedload(Users.projects),
                joinedload(Projects.donaters).joinedload(Donaters.project),
                joinedload(Projects.helpers).joinedload(Helpers.project)
            )
            .filter_by(status='wait')
            .all()
        )


## GET NEW CREATED BLOGS
def get_unverified_blogs() -> list[Blogs]:
    with SessionLocal() as db:
        return (
            db.query(Blogs)
            .options(
                joinedload(Blogs.user).joinedload(Users.blogs))
            .filter_by(is_verified=False)
            .all()
        )


## DELETE USER PROJECT
def delete_user_project(project_id: int, user_id: int):
    with SessionLocal() as db:
        project = db.query(Projects).filter_by(id=project_id, user_id=user_id).first()
        if project:
            db.delete(project)
            db.commit()
            return True
        return False


## DELETE HELPER IN PROJECT
def delete_helper_in_project(user_id: int, project_id: int) -> bool:
    with SessionLocal() as db:
        helper = db.query(Helpers).filter_by(user_id=user_id, project_id=project_id).first()
        if helper:
            db.delete(helper)
            db.commit()
            return True
        return False


## DELETE USER BLOG
def delete_blog(blog_id: int) -> bool:
    with SessionLocal() as db:
        blog = db.query(Blogs).filter_by(id=blog_id).first()
        if blog:
            db.delete(blog)
            db.commit()
            return True
        return False


## GET TOP HELPERS
def get_top_helpers(limit: int) -> list[any]:
    with SessionLocal() as db:
        return (
            db.query(Users.telegram_id, Users.name, func.count(Helpers.project_id).label("project_count"))
            .join(Helpers, Helpers.user_id == Users.id)
            .group_by(Users.id)
            .order_by(desc("project_count"))
            .limit(limit)
            .all()
        )


## GET TOP DONATERS
def get_top_donaters(limit: int = 5) -> list[any]:
    with SessionLocal() as db:
        return (
            db.query(Users.telegram_id, Users.name, func.sum(Donaters.amount).label("total_amount"))
            .join(Donaters, Donaters.user_id == Users.id)
            .group_by(Users.id)
            .order_by(desc("total_amount"))
            .limit(limit)
            .all()
        )


## GET TOP CREATERS OF PROJECTS
def get_top_creators(limit: int = 3) -> list[any]:
    with SessionLocal() as db:
        return (
            db.query(Users.telegram_id, Users.name, func.count(Projects.id).label("project_count"))
            .join(Projects, Projects.user_id == Users.id)
            .group_by(Users.id)
            .order_by(desc("project_count"))
            .limit(limit)
            .all()
        )


## GET HELPER PROJECTS
def get_helper_projects(user_id: int) -> list[Projects]:
    with SessionLocal() as db:
        return (
            db.query(Projects)
            .join(Helpers, Helpers.project_id == Projects.id)
            .filter(Helpers.user_id == user_id)
            .order_by(Projects.created_at.desc())
            .all()
        )


## GET USER BLOGS
def get_user_blogs(user_id: int) -> list[Blogs]:
    with SessionLocal() as db:
        return db.query(Blogs).filter(Blogs.user_id == user_id).order_by(Blogs.created_at.desc()).all()


## GET ALL PROJECTS
def get_all_projects() -> list[Projects]:
    with SessionLocal() as db:
        return db.query(Projects).all()


## GET COUNT OF USERS
def count_users() -> int:
    with SessionLocal() as db:
        return db.query(func.count(Users.id)).scalar()


## GET COUNT OF PROJECTS
def count_projects() -> int:
    with SessionLocal() as db:
        return db.query(func.count(Projects.id)).scalar()


## GET COUNT OF HELPERS
def count_helpers() -> int:
    with SessionLocal() as db:
        return db.query(func.count(Helpers.id)).scalar()


## GET SUM OF DONATES
def count_total_cash() -> int:
    with SessionLocal() as db:
        return db.query(func.sum(Donaters.amount)).scalar() or 0
    

## DELETE USER BLOG
def clean_invalid_blogs():
    with SessionLocal() as db:
        invalid_blogs = db.query(Blogs).outerjoin(Users).filter(Users.id == None).all()
        for blog in invalid_blogs:
            db.delete(blog)
        db.commit()
