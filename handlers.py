from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError
from asyncio import sleep
from aiogram import Bot, Router, F, types
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f
from utils.csv_tools import export_users_to_csv

import database.functions as db
import keyboards as kb
import utils.config as cf

bot = Bot(token=cf.TOKEN)
router = Router()


@router.message(F.text.startswith("/start"))
async def register_user(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = db.get_user_by_telegram_id(telegram_id=user_id)
    if user:
        await state.update_data(id_user=user.id)
        text = message.text
        if text.startswith("/start join_helper_"):
            project_id = int(text.split("join_helper_")[1])
            project_helpers = db.get_all_helpers_in_project(project_id=project_id)
            if user.id not in project_helpers:
                db.add_helper(user_id=user.id, project_id=project_id)
                await bot.send_message(chat_id=user_id, text="🤝 Siz loyiha ko‘ngillisi sifatida muvaffaqiyatli qo‘shildingiz!")
                return await bot.send_photo(chat_id=user_id, photo=cf.start_photo, caption=cf.start_msg, reply_markup=kb.main_menu(), parse_mode="HTML")
            else:
                await message.answer("ℹ️ Siz allaqachon ushbu loyiha ko‘ngillisi sifatida qo‘shilgansiz.")
                return await bot.send_photo(chat_id=user_id, photo=cf.start_photo, caption=cf.start_msg, reply_markup=kb.main_menu(), parse_mode="HTML")
            
        elif text.startswith("/start join_donater_"):
            project_id = int(text.split("join_donater_")[1])
            await state.update_data(project_id=project_id)
            await bot.send_message(chat_id=user_id, text=
                "💰 <b>Homiylik qilish</b>\n\n"
                "Iltimos, ushbu loyiha uchun qancha miqdorda mablag‘ yubormoqchi ekanligingizni yozing (so‘mda):\n\n"
                "Masalan: <code>50000</code>",
                parse_mode="HTML", reply_markup=kb.back_button())
            return await state.set_state(cf.sena.enter_donation_amount)

        await bot.send_photo(chat_id=user_id, photo=cf.start_photo, caption=cf.start_msg, reply_markup=kb.main_menu())
    else:
        msg_text = (
            "👋 Assalomu alaykum, do‘stimiz!"
            "\nSizni loyihamizda ko‘rib turganimiz — biz uchun katta baxt! 😊"  
            "\nKeling, birgalikda ekologiyamiz uchun foydali ishlar qilamiz!"
            "\n\nBoshlash uchun, iltimos, o‘zingiz haqida biroz ma’lumot bering."
            "\n🗺 Qaysi shahar yoki viloyatdan ekanligingizni tanlang ⬇️"
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.regions_keyboard())
        await state.set_state(cf.sena.region)


@router.message(cf.sena.enter_donation_amount)
async def menu_enter_donation_amount(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_input = message.text.strip()
    if message.text == "🔙 Orqaga":
        await bot.send_photo(chat_id=user_id, photo=cf.start_photo, caption=cf.start_msg, reply_markup=kb.main_menu(), parse_mode="HTML")
        return await state.clear()

    if not user_input.isdigit() or int(user_input) <= 0:
        return await message.answer("⚠️ Iltimos, to‘g‘ri miqdorni kiriting. Masalan: <code>50000</code>", parse_mode="HTML")

    amount = int(user_input)
    data = await state.get_data()
    project_id = data.get("project_id")
    pay_url = f"https://example.com/pay?project={project_id}&amount={amount}"
    msg_text = (
        f"💰 <b>Homiylik</b>\n\n"
        f"Siz <b>{amount:_} so‘m</b> miqdorida homiylik qilmoqchisiz.\n"
        f"To‘lovni amalga oshirish uchun quyidagi tugmani bosing 👇"
    )
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text=f"💳 {amount:_} so‘m to‘lash", url=pay_url)]])
    await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=keyboard, parse_mode="HTML")
    await state.clear()


