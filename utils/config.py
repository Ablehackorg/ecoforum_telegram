from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import pytz

def tashkent_now():
    tz = pytz.timezone("Asia/Tashkent")
    return datetime.now(tz)

admins = [5012184829]
shahar_viyolat = [
    "Toshkent shahri", "Toshkent viloyati", "Andijon shahri", "Andijon viloyati", "Namangan shahri", "Namangan viloyati",
    "Fargʻona shahri", "Fargʻona viloyati", "Samarqand shahri", "Samarqand viloyati", "Buxoro shahri", "Buxoro viloyati",
    "Navoiy shahri", "Navoiy viloyati", "Qarshi shahri", "Qashqadaryo viloyati", "Termiz shahri", "Surxondaryo viloyati",
    "Jizzax shahri", "Jizzax viloyati", "Guliston shahri", "Sirdaryo viloyati", "Urganch shahri", "Xorazm viloyati",
    "Nukus shahri", "Qoraqalpogʻiston Respublikasi"
    ]

TOKEN = "7228028255:AAHjuOwStmWJmHLPJugR5iNWLwaEQu_8Wqs"
TIMEZONE = "Asia/Tashkent"

bot_url = "diwa_1_bot"
project_group = "https://t.me/"
project_posts_channel_url = "https://t.me/about_all_with_karyuX"
project_posts_channel = "@about_all_with_karyuX"
project_blogs_channel_url = "https://t.me/about_all_with_karyuX"
project_blogs_channel = "@about_all_with_karyuX"
project_news_channel = "https://t.me/"
guide_for_use = "https://t.me/"
leaderboard_channel_url = "https://t.me/"
leaderboard_channel = "@" #kanal eng faollar

inplace_msg = "Yashil kelajakni birga barpo etamiz 🌱"
start_photo = "https://images.pexels.com/photos/1072824/pexels-photo-1072824.jpeg" 
start_msg = (
    "🌿 Assalomu alaykum va ekologik loyihamizga xush kelibsiz! 🌍\n\n"
    "Bu yerda siz tabiatni asrash, ekologik muammolarni hal qilish va jamiyatga foyda keltiradigan loyihalarda ishtirok etishingiz mumkin.\n\n"
    "📌 Boshlash uchun pastdagi menyudan kerakli bo‘limni tanlang yoki ro‘yxatdan o‘ting!"
)
admin_photo = "https://img.freepik.com/premium-vector/ui-ux-info-graphic-data-graphic-chart-admin-dashboard-vector-illustration_494980-6384.jpg"
admin_msg = (
    "🌿 Ekologik nazorat qo‘lingizda!\n\n"
    "Siz administrator sifatida loyihalarning muvaffaqiyatli ishlashiga javobgarsiz. Bugun qanday yaxshilik qilamiz?\n\n"
    "📋 Quyidagi funksiyalardan birini tanlang:"
)

class sena(StatesGroup):
    id_user = State()
    enter_donation_amount = State()
    region = State()
    age = State()
    sex = State()

    admin_menu = State()
    admin_message_post = State()
    admin_message_photo = State()
    admin_message_button = State()
    admin_message_final = State()

    admin_search_project = State()
    search_by_name = State()
    search_by_project = State()

    admin_new_projects = State()
    admin_new_blogs = State()
    blog_approve_reject = State()
    project_approve_reject = State()

    my_projetcs = State()
    create_project_name = State()
    create_project_description = State()
    create_project_photo = State()
    create_project_helpers = State()
    create_project_donaters = State()
    create_project_final = State()

    user_projects = State()
    show_project = State()
    my_project_edit = State()
    my_project_edit_name = State()
    my_project_edit_description = State()
    my_project_edit_photo = State()
    my_project_edit_quantity = State()
    my_project_edit_amount = State()
    my_project_helpers = State()
    delet_helpers = State()
    my_project_donaters = State()

    my_helped_projects = State()
    helper_project_id = State()
    cancel_helper_project = State()

    my_blogs = State()
    create_blog_name = State()
    create_blog_description = State()
    create_blog_photo = State()
    manage_blog = State()
    edit_blog_title = State()
    edit_blog_content = State()
    edit_blog_photo = State()

    about_company = State()