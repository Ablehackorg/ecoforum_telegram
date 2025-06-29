from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

import database.functions as db
import utils.config as cf

## BACK BUTTON FOR ALL
def back_button():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🔙 Orqaga"))
    return builder.as_markup(resize_keyboard=True, input_field_placeholder=cf.inplace_msg)

## ACCEPT & CANCEL
def create_project_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="✅ Tasdiqlayman", callback_data="Tasdiqlash"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="Bekor qilish"),
    )
    return builder.as_markup()

## REGIONS
def regions_keyboard():
    builder = ReplyKeyboardBuilder()
    for i in cf.shahar_viyolat:
        builder.add(KeyboardButton(text=i))
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True, input_field_placeholder="🏙 Qaysi viloyatda yashaysiz?")

## BACK BUTTON FOR AGE
def back_button_age():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🔙 Orqaga"))
    return builder.as_markup(resize_keyboard=True, input_field_placeholder="📅 Yoshingizni kiriting (faqat raqamlarda)...")

## SEXS
def sexs_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="👩‍🌾 Ayol"), KeyboardButton(text="👨‍🌾 Erkak"))
    return builder.as_markup(resize_keyboard=True, input_field_placeholder="🚻 Jinsingizni tanlang: Erkak yoki Ayol")


## MAIN MENU
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="📂 Mening loyihalarim"),
        KeyboardButton(text="🤝 Ko‘ngillilik faoliyatim"),
        KeyboardButton(text="📝 Mening bloglarim"),
        KeyboardButton(text="🏢 Loyiha haqida")
    )
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, input_field_placeholder=cf.inplace_msg)


## ADMIN PANEL
def admin_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="📢 Hammaga xabar yuborish"),
        KeyboardButton(text="🆕 Yangi loyihalar"),
        KeyboardButton(text="📝 Yangi bloglar"),
        KeyboardButton(text="🔍 Loyiha izlash"),
        KeyboardButton(text="👥 Foydalanuvchilar ro‘yxati"),
        KeyboardButton(text="📊 Statistika"),
        KeyboardButton(text="🔙 Orqaga")
    )
    builder.adjust(1, 2, 2, 2)
    return builder.as_markup(resize_keyboard=True, input_field_placeholder=cf.inplace_msg)


## MENU MY PROJECTS
def my_projects_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="🆕 Yangi loyiha yaratish"),
        KeyboardButton(text="📋 Loyihalar ro‘yxati"),
        KeyboardButton(text="📊 Statistika"),
        KeyboardButton(text="🔙 Orqaga"),
    )
    builder.adjust(1, 1, 2)
    return builder.as_markup(resize_keyboard=True, input_field_placeholder=cf.inplace_msg)


## MENU LIST OF PROJECTS
def list_of_projects_menu(telegram_id: int):
    builder = ReplyKeyboardBuilder()
    projects = db.get_user_projects(user_id=telegram_id)

    if not projects:
        builder.add(KeyboardButton(text="❌ Loyihalaringiz topilmadi"))
    else:
        project_names = [
            p.name[:30] + "…" if len(p.name) > 30 else p.name for p in projects
        ]
        for name in project_names:
            builder.add(KeyboardButton(text=name))
        builder.adjust(3)

    builder.add(KeyboardButton(text="🔙 Orqaga"))
    return builder.as_markup(resize_keyboard=True, input_field_placeholder=cf.inplace_msg)


## 
def show_project(status: str):
    builder = InlineKeyboardBuilder()
    if status in ["check", "wait"]:
        builder.add(
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data="edit_project"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data="delete_project"),
        )
    builder.add(
        InlineKeyboardButton(text="🤝 Ko‘ngillilar", callback_data="project_helpers"),
        InlineKeyboardButton(text="💰 Homiylar", callback_data="project_donaters"),
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="project_back"),
    )
    builder.adjust(2)
    return builder.as_markup()


def my_project_edit():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📝 Loyiha nomi", callback_data="edit_name"),
        InlineKeyboardButton(text="📄 Tavsifni o‘zgartirish", callback_data="edit_description"),
        InlineKeyboardButton(text="🖼 Rasmni almashtirish", callback_data="edit_photo"),
        InlineKeyboardButton(text="👥 Ko‘ngillilar soni", callback_data="edit_helpers_quantity"),
        InlineKeyboardButton(text="💸 Mablag‘ maqsadi", callback_data="edit_total_amount"),
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="back"),
    )
    builder.adjust(1, 2, 2, 1)
    return builder.as_markup()


def my_project_helpers_menu():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🗑 Ko‘ngillini o‘chirish", callback_data="delet_helper"),
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="back"),
    )
    return builder.as_markup()