@router.message(cf.sena.region)
async def register_user_region(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text in cf.shahar_viyolat:
        await state.update_data(region=message.text)
        msg_text = (
            "✅ Ajoyib, viloyatingiz saqlandi!\n\n"
            "👤 Endi iltimos, yoshingizni raqam shaklida kiriting:"
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.back_button_age())
        await state.set_state(cf.sena.age)
    else:
        msg_text = (
            "❌ Kechirasiz, bu shahar yoki viloyat ro‘yxatda topilmadi.\n\n"
            "Iltimos, tugmalardan birini tanlang yoki qaytadan urinib ko‘ring ⬇️"
        )
        await bot.send_message(chat_id=user_id, text=msg_text)


@router.message(cf.sena.age)
async def register_user_region(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.strip()
    if text.isdigit():
        age = int(text)
        await state.update_data(age=age)
        msg_text = (
            "✅ Yoshingiz qabul qilindi!\n\n"
            "👤 Endi iltimos, jinsingizni tanlang:"
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.sexs_keyboard())
        await state.set_state(cf.sena.sex)
    elif message.text == "⬅️ Ortga":
        msg_text = "🔙 Ortga qaytdingiz. Iltimos, shahringiz yokida viloyatingizni qayta tanlang:"
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.regions_keyboard())
        await state.set_state(cf.sena.region)
    else:
        msg_text = "❗ Iltimos, faqat raqamlardan iborat yosh kiriting."
        await bot.send_message(chat_id=user_id, text=msg_text)


@router.message(cf.sena.sex)
async def register_user_region(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text in ["👨‍🌾 Erkak", "👩‍🌾 Ayol"]:
        sex = "F" if message.text == "👩‍🌾 Ayol" else "M"
        data = await state.get_data()
        msg_text = (
            "🎉 Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!\n\n"
            "Endi siz bizning ekologik loyihamizda ishtirok etishingiz mumkin 💚"
        )
        db.register_user(telegram_id=user_id, name=message.from_user.full_name, region=data['region'], age=int(data['age']), sex=sex)
        user = db.get_user_by_telegram_id(telegram_id=user_id)
        await state.update_data(id_user=user.id)
        await bot.send_message(chat_id=user_id, text=msg_text)
        await bot.send_photo(chat_id=user_id, photo=cf.start_photo, caption=cf.start_msg, reply_markup=kb.main_menu())
        await state.clear()
    elif message.text == "⬅️ Ortga":
        msg_text = "🔙 Ortga qaytdingiz. Iltimos, yoshingizni qayta kiriting:"
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.back_button())
        await state.set_state(cf.sena.age)
    else:
        msg_text = (
            "❗ Iltimos, jinsingizni faqat berilgan tugmalardan tanlang: Erkak yoki Ayol."
        )
        await bot.send_message(chat_id=user_id, text=msg_text)


@router.message(lambda msg: msg.text == "/admin" and msg.from_user.id in cf.admins)
async def admin_panel(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await bot.send_photo(chat_id=user_id, photo=cf.admin_photo, caption=cf.admin_msg, reply_markup=kb.admin_menu())
    await state.set_state(cf.sena.admin_menu)


@router.message(lambda msg: msg.text == "📂 Mening loyihalarim")
async def my_projects(message: Message, state: FSMContext):
    user_id = message.from_user.id
    msg_text = (
        "🗂 <b>Shaxsiy loyihalaringiz bo‘limi</b>\n\n"
        "Bu yerda siz yaratgan loyihalarni:\n"
        "✏️ Tahrirlash\n"
        "📊 Natijalarini ko‘rish\n"
        "🔄 Faolligini kuzatish imkoniyatiga egasiz.\n\n"
        "💡 Sizning tashabbuslaringiz jamiyat uchun katta o‘zgarishlar yasashi mumkin 🌍"
    )
    await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_projects_menu(), parse_mode="HTML")
    await state.set_state(cf.sena.my_projetcs)


@router.message(cf.sena.my_projetcs)
async def menu_my_projects(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "🆕 Yangi loyiha yaratish":
        msg_text = (
            "🆕 <b>Yangi loyiha yaratish</b>\n\n"
            "Ijtimoiy muammo, ekologik tashabbus yoki ko‘ngillilarni jalb qiladigan g‘oya bormi?\n\n"
            "📌 Endi siz yangi loyihangizni shu yerda ro‘yxatdan o‘tkazishingiz mumkin!\n\n"
            "✍️ Loyiha nomi, maqsadi va kerakli ko‘ngillilar sonini kiriting — biz esa uni jamoatchilik e’tiboriga havola qilamiz!\n\n"
            "🚀 Keling, birgalikda jamiyat uchun foydali ishlarni amalga oshiramiz!\n\n"
            "📝 Boshlash uchun, loyihangiz nomini kiriting:"
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.back_button(), parse_mode="HTML")
        await state.set_state(cf.sena.create_project_name)
    elif message.text == "📋 Loyihalar ro‘yxati":
        msg_text = (
            "📋 <b>Siz yaratgan loyihalar ro‘yxati</b>\n\n"
            "Bu yerda siz ilgari yaratgan loyihalaringizni ko‘rishingiz mumkin. "
            "Har bir loyiha – bu ijtimoiy o‘zgarish sari tashlangan qadamingiz. 🌱\n\n"
            "⬇️ Ko‘rish uchun kerakli loyihani tanlang:"
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.list_of_projects_menu(telegram_id=user_id), parse_mode="HTML")
        await state.set_state(cf.sena.user_projects)
    elif message.text == "📊 Statistika":
        await bot.send_message(chat_id=user_id, text=db.generate_user_stats(telegram_id=user_id), parse_mode="HTML")
    elif message.text == "🔙 Orqaga":
        await bot.send_photo(chat_id=user_id, photo=cf.start_photo, caption=cf.start_msg, reply_markup=kb.main_menu())
        await state.clear()


@router.message(cf.sena.create_project_name)
async def menu_create_project_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "🔙 Orqaga":
        msg_text = (
            "🗂 <b>Shaxsiy loyihalaringiz bo‘limi</b>\n\n"
            "Bu yerda siz yaratgan loyihalarni:\n"
            "✏️ Tahrirlash\n"
            "📊 Natijalarini ko‘rish\n"
            "🔄 Faolligini kuzatish imkoniyatiga egasiz.\n\n"
            "💡 Sizning tashabbuslaringiz jamiyat uchun katta o‘zgarishlar yasashi mumkin 🌍"
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_projects_menu(), parse_mode="HTML")
        await state.set_state(cf.sena.my_projetcs)
    else:
        if message.text:
            msg_text = (
                "✅ Ajoyib nom! Endi loyihangizni qisqacha tavsiflab bering.\n\n"
                "📄 <b>Loyiha tavsifi</b>\n\n"
                "Endi iltimos, loyihangiz haqida qisqacha va tushunarli tavsif yozing.\n\n"
                "📝 Tavsifda quyidagilar bo‘lishi mumkin:\n"
                "• Loyiha maqsadi\n"
                "• Qanday muammoni hal qiladi\n"
                "• Ko‘ngillilar qanday yordam berishi mumkin\n\n"
                "💡 Masalan:\n"
                "“Mahallamizdagi bolalar uchun ekologik o‘yin maydonchasi quramiz. Ko‘ngillilar dizayn, tozalash va qurilish ishlarida yordam berishadi.”"
            )
            await state.update_data(create_project_name=message.text)
            await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.back_button(), parse_mode="HTML")
            await state.set_state(cf.sena.create_project_description)
        else:
            await bot.send_message(chat_id=user_id, text="⚠️ Iltimos, faqatgina rasm yuboring.\n")


@router.message(cf.sena.create_project_description)
async def menu_create_project_description(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "🔙 Orqaga":
        msg_text = (
            "🆕 <b>Yangi loyiha yaratish</b>\n\n"
            "Ijtimoiy muammo, ekologik tashabbus yoki ko‘ngillilarni jalb qiladigan g‘oya bormi?\n\n"
            "📌 Endi siz yangi loyihangizni shu yerda ro‘yxatdan o‘tkazishingiz mumkin!\n\n"
            "✍️ Loyiha nomi, maqsadi va kerakli ko‘ngillilar sonini kiriting — biz esa uni jamoatchilik e’tiboriga havola qilamiz!\n\n"
            "🚀 Keling, birgalikda jamiyat uchun foydali ishlarni amalga oshiramiz!\n\n"
            "📝 Boshlash uchun, loyihangiz nomini kiriting:"
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.back_button(), parse_mode="HTML")
        await state.set_state(cf.sena.create_project_name)
    else:
        if message.text:
            await state.update_data(create_project_description=message.text)
            msg_text = (
                "🖋 Tavsif ro‘yxatga olindi. Endigi qadam — loyiha rasmi\n\n"
                "🖼 <b>Loyiha rasmi</b>\n\n"
                "Iltimos, loyihangizni ifodalaydigan biror rasm yuboring.\n"
                "Bu rasm boshqa foydalanuvchilar uchun vizual tasavvur hosil qilishga yordam beradi.\n\n"
                "📌 Tavsiya:\n"
                "• Haqiqiy fotosurat yoki afisha\n"
                "• Loyiha joyi yoki faoliyatiga oid rasm\n"
                "• Logotip yoki banner ham bo‘lishi mumkin\n\n"
                "❗️Eslatma: faqatgina rasm yuboring, matn emas."
            )
            await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.back_button(), parse_mode="HTML")
            await state.set_state(cf.sena.create_project_photo)
        else:
            await bot.send_message(chat_id=user_id, text="⚠️ Iltimos, faqatgina matn yuboring")


@router.message(cf.sena.create_project_photo)
async def menu_create_project_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "🔙 Orqaga":
        mgs_text = (
            "📄 <b>Loyiha tavsifi</b>\n\n"
            "Endi iltimos, loyihangiz haqida qisqacha va tushunarli tavsif yozing.\n\n"
            "📝 Tavsifda quyidagilar bo‘lishi mumkin:\n"
            "• Loyiha maqsadi\n"
            "• Qanday muammoni hal qiladi\n"
            "• Ko‘ngillilar qanday yordam berishi mumkin\n\n"
            "💡 Masalan:\n"
            "“Mahallamizdagi bolalar uchun ekologik o‘yin maydonchasi quramiz. Ko‘ngillilar dizayn, tozalash va qurilish ishlarida yordam berishadi.”"
        )
        await bot.send_message(chat_id=user_id, text=mgs_text, reply_markup=kb.back_button(), parse_mode="HTML")
        await state.set_state(cf.sena.create_project_description)
    elif message.photo:
        photo_id = message.photo[-1].file_id
        await state.update_data(create_project_photo=photo_id)
        msg_text = (
            "📸 <b>Rasm qabul qilindi!</b>\n\n"
            "🔢 Endi, iltimos, ushbu loyiha muvaffaqiyatli amalga oshishi uchun kerakli ko‘ngillilar sonini kiriting.\n\n"
            "📌 Masalan: <b>10</b>\n"
            "Bu raqam orqali biz boshqa foydalanuvchilarga loyiha hajmini tushunarli qilib taqdim etamiz."
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.back_button(), parse_mode="HTML")
        await state.set_state(cf.sena.create_project_helpers)

    else:
        msg_text = (
            "⚠️ Iltimos, faqatgina rasm yuboring.\n"
            "Rasmni yuborish orqali loyiha vizual tarzda taqdim etiladi."
        )
        await bot.send_message(chat_id=user_id, text=msg_text)


@router.message(cf.sena.create_project_helpers)
async def menu_create_project_helpers(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "🔙 Orqaga":
        msg_text = (
            "🖼 <b>Loyiha rasmi</b>\n\n"
            "Iltimos, loyihangizni ifodalaydigan biror rasm yuboring.\n"
            "Bu rasm boshqa foydalanuvchilar uchun vizual tasavvur hosil qilishga yordam beradi.\n\n"
            "📌 Tavsiya:\n"
            "• Haqiqiy fotosurat yoki afisha\n"
            "• Loyiha joyi yoki faoliyatiga oid rasm\n"
            "• Logotip yoki banner ham bo‘lishi mumkin\n\n"
            "❗️Eslatma: faqatgina rasm yuboring, matn emas."
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.back_button(), parse_mode="HTML")
        await state.set_state(cf.sena.create_project_photo)
    else:
        text = message.text.strip()
        if text.isdigit():
            msg_text = (
                "🤝 Ko‘ngillilar soni saqlandi! Endi loyiha uchun kerakli mablag‘ni belgilaymiz\n\n"
                "💰 <b>Homiylik summasi</b>\n\n"
                "Endi iltimos, ushbu loyiha uchun zarur bo‘lgan mablag‘ miqdorini kiriting (so‘mda).\n\n"
                "📌 Masalan: <b>1000000</b>\n"
                "Bu summa orqali loyiha xarajatlarini qoplay olish imkoningiz bo‘ladi.\n\n"
                "❗️Faqat raqam ko‘rinishida yuboring, so‘msiz."
            )
            await state.update_data(create_project_helpers=message.text)
            await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.back_button(), parse_mode="HTML")
            await state.set_state(cf.sena.create_project_donaters)
        else:
            await bot.send_message(chat_id=user_id, text="⚠️ Iltimos, faqatgina matn yuboring")


@router.message(cf.sena.create_project_donaters)
async def menu_create_project_donate(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    if message.text == "🔙 Orqaga":
        msg_text = (
            "🔢 Endi, iltimos, ushbu loyiha muvaffaqiyatli amalga oshishi uchun kerakli ko‘ngillilar sonini kiriting.\n\n"
            "📌 Masalan: <b>10</b>\n"
            "Bu raqam orqali biz boshqa foydalanuvchilarga loyiha hajmini tushunarli qilib taqdim etamiz."
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.back_button(), parse_mode="HTML")
        await state.set_state(cf.sena.create_project_helpers)
    else:
        text = message.text.strip()
        if text.isdigit():
            await state.update_data(create_project_donaters=int(message.text))
            await bot.send_message(chat_id=user_id, text="📦 Budjet belgilandi! Endi loyiha ma’lumotlarini ko‘rib chiqamiz", reply_markup=types.ReplyKeyboardRemove())
            msg_text = (
                "🆕 <b>Yangi loyiha ma'lumotlari</b>\n\n"
                f"📌 <b>Loyiha nomi:</b> {data['create_project_name']}\n\n"
                f"📝 <b>Tavsifi:</b>\n{data['create_project_description']}\n\n"
                f"🤝 <b>Kerakli ko‘ngillilar soni:</b> {data['create_project_helpers']} ta\n"
                f"💰 <b>Kerakli mablag‘ miqdori:</b> {message.text} so‘m\n\n"
                "Iltimos, quyidagi tugmalar orqali ushbu loyihani tasdiqlang yoki bekor qiling:"
            )
            await bot.send_photo(chat_id=user_id, photo=data['create_project_photo'], caption=msg_text, reply_markup=kb.create_project_keyboard(), parse_mode="HTML")
            await state.set_state(cf.sena.create_project_final)
        else:
            await bot.send_message(chat_id=user_id, text="⚠️ Iltimos, faqatgina matn yuboring")


@router.callback_query(cf.sena.create_project_final)
async def menu_create_project(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    id_user = data.get('id_user') or db.get_user_by_telegram_id(telegram_id=user_id).id 
    msg_text = (
        "🗂 <b>Shaxsiy loyihalaringiz bo‘limi</b>\n\n"
        "Bu yerda siz yaratgan loyihalarni:\n"
        "✏️ Tahrirlash\n"
        "📊 Natijalarini ko‘rish\n"
        "🔄 Faolligini kuzatish imkoniyatiga egasiz.\n\n"
        "💡 Sizning tashabbuslaringiz jamiyat uchun katta o‘zgarishlar yasashi mumkin 🌍"
    )
    if callback.data == "Tasdiqlash":
        db.generate_user_project(user_id=id_user,
                            name=data['create_project_name'],
                            description=data['create_project_description'],
                            photo_id=data['create_project_photo'],
                            total_quantity=data['create_project_helpers'],
                            total_amount=data['create_project_donaters'])
        admin_msg = (
            "📥 <b>Yangi loyiha yuborildi!</b>\n\n"
            "Iltimos, uni tekshirib chiqing va tasdiqlang yoki rad eting.\n\n"
            "🔎 Admin panel orqali loyihani ko‘rishingiz mumkin."
        )
        for admin_id in cf.admins:
            await bot.send_message(chat_id=admin_id, text=admin_msg, parse_mode="HTML")
        await bot.answer_callback_query(callback_query_id=callback.id, text="✅ Loyiha muvaffaqiyatli qabul qilindi!\n\n🕵️ Adminlar tomonidan ko‘rib chiqilishi kutilmoqda.\n⏳ Iltimos, biroz kuting — tez orada siz bilan bog‘lanamiz.", show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=None)
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_projects_menu(), parse_mode="HTML")
        await state.set_state(cf.sena.my_projetcs)
    elif callback.data == "Bekor qilish":
        await bot.answer_callback_query(callback_query_id=callback.id, text="❌ Ushbu loyiha bekor qilindi.\n💡 Har bir yakun — yangi boshlanish uchun imkoniyat!", show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=None)
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_projects_menu(), parse_mode="HTML")
        await state.set_state(cf.sena.my_projetcs)
    else:
        await bot.answer_callback_query(callback_query_id=callback.id, text="⚠️ Noma'lum buyruq", show_alert=False)
################################################################################################

################################################################################################
@router.message(cf.sena.user_projects)
async def menu_user_projects(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    id_user = int(data.get('id_user') or db.get_user_by_telegram_id(telegram_id=user_id).id)
    projects = db.get_user_projects(user_id=id_user)
    if message.text == "🔙 Orqaga":
        msg_text = (
            "🗂 <b>Shaxsiy loyihalaringiz bo‘limi</b>\n\n"
            "Bu yerda siz yaratgan loyihalarni:\n"
            "✏️ Tahrirlash\n"
            "📊 Natijalarini ko‘rish\n"
            "🔄 Faolligini kuzatish imkoniyatiga egasiz.\n\n"
            "💡 Sizning tashabbuslaringiz jamiyat uchun katta o‘zgarishlar yasashi mumkin 🌍"
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_projects_menu(), parse_mode="HTML")
        await state.set_state(cf.sena.my_projetcs)
    if not projects:
        msg_text = (
            "❌ <b>Sizda hali hech qanday loyiha mavjud emas</b>.\n\n"
            "📌 Loyihangiz g‘oyasi bo‘lsa, uni yaratish orqali uni boshqalarga taqdim eting va ko‘ngillilarni jalb qiling!\n\n"
            "🆕 Yangi loyiha yaratish uchun <b>“🆕 Yangi loyiha yaratish”</b> tugmasini bosing."
        )
        if message.text == "❌ Loyihalaringiz topilmadi":
            await bot.send_message(chat_id=user_id, text=msg_text, parse_mode="HTML")
    else:
        project_names = [
            p.name[:30] + "…" if len(p.name) > 30 else p.name for p in projects
        ]
        if message.text not in project_names:
            msg_text = (
                "ℹ️ Tanlangan loyiha topilmadi.\n\n"
                "Iltimos, ro‘yxatdan mavjud loyihalardan birini tanlang yoki '🔙 Orqaga' tugmasini bosing."
            )
            return await bot.send_message(chat_id=user_id, text=msg_text)
        for project in projects:
            if message.text == project.name:
                msg_text = (
                    f"📄 <b>Loyiha tafsilotlari</b>\n\n"
                    f"<b>Nomi:</b> {project.name}\n"
                    f"<b>Holati:</b> {project.status.title()}\n"
                    f"<b>Ko‘ngillilar:</b> {project.helper_quantity} / {project.total_quantity} ta\n"
                    f"<b>Yig‘ilgan mablag‘:</b> {project.cash_amount:_} / {project.total_amount:_} so‘m\n\n"
                    f"<b>Tavsif:</b>\n{project.description}"
                )
                await bot.send_message(chat_id=user_id, text="🚀", reply_markup=types.ReplyKeyboardRemove())
                await bot.send_photo(chat_id=user_id, photo=project.photo_id, caption=msg_text, reply_markup=kb.show_project(status=project.status), parse_mode="HTML")
                await state.update_data(show_project=project.id)
                await state.set_state(cf.sena.show_project)
                break


@router.callback_query(cf.sena.show_project)
async def menu_show_project(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    project = db.get_project_by_id(project_id=int(data['show_project']))
    if callback.data == "edit_project":
        msg_text = (
            "✏️ <b>Loyihani tahrirlash</b>\n\n"
            "Siz hozirda loyihangizni ma’lumotlarini o‘zgartirish jarayonidasiz.\n"
            "Iltimos, tahrirlamoqchi bo‘lgan bo‘limni tanlang yoki '🔙 Orqaga' tugmasini bosing."
        )
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_project_edit(), parse_mode="HTML")
        await state.set_state(cf.sena.my_project_edit)
    elif callback.data == "delete_project":
        id_user = int(data.get('id_user') or db.get_user_by_telegram_id(telegram_id=user_id).id)
        msg_text = (
            "❌ <b>Loyiha muvaffaqiyatli o‘chirildi</b>\n\n"
            "Agar bu xatolik bilan amalga oshirilgan bo‘lsa, admin bilan bog‘laning.\n"
            "Siz boshqa loyihalarni yaratishingiz yoki mavjudlarini ko‘rishingiz mumkin."
        )
        db.delete_user_project(project_id=data['show_project'], user_id=id_user)
        await bot.answer_callback_query(callback_query_id=callback.id, text="🗑 Loyiha o‘chirildi", show_alert=False)
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.list_of_projects_menu(telegram_id=user_id), parse_mode="HTML")
        await state.set_state(cf.sena.user_projects)
    elif callback.data == "project_helpers":
        msg_text = (
            "\n\n🤝 <b>Loyihadagi ko‘ngillilar</b>\n\n"
            "Bu yerda ushbu loyihada ishtirok etayotgan ko‘ngillilar ro‘yxatini ko‘rishingiz mumkin.\n"
            "📌 Ular sizning tashabbusingizga hissa qo‘shayotgan insonlardir."
        )
        helpers = project.helpers
        if helpers:
            msg_text += (
                "🤝 <b>Loyihadagi ko‘ngillilar</b>\n\n" +
                "\n".join([
                    f"• <a href='tg://user?id={h.user.telegram_id}'>{h.user.name or '👤 Nomaʼlum foydalanuvchi'}</a>" 
                    for h in helpers
                ])
            )
        else:
            msg_text += "\n\nℹ️ Ushbu loyihada hali ko‘ngillilar mavjud emas"
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_project_helpers_menu(), parse_mode="HTML")
        await state.set_state(cf.sena.my_project_helpers)
    elif callback.data == "project_donaters":
        msg_text = (
            "💰 <b>Loyihaga hissa qo‘shganlar</b>\n\n"
            "Quyidagi ro‘yxatda homiylar ko‘rsatilgan. Ular tomonidan qoldirilgan mablag‘ loyihangizni amalga oshirishga xizmat qilmoqda.\n\n"
            "🙏 Ularga rahmat!"
        )
        donaters = project.donaters
        if donaters:
            msg_text += (
                "\n\n💰 <b>Loyihaga homiylik qilganlar</b>\n\n" +
                "\n".join([
                    f"• <a href='tg://user?id={d.user.telegram_id}'>{d.user.name or '👤 Nomaʼlum foydalanuvchi'}</a> — {d.amount:_} so‘m"
                    for d in donaters
                ])
            )
        else:
            msg_text += "\n\nℹ️ Ushbu loyihaga hali hech kim hissa qo‘shmagan"
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_project_donaters(project_id=int(data['show_project'])), parse_mode="HTML")
        await state.set_state(cf.sena.my_project_donaters)
    else:
        await bot.answer_callback_query(callback_query_id=callback.id, text="⚠️ Noma'lum buyruq", show_alert=False)


