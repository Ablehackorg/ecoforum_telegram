from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

import database.functions as db
import utils.config as cf

scheduler = AsyncIOScheduler()

def generate_top_users_text() -> str:
    helpers = db.get_top_helpers(limit=5)
    donaters = db.get_top_donaters(limit=5)
    creators = db.get_top_creators(limit=3)

    msg = "🏅 <b>Eng faol foydalanuvchilar</b>\n"
    msg += "Quyidagi foydalanuvchilar platformamizda eng faol bo‘lishdi 👇\n\n"

    msg += "<b>🎯 Top 5 ko‘ngillilar:</b>\n\n"
    for h in helpers:
        msg += f"<a href='tg://user?id={h.telegram_id}'>{h.name or '👤 Nomaʼlum'}</a> — {h.project_count} ta loyiha\n"
    
    msg += "\n<b>💰 Top 5 homiylar:</b>\n\n"
    for d in donaters:
        msg += f"<a href='tg://user?id={d.telegram_id}'>{d.name or '👤 Nomaʼlum'}</a> — {int(d.total_amount):,} so‘m\n"

    msg += "\n<b>🆕 Top 3 loyihachi:</b>\n\n"
    for c in creators:
        msg += f"<a href='tg://user?id={c.telegram_id}'>{c.name or '👤 Nomaʼlum'}</a> — {c.project_count} ta loyiha\n"

    return msg

async def send_top_users(bot: Bot):
    msg_text = generate_top_users_text()
    await bot.send_message(chat_id=cf.leaderboard_channel, text=msg_text, parse_mode="HTML")

def setup_scheduler(bot: Bot):
    scheduler.add_job(send_top_users, "cron", day=1, hour=9, minute=0, args=[bot])
    scheduler.start()