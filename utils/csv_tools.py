import csv
from datetime import datetime
from database.functions import get_all_users  
from pathlib import Path

def export_users_to_csv(file_path: str = "users_list.csv") -> str:
    users = get_all_users()  
    file = Path(file_path)

    with file.open(mode='w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Ism", "Telegram ID", "Shahar | Viloyat", "Yoshi", "Jinsi", "Qo‘shilgan sana", "Loyihalar", "Bloglar", "Ko‘ngillilik"])

        for user in users:
            writer.writerow([
                user.name or "Noma'lum",
                user.telegram_id,
                user.region,
                user.age,
                user.sex,
                user.regist_at.strftime('%Y-%m-%d'),
                len(user.projects),
                len(user.blogs),
                len(user.helpers)
            ])

    return str(file)