@router.callback_query(cf.sena.my_project_edit)
async def menu_my_project_edit(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    project = db.get_project_by_id(project_id=int(data['show_project']))
    if callback.data == "back":
        msg_text = (
            f"📄 <b>Loyiha tafsilotlari</b>\n\n"
            f"<b>Nomi:</b> {project.name}\n"
            f"<b>Holati:</b> {project.status.title()}\n"
            f"<b>Ko‘ngillilar:</b> {project.helper_quantity} / {project.total_quantity} ta\n"
            f"<b>Yig‘ilgan mablag‘:</b> {project.cash_amount:_} / {project.total_amount:_} so‘m\n\n"
            f"<b>Tavsif:</b>\n{project.description}"
        )
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_photo(chat_id=user_id, photo=project.photo_id, caption=msg_text, reply_markup=kb.show_project(status=project.status), parse_mode="HTML")
        await state.set_state(cf.sena.show_project)
    elif callback.data == "edit_name":
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=user_id, text="✏️ Yangi loyiha nomini kiriting:", reply_markup=kb.back_button())
        await state.set_state(cf.sena.my_project_edit_name)
    elif callback.data == "edit_description":
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=user_id, text="📄 Yangi tavsif matnini kiriting:", reply_markup=kb.back_button())
        await state.set_state(cf.sena.my_project_edit_description)
    elif callback.data == "edit_photo":
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=user_id, text="🖼 Yangi rasmni yuboring:", reply_markup=kb.back_button())
        await state.set_state(cf.sena.my_project_edit_photo)
    elif callback.data == "edit_helpers_quantity":
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=user_id, text="👥 Maksimal ko‘ngillilar sonini kiriting (faqat raqam):", reply_markup=kb.back_button())
        await state.set_state(cf.sena.my_project_edit_quantity)
    elif callback.data == "edit_total_amount":
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=user_id, text="💰 Loyiha uchun kerakli umumiy mablag‘ni kiriting (so‘mda):", reply_markup=kb.back_button())
        await state.set_state(cf.sena.my_project_edit_amount)
    else:
        await bot.answer_callback_query(callback_query_id=callback.id, text="⚠️ Noma'lum buyruq", show_alert=False)