def my_project_helpers(project_id: int):
    builder = InlineKeyboardBuilder()
    project = db.get_project_by_id(project_id=project_id)
    helpers_name = project.helpers
    if helpers_name:
        for helper in helpers_name:
            name = helper.user.name or f"👤 {helper.user.telegram_id}"
            builder.add(InlineKeyboardButton(text=name, callback_data=f"helper_{helper.user.telegram_id}"))
    builder.adjust(3)
    builder.add(InlineKeyboardButton(text="🔙 Orqaga", callback_data="back"))
    return builder.as_markup()


def my_project_donaters(project_id: int):
    builder = InlineKeyboardBuilder()
    project = db.get_project_by_id(project_id=project_id)
    donaters = project.donaters
    if donaters:
        for donater in donaters:
            name = donater.user.name or f"👤 {donater.user.telegram_id}"
            builder.add(InlineKeyboardButton(text=name, callback_data=f"donater_{donater.user.telegram_id}"))
    builder.adjust(3)
    builder.add(InlineKeyboardButton(text="🔙 Orqaga", callback_data="back"))
    return builder.as_markup()


## MENU MY HELPED PROJECTS
def helped_projects_keyboard(projects: list):
    builder = ReplyKeyboardBuilder()
    for project in projects:
        builder.add(KeyboardButton(text=project.name[:30] + "…" if len(project.name) > 30 else project.name))
    builder.add(KeyboardButton(text="🔙 Orqaga"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, input_field_placeholder=cf.inplace_msg)


def helper_cancel():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="❌ Loyiha ishtirokidan chiqish", callback_data="cancel_helper"),
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")
    )
    return builder.as_markup()


def my_blogs_menu(blogs: list):
    builder = ReplyKeyboardBuilder()
    if blogs:
        for blog in blogs:
            builder.add(KeyboardButton(text=blog.title))
    builder.adjust(3)
    builder.row(
        KeyboardButton(text="➕ Yangi blog qo‘shish"),
        KeyboardButton(text="🔙 Orqaga"),
    )
    return builder.as_markup(resize_keyboard=True, input_field_placeholder=cf.inplace_msg)


def my_blog_manage():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="✏️ Nomi", callback_data="edit_blog_title"),
        InlineKeyboardButton(text="📝 Tavsifi", callback_data="edit_blog_content"),
        InlineKeyboardButton(text="📸 Rasm", callback_data="edit_blog_photo"),
        InlineKeyboardButton(text="🗑 O‘chirish", callback_data="delete_blog"),
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="back"),
    )
    builder.adjust(2, 1, 2)
    return builder.as_markup()


def about_project_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="💬 Umumiy guruh", url=cf.project_group),
        InlineKeyboardButton(text="📢 Loyihalar kanali", url=cf.project_posts_channel_url),
        InlineKeyboardButton(text="📝 Bloglar kanali", url=cf.project_blogs_channel_url),
        InlineKeyboardButton(text="📰 Yangiliklar", url=cf.project_news_channel),
        InlineKeyboardButton(text="📘 Qo‘llanma", url=cf.guide_for_use),
        InlineKeyboardButton(text="🏅 Eng faol foydalanuvchilar", url=cf.leaderboard_channel_url),
    )
    builder.adjust(1, 2, 2, 1)
    return builder.as_markup()


def admin_search_projects():
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="🔎 Muallif bo‘yicha"),
        KeyboardButton(text="🔎 Loyiha bo‘yicha"),
        KeyboardButton(text="🔙 Orqaga")
    )
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, input_field_placeholder=cf.inplace_msg)


def admin_message_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="⏭️ O‘tkazib yuborish"),
        KeyboardButton(text="🔙 Orqaga")
    )
    return builder.as_markup(resize_keyboard=True, input_field_placeholder=cf.inplace_msg)


def confirm_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📨 Yuborish"), KeyboardButton(text="🔙 Orqaga"))
    return builder.as_markup(resize_keyboard=True, input_field_placeholder=cf.inplace_msg)


def admin_project_review(project_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data=f"approve_project:{project_id}")
    builder.button(text="❌ Rad etish", callback_data=f"reject_project:{project_id}")
    return builder.as_markup()


def project_post_keyboard(project_id):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🤝 Ko‘ngilli bo‘lish",
        url=f"https://t.me/{cf.bot_url}?start=join_helper_{project_id}"
    )
    builder.button(
        text="💰 Homiylik qilish",
        url=f"https://t.me/{cf.bot_url}?start=join_donater_{project_id}"
    )
    return builder.as_markup()


def admin_blog_review(blog_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data=f"approve_blog:{blog_id}")
    builder.button(text="❌ Rad etish", callback_data=f"reject_blog:{blog_id}")
    return builder.as_markup()