@router.message(cf.sena.my_project_edit_name)
async def my_project_edit_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    project = db.get_project_by_id(project_id=data['show_project'])
    msg_text = (
        "✏️ <b>Loyihani tahrirlash</b>\n\n"
        "Siz hozirda loyihangizni ma’lumotlarini o‘zgartirish jarayonidasiz.\n"
        "Iltimos, tahrirlamoqchi bo‘lgan bo‘limni tanlang yoki '🔙 Orqaga' tugmasini bosing."
    )
    if message.text == "🔙 Orqaga":
        msg_text += "\n\n↩️ Tahrirlash bekor qilindi."
        await bot.send_message(chat_id=user_id, text="✏️", reply_markup=types.ReplyKeyboardRemove())
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_project_edit(), parse_mode="HTML")
        await state.set_state(cf.sena.my_project_edit)
        return
    db.update_project_field(project_id=project.id, field="name", value=message.text)
    await bot.send_message(chat_id=user_id, text=f"✅ Loyiha nomi yangilandi:\n<b>{message.text}</b>", reply_markup=types.ReplyKeyboardRemove())
    await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_project_edit(), parse_mode="HTML")
    await state.set_state(cf.sena.my_project_edit)


@router.message(cf.sena.my_project_edit_description)
async def my_project_edit_description(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    project = db.get_project_by_id(project_id=data['show_project'])
    msg_text = (
        "✏️ <b>Loyihani tahrirlash</b>\n\n"
        "Siz hozirda loyihangizni ma’lumotlarini o‘zgartirish jarayonidasiz.\n"
        "Iltimos, tahrirlamoqchi bo‘lgan bo‘limni tanlang yoki '🔙 Orqaga' tugmasini bosing."
    )
    if message.text == "🔙 Orqaga":
        msg_text += "\n\n↩️ Tahrirlash bekor qilindi."
        await bot.send_message(chat_id=user_id, text="✏️", reply_markup=types.ReplyKeyboardRemove())
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_project_edit(), parse_mode="HTML")
        await state.set_state(cf.sena.my_project_edit)
        return
    
    db.update_project_field(project_id=project.id, field="description", value=message.text)
    await bot.send_message(chat_id=user_id, text="✅ Tavsif yangilandi.", reply_markup=types.ReplyKeyboardRemove())
    await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_project_edit())
    await state.set_state(cf.sena.my_project_edit)


@router.message(cf.sena.my_project_edit_photo)
async def my_project_edit_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    project = db.get_project_by_id(project_id=data['show_project'])
    msg_text = (
            "✏️ <b>Loyihani tahrirlash</b>\n\n"
            "Siz hozirda loyihangizni ma’lumotlarini o‘zgartirish jarayonidasiz.\n"
            "Iltimos, tahrirlamoqchi bo‘lgan bo‘limni tanlang yoki '🔙 Orqaga' tugmasini bosing."
        )
    if message.text == "🔙 Orqaga":
        msg_text += "\n\n↩️ Rasmni yangilash bekor qilindi."
        await bot.send_message(chat_id=user_id, text="✏️", reply_markup=types.ReplyKeyboardRemove())
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_project_edit(), parse_mode="HTML")
        await state.set_state(cf.sena.my_project_edit)
        return
    
    if not message.photo:
        await bot.send_message(chat_id=user_id, text="❗ Iltimos, rasm yuboring.")
        return
    
    file_id = message.photo[-1].file_id
    db.update_project_field(project_id=project.id, field="photo", value=file_id)
    await bot.send_message(chat_id=user_id, text="✅ Rasm muvaffaqiyatli yangilandi.", reply_markup=types.ReplyKeyboardRemove())
    await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_project_edit())
    await state.set_state(cf.sena.my_project_edit)


@router.message(cf.sena.my_project_edit_quantity)
async def my_project_edit_quantity(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    project = db.get_project_by_id(project_id=data['show_project'])
    msg_text = (
        "✏️ <b>Loyihani tahrirlash</b>\n\n"
        "Siz hozirda loyihangizni ma’lumotlarini o‘zgartirish jarayonidasiz.\n"
        "Iltimos, tahrirlamoqchi bo‘lgan bo‘limni tanlang yoki '🔙 Orqaga' tugmasini bosing."
    )
    if message.text == "🔙 Orqaga":
        msg_text += "\n\n↩️ Rasmni yangilash bekor qilindi."
        await bot.send_message(chat_id=user_id, text="✏️", reply_markup=types.ReplyKeyboardRemove())
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_project_edit(), parse_mode="HTML")
        await state.set_state(cf.sena.my_project_edit)
        return

    if not message.text.isdigit():
        await bot.send_message(chat_id=user_id, text="❗ Iltimos, raqam kiriting.")
        return

    db.update_project_field(project_id=project.id, field="total_quantity", value=int(message.text))
    await bot.send_message(chat_id=user_id, text="✅ Ko‘ngillilar soni yangilandi.", reply_markup=types.ReplyKeyboardRemove())
    await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_project_edit())
    await state.set_state(cf.sena.my_project_edit)


@router.message(cf.sena.my_project_edit_amount)
async def my_project_edit_amount(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    project = db.get_project_by_id(project_id=data['show_project'])
    msg_text = (
        "✏️ <b>Loyihani tahrirlash</b>\n\n"
        "Siz hozirda loyihangizni ma’lumotlarini o‘zgartirish jarayonidasiz.\n"
        "Iltimos, tahrirlamoqchi bo‘lgan bo‘limni tanlang yoki '🔙 Orqaga' tugmasini bosing."
    )
    if message.text == "🔙 Orqaga":
        msg_text += "\n\n↩️ Amal bekor qilindi."
        await bot.send_message(chat_id=user_id, text="✏️", reply_markup=types.ReplyKeyboardRemove())
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_project_edit(), parse_mode="HTML")
        await state.set_state(cf.sena.my_project_edit)
        return

    if not message.text.isdigit():
        await bot.send_message(chat_id=user_id, text="❗ Iltimos, mablag‘ni raqam bilan kiriting.")
        return

    db.update_project_field(project_id=project.id, field="total_amount", value=int(message.text))
    await bot.send_message(chat_id=user_id, text="✅ Umumiy mablag‘ yangilandi.", reply_markup=types.ReplyKeyboardRemove())
    await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_project_edit())
    await state.set_state(cf.sena.my_project_edit)
################################################################################################

################################################################################################
@router.callback_query(cf.sena.my_project_helpers)
async def menu_my_project_helpers(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    project = db.get_project_by_id(project_id=int(data['show_project']))
    if callback.data == "back":
        msg_text = (
            f"📄 <b>Loyiha tafsilotlari</b>\n\n"
            f"<b>Nomi:</b> {project.name}\n"
            f"<b>Holati:</b> {project.status.title()}\n"
            f"<b>Ko‘ngillilar:</b> {project.helper_quantity} / {project.total_quantity} ta\n"
            f"<b>Yig‘ilgan mablag‘:</b> {project.cash_amount:_} / {project.total_amount:_} so‘m\n\n"
            f"<b>Tavsif:</b>\n{project.description}"
        )
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_photo(chat_id=user_id, photo=project.photo_id, caption=msg_text, reply_markup=kb.show_project(status=project.status), parse_mode="HTML")
        await state.set_state(cf.sena.show_project)
    elif callback.data == "delet_helper":
        msg_text = (
            "🗑 <b>Ko‘ngillini o‘chirish</b>\n\n"
            "Quyida loyihangizda ishtirok etayotgan ko‘ngillilar ro‘yxati keltirilgan.\n"
            "Ro‘yxatdan chiqarishni istagan ko‘ngillini tanlang.\n\n"
            "⚠️ Diqqat! Bu amalni bekor qilib bo‘lmaydi."
        )
        await callback.message.edit_text(text=msg_text, reply_markup=kb.my_project_helpers(project_id=data['show_project']), parse_mode="HTML")
        await state.set_state(cf.sena.delet_helpers)
    else:
        await bot.answer_callback_query(callback_query_id=callback.id, text="⚠️ Noma'lum buyruq", show_alert=False)


@router.callback_query(cf.sena.delet_helpers)
async def menu_delet_helpers(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    project_id = int(data['show_project'])
    project = db.get_project_by_id(project_id=project_id)
    helpers = project.helpers
    if callback.data == "back":
        msg_text = (
            "🤝 <b>Loyihadagi ko‘ngillilar</b>\n\n" +
            "\n".join([
                f"• <a href='tg://user?id={h.user.telegram_id}'>{h.user.name or '👤 Nomaʼlum foydalanuvchi'}</a>"
                for h in helpers
            ]) if helpers else "ℹ️ Ushbu loyihada hali ko‘ngillilar mavjud emas"
        )
        await bot.edit_message_text(chat_id=user_id, message_id=callback.message.message_id, text=msg_text, parse_mode="HTML", reply_markup=kb.my_project_helpers_menu())
        await state.set_state(cf.sena.my_project_helpers)
        return

    for helper in helpers:
        if callback.data == f"helper_{helper.user.telegram_id}":
            db.delete_helper_in_project(user_id=helper.user.telegram_id, project_id=project_id)
            await bot.answer_callback_query(
                callback_query_id=callback.id,
                text="✅ Ko‘ngilli o‘chirildi",
                show_alert=True
            )
            break

    project = db.get_project_by_id(project_id=project_id)
    helpers = project.helpers
    msg_text = (
        "🤝 <b>Loyihadagi ko‘ngillilar</b>\n\n" +
        "\n".join([
            f"• <a href='tg://user?id={h.user.telegram_id}'>{h.user.name or '👤 Nomaʼlum foydalanuvchi'}</a>"
            for h in helpers
        ]) if helpers else "ℹ️ Ushbu loyihada hali ko‘ngillilar mavjud emas"
    )
    await callback.message.edit_text(text=msg_text, parse_mode="HTML", reply_markup=kb.my_project_helpers_menu(project_id=project_id))
    await state.set_state(cf.sena.my_project_helpers)
################################################################################################

################################################################################################
@router.callback_query(cf.sena.my_project_donaters)
async def menu_my_project_donaters(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    project = db.get_project_by_id(project_id=int(data['show_project']))
    if callback.data == "back":
        msg_text = (
            f"📄 <b>Loyiha tafsilotlari</b>\n\n"
            f"<b>Nomi:</b> {project.name}\n"
            f"<b>Holati:</b> {project.status.title()}\n"
            f"<b>Ko‘ngillilar:</b> {project.helper_quantity} / {project.total_quantity} ta\n"
            f"<b>Yig‘ilgan mablag‘:</b> {project.cash_amount:_} / {project.total_amount:_} so‘m\n\n"
            f"<b>Tavsif:</b>\n{project.description}"
        )
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_photo(chat_id=user_id, photo=project.photo_id, caption=msg_text, reply_markup=kb.show_project(status=project.status), parse_mode="HTML")
        await state.set_state(cf.sena.show_project)
    else:
        await bot.answer_callback_query(callback_query_id=callback.id, text="⚠️ Noma'lum buyruq", show_alert=False)
################################################################################################

################################################################################################
@router.message(lambda msg: msg.text == "🤝 Ko‘ngillilik faoliyatim")
async def my_helped_projects(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    id_user = int(data.get('id_user') or db.get_user_by_telegram_id(telegram_id=user_id).id)
    my_helper_projects = db.get_helper_projects(user_id=id_user)
    if not my_helper_projects:
        msg_text = "ℹ️ Siz hali hech qaysi loyihada ko‘ngilli sifatida ishtirok etmagansiz."
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.main_menu())
        return
    msg_text = (
        "🤝 <b>Siz ishtirok etayotgan loyihalar</b>\n\n" +
        "\n\n".join([
            f"<b>{p.name}</b>\n"
            f"📌 Holati: {p.status.title()}\n"
            f"📄 Tavsif: {p.description[:100]}…" if len(p.description) > 100 else f"📄 Tavsif: {p.description}"
            for p in my_helper_projects
        ])
    )
    await bot.send_message(chat_id=user_id, text=msg_text, parse_mode="HTML", reply_markup=kb.helped_projects_keyboard(my_helper_projects))
    await state.set_state(cf.sena.my_helped_projects)


@router.message(cf.sena.my_helped_projects)
async def menu_my_helped_projects(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    id_user = int(data.get('id_user') or db.get_user_by_telegram_id(telegram_id=user_id).id)
    my_helper_projects = db.get_helper_projects(user_id=id_user)
    if message.text == "🔙 Orqaga":
        await bot.send_photo(chat_id=user_id, photo=cf.start_photo, caption=cf.start_msg, reply_markup=kb.main_menu())
        await state.clear()
        return
    if my_helper_projects:
        for project in my_helper_projects:
            if message.text == project.name:
                await state.update_data(helper_project_id=project.id)
                msg_text = (
                    f"📄 <b>Loyiha tafsilotlari</b>\n\n"
                    f"<b>Nomi:</b> {project.name}\n"
                    f"<b>Holati:</b> {project.status.title()}\n"
                    f"<b>Ko‘ngillilar:</b> {project.helper_quantity} / {project.total_quantity} ta\n"
                    f"<b>Yig‘ilgan mablag‘:</b> {project.cash_amount:_} / {project.total_amount:_} so‘m\n\n"
                    f"<b>Tavsif:</b>\n{project.description}"
                )
                await bot.send_message(chat_id=user_id, text="🚀", reply_markup=types.ReplyKeyboardRemove())
                await bot.send_photo(chat_id=user_id, photo=project.photo_id, caption=msg_text, parse_mode="HTML", reply_markup=kb.helper_cancel())
                await state.set_state(cf.sena.cancel_helper_project)
                return
        await bot.send_message(chat_id=user_id, text="❗️ Bunday loyiha topilmadi. Iltimos, tugmalardan foydalaning.", reply_markup=kb.helped_projects_keyboard(my_helper_projects))
    else:
        await bot.send_message(chat_id=user_id, text="ℹ️ Siz hali hech qanday loyihada ko‘ngilli sifatida ishtirok etmagansiz.", reply_markup=kb.main_menu())
        await state.clear()


@router.callback_query(cf.sena.cancel_helper_project)
async def menu_cancel_helper_project(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    project_id = data.get('helper_project_id')
    id_user = int(data.get('id_user') or db.get_user_by_telegram_id(telegram_id=user_id).id)
    my_helper_projects = db.get_helper_projects(user_id=id_user)
    if not my_helper_projects:
        await bot.answer_callback_query(callback_query_id=callback.id, text="ℹ️ Siz hech bir loyihada ko‘ngilli emassiz.", show_alert=True)
        return await state.clear()
    if callback.data == "back":
        msg_text = (
            "🤝 <b>Siz ishtirok etayotgan loyihalar</b>\n\n" +
            "\n\n".join([
                f"<b>{p.name}</b>\n"
                f"📌 Holati: {p.status.title()}\n"
                f"📄 Tavsif: {p.description[:100]}…" if len(p.description) > 100 else f"📄 Tavsif: {p.description}"
                for p in my_helper_projects
            ])
        )
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.helped_projects_keyboard(db.get_helper_projects(user_id=id_user)), parse_mode='HTML')
        await state.set_state(cf.sena.my_helped_projects)
    elif callback.data == "cancel_helper":
        db.delete_helper_in_project(user_id=id_user, project_id=project_id)
        await bot.answer_callback_query(callback_query_id=callback.id, text="✅ Siz ushbu loyihadan chiqarildingiz.", show_alert=True)
        msg_text = (
            "❌ Siz endi bu loyihaning ko‘ngillisi emassiz.\n\n"
            "Agar bu xatolik bilan amalga oshirilgan bo‘lsa, qayta ro‘yxatdan o‘tishingiz mumkin."
        )
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.helped_projects_keyboard(db.get_helper_projects(user_id=id_user)), parse_mode='HTML')
        await state.set_state(cf.sena.my_helped_projects)
    else:
        await bot.answer_callback_query(callback_query_id=callback.id, text="⚠️ Noma'lum buyruq", show_alert=False)
################################################################################################

################################################################################################
@router.message(lambda msg: msg.text == "📝 Mening bloglarim")
async def my_blogs(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    id_user = int(data.get('id_user') or db.get_user_by_telegram_id(telegram_id=user_id).id)
    blogs = db.get_user_blogs(user_id=id_user)
    msg_text = "📝 <b>Siz yozgan bloglar</b>\n\n"
    if not blogs:
        msg_text += "📭 Siz hali birorta blog yaratmagansiz.\n\n✍️ Yangi blog yaratish uchun '➕ Yangi blog qo‘shish' tugmasini bosing."
    else:
        for b in blogs:
            description = b.content[:100] + "…" if len(b.content) > 100 else b.content
            msg_text += (
                f"<b>📌 {b.title}</b>\n"
                f"{description}\n\n"
            )
    await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_blogs_menu(blogs), parse_mode='HTML')
    await state.set_state(cf.sena.my_blogs)


@router.message(cf.sena.my_blogs)
async def menu_my_blogs(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    id_user = int(data.get('id_user') or db.get_user_by_telegram_id(telegram_id=user_id).id)
    user_blogs = db.get_user_blogs(user_id=id_user)

    if message.text == "🔙 Orqaga":
        await bot.send_photo(chat_id=user_id, photo=cf.start_photo, caption=cf.start_msg, reply_markup=kb.main_menu(), parse_mode='HTML')
        await state.clear()
        return

    if message.text == "➕ Yangi blog qo‘shish":
        await bot.send_message(chat_id=user_id, text="📌 Yangi blog nomini kiriting:", reply_markup=kb.back_button())
        await state.set_state(cf.sena.create_blog_name)
        return

    for blog in user_blogs:
        if message.text == blog.title:
            await state.update_data(selected_blog_id=blog.id)
            msg_text = (
                f"📝 <b>{blog.title}</b>\n\n"
                f"{blog.content}\n\n"
                f"<i>Blog moderatsiya: {'✅ Tasdiqlangan' if blog.is_verified else '⏳ Ko‘rib chiqilmoqda'}</i>"
            )
            await bot.send_message(chat_id=user_id, text="🚀", reply_markup=types.ReplyKeyboardRemove())
            await bot.send_photo(chat_id=user_id, photo=blog.photo_id, caption=msg_text, reply_markup=kb.my_blog_manage(), parse_mode='HTML')
            await state.set_state(cf.sena.manage_blog)
            return

    await bot.send_message(chat_id=user_id, text="❗️Blog topilmadi. Iltimos, mavjud blogni tanlang yoki yangisini yarating")
################################################################################################

################################################################################################
@router.callback_query(cf.sena.manage_blog)
async def menu_manage_blog(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    id_user = int(data.get('id_user') or db.get_user_by_telegram_id(telegram_id=user_id).id)
    blogs = db.get_user_blogs(user_id=id_user)
    if callback.data == "back":
        msg_text = "📝 <b>Siz yozgan bloglar</b>\n\n"
        if not blogs:
            msg_text += "📭 Siz hali birorta blog yaratmagansiz.\n\n✍️ Yangi blog yaratish uchun '➕ Yangi blog qo‘shish' tugmasini bosing."
        else:
            for b in blogs:
                description = b.content[:100] + "…" if len(b.content) > 100 else b.content
                msg_text += (
                    f"<b>📌 {b.title}</b>\n"
                    f"{description}\n\n"
                )
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_blogs_menu(blogs=blogs), parse_mode="HTML")
        return await state.set_state(cf.sena.my_blogs)
    elif callback.data == "edit_blog_title":
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=user_id, text="✏️ Yangi blog nomini kiriting:", reply_markup=kb.back_button())
        await state.set_state(cf.sena.edit_blog_title)
    elif callback.data == "edit_blog_content":
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=user_id, text="📝 Yangi tavsifni yuboring:", reply_markup=kb.back_button())
        await state.set_state(cf.sena.edit_blog_content)
    elif callback.data == "edit_blog_photo":
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=user_id, text="📷 Yangi suratni yuboring:", reply_markup=kb.back_button())
        await state.set_state(cf.sena.edit_blog_photo)
    elif callback.data == "delete_blog":
        db.delete_blog(blog_id=data["selected_blog_id"])
        id_user = int(data.get('id_user') or db.get_user_by_telegram_id(telegram_id=user_id).id)
        blogs = db.get_user_blogs(user_id=id_user)
        msg_text = "📝 <b>Siz yozgan bloglar</b>\n\n"
        if not blogs:
            msg_text += "📭 Siz hali birorta blog yaratmagansiz.\n\n✍️ Yangi blog yaratish uchun '➕ Yangi blog qo‘shish' tugmasini bosing."
        else:
            for b in blogs:
                description = b.content[:100] + "…" if len(b.content) > 100 else b.content
                msg_text += (
                    f"<b>📌 {b.title}</b>\n"
                    f"{description}\n\n"
                )
        await bot.answer_callback_query(callback_query_id=callback.id, text="🗑 Blog o‘chirildi.", show_alert=False)
        await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_blogs_menu(blogs=blogs), parse_mode="HTML")
        await state.set_state(cf.sena.my_blogs)
    else:
        await bot.answer_callback_query(callback_query_id=callback.id, text="⚠️ Noma'lum buyruq", show_alert=False)

def format_blog_caption(blog):
    return (
        f"📝 <b>{blog.title}</b>\n\n"
        f"{blog.content}\n\n"
        f"<i>Blog moderatsiya: {'✅ Tasdiqlangan' if blog.is_verified else '⏳ Ko‘rib chiqilmoqda'}</i>"
    )

async def return_to_manage_menu(user_id, blog, state):
    await bot.send_message(chat_id=user_id, text="⬅️ Tahrirlash menyusiga qaytdingiz", reply_markup=types.ReplyKeyboardRemove())
    await bot.send_photo(chat_id=user_id, photo=blog.photo_id, caption=format_blog_caption(blog), parse_mode="HTML", reply_markup=kb.my_blog_manage())
    await state.set_state(cf.sena.manage_blog)


@router.message(cf.sena.edit_blog_title)
async def save_blog_title(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()

    if message.text == "🔙 Orqaga":
        blog = db.get_blog_by_id(data['selected_blog_id'])
        return await return_to_manage_menu(user_id, blog, state)

    db.update_blog_field(blog_id=data["selected_blog_id"], field="title", value=message.text)
    blog = db.get_blog_by_id(data["selected_blog_id"])
    await bot.send_message(chat_id=user_id, text="✅ Blog nomi yangilandi!", reply_markup=types.ReplyKeyboardRemove())
    await bot.send_photo(chat_id=user_id, photo=blog.photo_id, caption=format_blog_caption(blog), reply_markup=kb.my_blog_manage(), parse_mode="HTML")
    await state.set_state(cf.sena.manage_blog)


@router.message(cf.sena.edit_blog_content)
async def save_blog_content(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()

    if message.text == "🔙 Orqaga":
        blog = db.get_blog_by_id(data["selected_blog_id"])
        return await return_to_manage_menu(user_id, blog, state)

    db.update_blog_field(blog_id=data["selected_blog_id"], field="content", value=message.text)
    blog = db.get_blog_by_id(data["selected_blog_id"])
    await bot.send_message(chat_id=user_id, text="✅ Tavsif yangilandi!", reply_markup=types.ReplyKeyboardRemove())
    await bot.send_photo(chat_id=user_id, photo=blog.photo_id, caption=format_blog_caption(blog), reply_markup=kb.my_blog_manage(), parse_mode="HTML")
    await state.set_state(cf.sena.manage_blog)


@router.message(or_f(F.photo, F.text == "🔙 Orqaga"), cf.sena.edit_blog_photo)
async def save_blog_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()

    if message.text == "🔙 Orqaga":
        blog = db.get_blog_by_id(data["selected_blog_id"])
        return await return_to_manage_menu(user_id, blog, state)

    file_id = message.photo[-1].file_id
    db.update_blog_field(blog_id=data["selected_blog_id"], field="photo_id", value=file_id)
    blog = db.get_blog_by_id(data["selected_blog_id"])

    await bot.send_message(chat_id=user_id, text="✅ Rasm yangilandi!", reply_markup=types.ReplyKeyboardRemove())
    await bot.send_photo(chat_id=user_id, photo=file_id, caption=format_blog_caption(blog), reply_markup=kb.my_blog_manage(), parse_mode="HTML")
    await state.set_state(cf.sena.manage_blog)
################################################################################################

################################################################################################
@router.message(cf.sena.create_blog_name)
async def blog_get_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    id_user = int(data.get('id_user') or db.get_user_by_telegram_id(telegram_id=user_id).id)
    blogs = db.get_user_blogs(user_id=id_user)
    msg_text = "📝 <b>Siz yozgan bloglar</b>\n\n"
    if not blogs:
        msg_text += "📭 Siz hali birorta blog yaratmagansiz.\n\n✍️ Yangi blog yaratish uchun '➕ Yangi blog qo‘shish' tugmasini bosing."
    else:
        for b in blogs:
            description = b.content[:100] + "…" if len(b.content) > 100 else b.content
            msg_text += (
                f"<b>📌 {b.title}</b>\n"
                f"{description}\n\n"
            )
    if message.text == "🔙 Orqaga":
        msg_text += "\n🔙 Asosiy blog menyusiga qaytdingiz."
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.my_blogs_menu(blogs=blogs), parse_mode="HTML")
        return await state.set_state(cf.sena.my_blogs)

    await state.update_data(new_blog_name=message.text)
    await bot.send_message(chat_id=user_id,
        text="✏️ <b>Endi blog tavsifini kiriting:</b>\n\nIltimos, blog mazmunini qisqacha tushuntirib bering.",
        reply_markup=kb.back_button(), parse_mode='HTML')
    await state.set_state(cf.sena.create_blog_description)


@router.message(cf.sena.create_blog_description)
async def blog_get_description(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "🔙 Orqaga":
        msg_text = "✏️ Blog nomini qaytadan kiriting:"
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.back_button())
        return await state.set_state(cf.sena.create_blog_name)

    await state.update_data(new_blog_description=message.text)
    await bot.send_message(chat_id=user_id, text="📸 <b>Endi blog uchun rasm yuboring:</b>",
        reply_markup=kb.back_button(), parse_mode='HTML')
    await state.set_state(cf.sena.create_blog_photo)


@router.message(or_f(F.photo, F.text == "🔙 Orqaga"), cf.sena.create_blog_photo)
async def blog_get_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "🔙 Orqaga":
        msg_text = "✏️ Blog tavsifini qaytadan kiriting:"
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.back_button())
        return await state.set_state(cf.sena.create_blog_description)
    
    data = await state.get_data()
    id_user = int(data.get('id_user') or db.get_user_by_telegram_id(telegram_id=user_id).id)
    photo_id = message.photo[-1].file_id
    blog = db.generate_user_blog(user_id=data['id_user'], title=data["new_blog_name"], content=data["new_blog_description"], photo_id=photo_id)
    blogs = db.get_user_blogs(user_id=id_user)
    admin_text = (
        "📝 <b>Yangi blog kelib tushdi!</b>\n\n"
        "👤 <b>Muallif:</b> <a href='tg://user?id={user_id}'>{full_name}</a>\n"
        "📌 <b>Sarlavha:</b> <i>{title}</i>\n\n"
        "🔎 Blog moderatsiyani kutmoqda. Iltimos, tekshiring va tasdiqlang yoki rad eting."
    ).format(
        user_id=user_id,
        full_name=message.from_user.full_name,
        title=blog.title
    )
    for ids in cf.admins:
        await bot.send_message(chat_id=ids, text=admin_text, parse_mode='HTML')
    await bot.send_message(chat_id=user_id,
        text="✅ <b>Blog moderatsiyaga yuborildi.</b>\nAdminlar tomonidan tasdiqlangach, u platformada ko‘rinadi.",
        reply_markup=kb.my_blogs_menu(blogs=blogs), parse_mode='HTML')
    await state.set_state(cf.sena.my_blogs)
################################################################################################

################################################################################################
@router.message(lambda msg: msg.text == "🏢 Loyiha haqida")
async def about_project(message: Message, state: FSMContext):
    user_id = message.from_user.id
    users_count = db.count_users()              
    projects_count = db.count_projects()        
    volunteers_count = db.count_helpers()       
    total_cash = db.count_total_cash()
    msg_text = (
        "🏢 <b>Platforma haqida</b>\n\n"
        "Bu platforma ijtimoiy loyihalarni yaratish, ularni qo‘llab-quvvatlash va targ‘ib qilish uchun ochilgan.\n\n"
        "🎯 Maqsadimiz — yaxshi niyatdagi tashabbuslarni bir joyga jamlash va yordam beruvchilarni birlashtirish.\n\n"
        f"📊 <b>Statistika:</b>\n"
        f"• 👤 Foydalanuvchilar: {users_count:_}\n"
        f"• 📂 Loyihalar: {projects_count:,}\n"
        f"• 🤝 Ko‘ngillilar: {volunteers_count:,}\n"
        f"• 💰 Yig‘ilgan mablag‘: {total_cash:_} so‘m\n\n"
        "📚 <b>Foydali havolalar:</b> Quyidagi tugmalar orqali kerakli bo‘limga o‘ting 👇"
    )
    await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.about_project_keyboard(), parse_mode='HTML')
################################################################################################

################################################################################################
@router.message(cf.sena.admin_menu)
async def admin_menu(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "📢 Hammaga xabar yuborish":
        msg_text = (
            "📣 <b>Umumiy xabar yaratish</b>\n\n"
            "Endi siz barcha foydalanuvchilarga yuboriladigan xabar ustida ishlamoqdasiz.\n\n"
            "📝 <b>1-qadam:</b> Iltimos, xabaringiz uchun qisqacha matnli tavsif (izoh) yozing.\n"
            "Bu tavsif postga biriktiriladi va barcha foydalanuvchilarga yuboriladi.\n\n"
            "➡️ Keyingi bosqichlarda siz rasm qo‘shishingiz yoki tugma orqali havola biriktirishingiz mumkin bo‘ladi."
        )
        await bot.send_message(chat_id=user_id, text=msg_text, parse_mode="HTML", reply_markup=kb.back_button())
        await state.set_state(cf.sena.admin_message_post)

    elif message.text == "🆕 Yangi loyihalar":
        msg_text = (
            "🆕 <b>Yangi yuborilgan loyihalar</b>\n\n"
            "Bu bo‘limda foydalanuvchilar tomonidan yuborilgan va hozircha tekshirilmagan loyihalar ro‘yxati ko‘rsatiladi."
        )
        await bot.send_message(chat_id=user_id, text=msg_text, parse_mode="HTML", reply_markup=kb.back_button())
        projects = db.get_unverified_projects()

        if not projects:
            await bot.send_message(chat_id=user_id, text="📭 Hozircha yangi yuborilgan loyiha mavjud emas.")
            return await state.set_state(cf.sena.admin_menu)

        for project in projects:
            await state.update_data(project_owner=project.user_id)
            msg_text = (
                f"📁 <b>{project.name}</b>\n\n"
                f"📄 {project.description}\n\n"
                f"👤 <a href='tg://user?id={project.user.telegram_id}'>{project.user.name or 'Foydalanuvchi'}</a>\n"
                f"🤝 Ko‘ngillilar soni: {len(project.helpers)}\n"
                f"💰 Homiylar soni: {len(project.donaters)}\n"
                f"🕐 Yuborilgan sana: {project.created_at.strftime('%Y-%m-%d')}"
            )
            await bot.send_photo(chat_id=user_id, photo=project.photo_id, caption=msg_text, parse_mode="HTML", reply_markup=kb.admin_project_review(project_id=project.id))
        await state.set_state(cf.sena.project_approve_reject)

    elif message.text == "📝 Yangi bloglar":
        msg_text = (
            "📝 <b>Yangi bloglar</b>\n\n"
            "Foydalanuvchilar tomonidan yuborilgan blog yozuvlarini ko‘rish va moderatsiya qilish imkoniyati."
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.back_button(), parse_mode="HTML")
        blogs = db.get_unverified_blogs()

        if not blogs:
            await bot.send_message(chat_id=user_id, text="📭 Hozircha yangi blog yozuvi mavjud emas.")
            return await state.set_state(cf.sena.admin_menu)
        for blog in blogs:
            msg_text = (
                f"📝 <b>{blog.title}</b>\n\n"
                f"{blog.content}\n\n"
                f"👤 <a href='tg://user?id={blog.user.telegram_id}'>{blog.user.name or 'Foydalanuvchi'}</a>"
            )
            await bot.send_photo(chat_id=user_id, photo=blog.photo_id, caption=msg_text, parse_mode="HTML", reply_markup=kb.admin_blog_review(blog_id=blog.id))
        await state.set_state(cf.sena.blog_approve_reject)

    elif message.text == "🔍 Loyiha izlash":
        msg_text = (
            "🔎 <b>Loyiha nomi yoki muallif bo‘yicha qidiring</b>"
            "\n\n📂 Bu bo‘limda siz yangi yuborilgan loyihalarni qulay va tez topishingiz mumkin."
            "\n👤 <i>Muallif ismini</i> yoki 📌 <i>loyiha nomini</i> kiriting — kerakli natijalar darhol chiqadi!"
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.admin_search_projects(), parse_mode="HTML")
        await state.set_state(cf.sena.admin_search_project)

    elif message.text == "👥 Foydalanuvchilar ro‘yxati":
        msg_text = (
            "👥 <b>Foydalanuvchilar ro‘yxati</b>\n\n"
            "Botdan foydalanayotgan barcha foydalanuvchilarning ro‘yxati va ularning faoliyati."
        )
        file_path = export_users_to_csv()
        await bot.send_document(chat_id=user_id, document=FSInputFile(file_path), caption=msg_text, parse_mode='HTML')

    elif message.text == "📊 Statistika":
        msg_text = (
            "📊 <b>Bot statistikasi</b>\n\n"
            "📌 Umumiy foydalanuvchilar: ...\n"
            "📌 Yaratilgan loyihalar: ...\n"
            "📌 Faol ko‘ngillilar: ...\n"
            "📌 Homiyliklar soni: ...\n\n"
            "Ushbu statistikalar yordamida tizim samaradorligini kuzatishingiz mumkin."
        )
        await bot.send_message(chat_id=user_id, text=msg_text, parse_mode="HTML", reply_markup=kb.admin_statistic())
        
    elif message.text == "🔙 Orqaga":
        await bot.send_photo(chat_id=user_id, photo=cf.start_photo, caption=cf.start_msg, reply_markup=kb.main_menu(), parse_mode="HTML")
        return await state.clear()

    else:
        await bot.send_message(chat_id=user_id, text="")
################################################################################################

################################################################################################
@router.message(cf.sena.admin_search_project)
async def admin_search_project(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "🔙 Orqaga":
        await bot.send_photo(chat_id=user_id, photo=cf.admin_photo, caption=cf.admin_msg, reply_markup=kb.admin_menu(), parse_mode="HTML")
        return await state.set_state(cf.sena.admin_menu)
    elif message.text == "🔎 Muallif bo‘yicha":
        msg_text = (
            "<b>🔎 Muallif bo‘yicha izlash</b>\n\n"
            "Iltimos, izlamoqchi bo‘lgan <b>muallif ismini</b> kiriting.\n"
            "Masalan: <i>Aliyev Diyor</i> yoki <i>G‘ulomova Zuxra</i>.\n\n"
            "📝 Biz sizga shu muallifga tegishli loyihalarni ko‘rsatamiz."
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.back_button(), parse_mode='HTML')
        await state.set_state(cf.sena.search_by_name)
    elif message.text == "🔎 Loyiha bo‘yicha":
        msg_text = (
            "<b>🔎 Loyiha bo‘yicha izlash</b>\n\n"
            "Iltimos, izlamoqchi bo‘lgan <b>loyiha nomini</b> kiriting.\n"
            "Masalan: <i>Toza havo</i>, <i>Yashil maktab</i> yoki <i>Quyosh energiyasi</i>.\n\n"
            "📂 Biz sizga shu nomga mos loyihalarni topamiz."
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.back_button(), parse_mode='HTML')
        await state.set_state(cf.sena.search_by_project)
    else:
        await bot.send_message(chat_id=user_id, text=(
                "<b>🤔 Noma’lum buyruq</b>\n\n"
                "Kechirasiz, bu buyruqni tushunmadim.\n"
                "Iltimos, menyudan <b>mos variant</b>ni tanlang yoki qaytadan urinib ko‘ring.\n\n"
                "⬅️ <i>Ortga qaytish uchun menyudagi tugmani bosing.</i>"), parse_mode="HTML")


# @router.message(cf.sena.search_by_name)
# async def menu_search_by_name(message: Message, state: FSMContext):
#     user_id = message.from_user.id
#     data = await state.get_data()
#     if message.text == "🔙 Orqaga":
#         msg_text = (
#             "🔎 <b>Loyiha nomi yoki muallif bo‘yicha qidiring</b>"
#             "\n\n📂 Bu bo‘limda siz yangi yuborilgan loyihalarni qulay va tez topishingiz mumkin."
#             "\n👤 <i>Muallif ismini</i> yoki 📌 <i>loyiha nomini</i> kiriting — kerakli natijalar darhol chiqadi!"
#         )
#         await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.admin_search_projects(), parse_mode="HTML")
#         return await state.set_state(cf.sena.admin_search_project)

#     if (message.text).isdigit():
#         tg_id = message.text
#         id_user = int(data.get('id_user') or db.get_user_by_telegram_id(telegram_id=tg_id).id)
#         user_projects = db.get_user_projects(user_id=id_user)




@router.message(cf.sena.search_by_project)
async def menu_search_by_project(message: Message, state: FSMContext):
    user_id = message.from_user.id
    projects = db.get_all_projects()
    if message.text == "🔙 Orqaga":
        msg_text = (
            "🔎 <b>Loyiha nomi yoki muallif bo‘yicha qidiring</b>"
            "\n\n📂 Bu bo‘limda siz yangi yuborilgan loyihalarni qulay va tez topishingiz mumkin."
            "\n👤 <i>Muallif ismini</i> yoki 📌 <i>loyiha nomini</i> kiriting — kerakli natijalar darhol chiqadi!"
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.admin_search_projects(), parse_mode="HTML")
        return await state.set_state(cf.sena.admin_search_project)
    for project in projects:
        if project.name == message.text:
            msg_text = (project.name, project.description)
            await bot.send_photo(chat_id=user_id, photo=project.photo_id, caption=msg_text, reply_markup=kb.(), parse_mode='HTML')
            return await state.set_state(cf.sena.searched_project)
    await bot.send_message(chat_id=user_id, text="Bunday loyiha nomi topilmadi", parse_mode="HTML")
################################################################################################

################################################################################################
@router.message(cf.sena.project_approve_reject)
async def back_blog_approve_reject(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "🔙 Orqaga":
        await bot.send_photo(chat_id=user_id, photo=cf.admin_photo, caption=cf.admin_msg, reply_markup=kb.admin_menu(), parse_mode="HTML")
        await state.set_state(cf.sena.admin_menu)
    else:
        await bot.send_message(chat_id=user_id, text="⚠️ Iltimos, '🔙 Orqaga' tugmasini tanlang yokida bloglarni qabul va bekor qiling.")


@router.callback_query(F.data.startswith("approve_project:"), cf.sena.project_approve_reject)
async def approve_project(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    project_id = int(callback.data.split(":")[1])
    db.update_project_field(project_id=project_id, field="status", value="active")
    project = db.get_project_by_id(project_id=project_id)
    if not project:
        return await callback.answer("❌ Loyiha topilmadi.", show_alert=True)

    msg_text = (
        f"📢 <b>Yangi loyiha!</b>\n\n"
        f"📁 <b>{project.name}</b>\n"
        f"{project.description}\n\n"
        f"🕐 Sana: {project.created_at.strftime('%Y-%m-%d')}\n"
        f"🤝 Ko‘ngillilar: {len(project.helpers)} ta\n"
        f"💰 Homiylar: {len(project.donaters)} ta"
    )

    await bot.send_photo(
        chat_id=cf.project_posts_channel,
        photo=project.photo_id,
        caption=msg_text,
        reply_markup=kb.project_post_keyboard(project_id),
        parse_mode='HTML'
    )
    users = db.get_all_users()
    notify_text = (
        f"📣 <b>Yangi loyiha e'lon qilindi!</b>\n\n"
        f"<b>{project.name}</b> — yangi tashabbusga qo‘shiling yoki homiylik qiling!\n"
        f"👉 Batafsil ma’lumot kanalimizda! -> {cf.project_posts_channel}"
    )
    for user in users:
        try:
            await bot.send_message(chat_id=user.telegram_id, text=notify_text, parse_mode="HTML")
        except Exception as e:
            print(f"❌ Failed to notify user {user.telegram_id}: {e}")

    await bot.answer_callback_query(callback.id, text="✅ Loyiha tasdiqlandi.", show_alert=False)
    await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)


@router.callback_query(F.data.startswith("reject_project:"), cf.sena.project_approve_reject)
async def reject_blog(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    project_id = int(callback.data.split(":")[1])
    db.delete_user_project(project_id, int(data['project_owner']))
    await bot.answer_callback_query(callback_query_id=callback.id, text="❌ Loyiha rad etildi va o‘chirildi.", show_alert=False)
    await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
################################################################################################

################################################################################################
@router.message(cf.sena.blog_approve_reject)
async def back_blog_approve_reject(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "🔙 Orqaga":
        await bot.send_photo(chat_id=user_id, photo=cf.admin_photo, caption=cf.admin_msg, reply_markup=kb.admin_menu(), parse_mode="HTML")
        await state.set_state(cf.sena.admin_menu)
    else:
        await bot.send_message(chat_id=user_id, text="⚠️ Iltimos, '🔙 Orqaga' tugmasini tanlang yokida bloglarni qabul va bekor qiling.")


@router.callback_query(F.data.startswith("approve_blog:"), cf.sena.blog_approve_reject)
async def approve_blog(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    blog_id = int(callback.data.split(":")[1])
    db.update_blog_field(blog_id=blog_id, field="is_verified", value=True)
    blog = db.get_blog_by_id(blog_id=blog_id)
    msg_text = (
        f"📝 <b>{blog.title}</b>\n\n"
        f"{blog.content}\n\n"
        f"👤 <a href='tg://user?id={blog.user.telegram_id}'>{blog.user.name or 'Foydalanuvchi'}</a>"
    )
    await bot.send_message(chat_id=cf.project_blogs_channel, text=msg_text, parse_mode="HTML")
    await bot.answer_callback_query(callback_query_id=callback.id, text="✅ Blog tasdiqlandi.", show_alert=False)
    await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)


@router.callback_query(F.data.startswith("reject_blog:"), cf.sena.blog_approve_reject)
async def reject_blog(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    blog_id = int(callback.data.split(":")[1])
    db.delete_blog(blog_id)
    await bot.answer_callback_query(callback_query_id=callback.id, text="❌ Blog rad etildi va o‘chirildi.", show_alert=False)
    await bot.delete_message(chat_id=user_id, message_id=callback.message.message_id)
################################################################################################

################################################################################################
@router.message(cf.sena.admin_message_post)
async def menu_admin_message_post(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "🔙 Orqaga":
        await bot.send_photo(chat_id=user_id, photo=cf.admin_photo, caption=cf.admin_msg, reply_markup=kb.admin_menu(), parse_mode='HTML')
        await state.set_state(cf.sena.admin_menu)
    else:
        await state.update_data(message_description=message.text)
        msg_text = (
            "📷 <b>2-qadam: Rasm qo‘shish (ixtiyoriy)</b>\n\n"
            "Agar xabaringizga rasm biriktirmoqchi bo‘lsangiz, hozir yuboring. "
            "Agar rasm kerak bo‘lmasa, «O‘tkazib yuborish» tugmasini bosing."
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.admin_message_keyboard(), parse_mode="HTML")
        await state.set_state(cf.sena.admin_message_photo)


@router.message(cf.sena.admin_message_photo)
async def menu_admin_message_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "🔙 Orqaga":
        msg_text = (
            "📝 <b>1-qadam: Tavsif matni</b>\n\n"
            "Iltimos, yubormoqchi bo‘lgan xabaringizning matnini yozing.\n"
            "Bu matn barcha foydalanuvchilarga yuboriladi."
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.admin_message_keyboard(), parse_mode="HTML")
        await state.set_state(cf.sena.admin_message_post)
    elif message.text == "⏭️ O‘tkazib yuborish":
        await state.update_data(message_photo=None)
        msg_text = (
            "🔗 <b>3-qadam: Tugma bilan havola biriktirish (ixtiyoriy)</b>\n\n"
            "Agar postga havola qo‘shmoqchi bo‘lsangiz, quyidagi shaklda yozing:\n"
            "<code>Do‘konni ko‘rish - https://example.com</code>\n\n"
            "Agar kerak bo‘lmasa, «⏭️ O‘tkazib yuborish» tugmasini bosing."
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.admin_message_keyboard(), parse_mode="HTML")
        await state.set_state(cf.sena.admin_message_button)
    else:
        if message.photo:
            await state.update_data(message_photo=message.photo[-1].file_id)
            msg_text = (
                "🔗 <b>3-qadam: Tugma bilan havola biriktirish (ixtiyoriy)</b>\n\n"
                "Agar postga havola qo‘shmoqchi bo‘lsangiz, quyidagi shaklda yozing:\n"
                "<code>Do‘konni ko‘rish - https://example.com</code>\n\n"
                "Agar kerak bo‘lmasa, «⏭️ O‘tkazib yuborish» tugmasini bosing."
            )
            await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.admin_message_keyboard(),
                                parse_mode="HTML")
            await state.set_state(cf.sena.admin_message_button)
        else:
            await bot.send_message(chat_id=user_id, text="⚠️ Iltimos, rasm yuboring..")


@router.message(cf.sena.admin_message_button)
async def menu_admin_message_button(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "🔙 Orqaga":
        msg_text = (
            "📷 <b>2-qadam: Rasm qo‘shish (ixtiyoriy)</b>\n\n"
            "Agar rasm biriktirmoqchi bo‘lsangiz, hozir yuboring.\n"
            "Yoki «⏭️ O‘tkazib yuborish» tugmasini bosing."
        )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.admin_message_keyboard(), parse_mode="HTML")
        await state.set_state(cf.sena.admin_message_photo)
    elif message.text == "⏭️ O‘tkazib yuborish":
        await state.update_data(message_button=None)
        await show_preview_and_confirm(message, state)
        await state.set_state(cf.sena.admin_message_final)

    else:
        try:
            text, url = message.text.split(" - ")
            await state.update_data(message_button={"text": text.strip(), "url": url.strip()})
            await show_preview_and_confirm(message, state)
            await state.set_state(cf.sena.admin_message_final)
        except:
            await bot.send_message(user_id, "❗️ Format noto‘g‘ri. Iltimos, quyidagicha yozing:\n<code>Nom - https://example.com</code>",
                                   parse_mode="HTML")


async def show_preview_and_confirm(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    description = data.get("message_description")
    photo = data.get("message_photo")
    button = data.get("message_button")

    if message.text == "🔙 Orqaga":
        msg_text = (
                "🔗 <b>3-qadam: Tugma bilan havola biriktirish (ixtiyoriy)</b>\n\n"
                "Agar postga havola qo‘shmoqchi bo‘lsangiz, quyidagi shaklda yozing:\n"
                "<code>Do‘konni ko‘rish - https://example.com</code>\n\n"
                "Agar kerak bo‘lmasa, «⏭️ O‘tkazib yuborish» tugmasini bosing."
            )
        await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.admin_message_keyboard(), parse_mode="HTML")
        return await state.set_state(cf.sena.admin_message_button)

    markup = None
    if button:
        markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=button['text'], url=button['url'])]
        ])

    if photo:
        await bot.send_photo(chat_id=user_id, photo=photo, caption=description, reply_markup=markup, parse_mode="HTML")
    else:
        await bot.send_message(chat_id=user_id, text=description, reply_markup=markup, parse_mode="HTML")

    await bot.send_message(user_id,
        "✅ <b>Xabar tayyor!</b>\n\nBarchasini tekshiring. Hammasi to‘g‘rimi?\n\n"
        "Yuborish uchun «📨 Yuborish» tugmasini bosing yoki «🔙 Orqaga» bilan o‘zgartiring.",
        reply_markup=kb.confirm_keyboard(), parse_mode="HTML")
    

@router.message(cf.sena.admin_message_final)
async def menu_admin_message_final(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "🔙 Orqaga":
        await show_preview_and_confirm(message, state)
    elif message.text == "📨 Yuborish":
        users = db.get_all_users()
        count = await send_to_all_users(bot, state, users)

        await bot.send_message(chat_id=user_id, text=f"✅ Xabar {count} foydalanuvchiga muvaffaqiyatli yuborildi!", reply_markup=kb.admin_menu())
        await state.set_state(cf.sena.admin_menu)


async def send_to_all_users(bot, state: FSMContext, users: list[int]):
    data = await state.get_data()
    description = data.get("message_description")
    photo = data.get("message_photo")
    button = data.get("message_button")
    markup = None
    if button:
        markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=button['text'], url=button['url'])]
        ])

    success = 0
    for user in users:
        try:
            if photo:
                await bot.send_photo(chat_id=user.telegram_id, photo=photo, caption=description,
                                     reply_markup=markup, parse_mode="HTML")
            else:
                await bot.send_message(chat_id=user.telegram_id, text=description,
                                       reply_markup=markup, parse_mode="HTML")
            success += 1
            await sleep(0.05) 
        except TelegramRetryAfter as e:
            await sleep(e.retry_after)
        except TelegramForbiddenError:
            pass  
        except Exception as e:
            print(f"Xatolik {user.telegram_id} ga yuborishda:", e)

    return success
################################################################################################