from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from sheets import *
from keyboards.inline import *
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


router1 = Router()


class Zadanie(StatesGroup):
    text = State()


class Otchet(StatesGroup):
    text = State()


class Zayavka(StatesGroup):
    text = State()


@router1.callback_query(F.data == "Адреса")  # общая
async def adress_callback(callback: CallbackQuery):
    adress = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range="Адреса")
        .execute()
        .get("values", [])
    )
    buffer = ""
    for i in adress[1:]:
        buffer += f"Адрес: {find_address(i[1])}\nВладелец: {i[2]}\nТелефон: {create_whatsapp_link(i[3])}\nПримечание: {i[4]}\n\n"

    await callback.message.answer(text=f"{buffer}")
    await callback.answer("")


@router1.callback_query(F.data == "Заявка")  # админ_склада вывод
async def zayavka_callback(callback: CallbackQuery):
    adress = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range="Заявки")
        .execute()
        .get("values", [])
    )

    buffer = ""
    for i in adress[1:]:
        buffer += (
            f"Адрес: {find_address(i[2])}\nВладелец: {i[3]}\nКоличество: {i[4]}\n\n"
        )

    await callback.message.answer(text=f"{buffer}")
    await callback.answer("")


@router1.callback_query(F.data == "Меню")  #  общая
async def adress_callback(callback: CallbackQuery):
    if callback.from_user.id in roles["Админ склада"]:
        await callback.message.edit_text(
            text="Меню Админа склада",
            reply_markup=inline_keyboard_menu_admin_sklada,
        )
        await callback.answer("")
    elif callback.from_user.id in roles["Супер юзер"]:
        await callback.message.edit_text(
            text="Меню Главного админа", reply_markup=inline_keyboard_menu_admin
        )
        await callback.answer("")
    elif callback.from_user.id in roles["Курьер"]:
        await callback.message.edit_text(
            text="Меню Курьера", reply_markup=inline_keyboard_menu_courier
        )
        await callback.answer("")


@router1.callback_query(F.data == "Дневное_задание")  # курьер вывод
async def reglament_callback(callback: CallbackQuery):
    adress = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range="Задание")
        .execute()
        .get("values", [])
    )

    buffer = ""
    try:
        for i in adress[1:]:
            buffer += f"Адрес: {find_address(i[0])}\nВладелец: {i[1]}\nКоличество: {i[2]}\nТелефон: {create_whatsapp_link(i[3])}\n\n"
        await callback.message.edit_text(
            text=f"{buffer}", disable_web_page_preview=True
        )
    except IndexError:
        callback.message.edit_text(text="Ошибка в таблице")
    finally:
        await callback.answer("")


@router1.callback_query(F.data == "Заявка")  # курьер
async def reglament_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Введите адрес", reply_markup=inline_keyboard_zayavka
    )
    await callback.answer("")


@router1.callback_query(F.data == "Задание")  # админ_склада
async def zadanie_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Выберите одно действие", reply_markup=inline_keyboard_zadanie
    )
    await callback.answer("")


@router1.callback_query(F.data == "Подтвердить_задание")  # админ_склада
async def reglament_callback(callback: CallbackQuery):
    with open("add_zadanie.txt", "r", encoding="utf-8") as file:
        buf = []
        for line in file:
            row = line.strip().split()
            buf.append(row)

    worksheet = sh.worksheet("Задание")

    worksheet.append_rows(buf)

    with open("add_zadanie.txt", "w") as file:
        pass

    await callback.message.edit_text(text=f"Задание отправлено в таблицу")
    await callback.answer("")


@router1.callback_query(F.data == "Добавить_задание")  # админ_склада
async def reglament_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Zadanie.text)
    await callback.message.edit_text(
        text="Введите Адрес Владельца Количество Наименование Телефон"
    )
    await callback.answer("")


@router1.message(Zadanie.text)
async def reglament_process_callback(message: Message, state: FSMContext):
    data = message.text
    await state.clear()
    with open("add_zadanie.txt", "a") as file:
        file.writelines(f"{data}\n")

    await message.answer(
        f"Добавлено, нажмите подтвердить чтобы отправить в таблицу",
        reply_markup=inline_keyboard_zadanie,
    )


@router1.callback_query(F.data == "Заново_задание")  # админ_склада
async def reglament_callback(callback: CallbackQuery):
    with open("add_zadanie.txt", "w") as file:
        pass
    await callback.message.edit_text(text="Задание очищено")
    await callback.answer("")


@router1.callback_query(F.data == "Оставить_заявку")  # курьер
async def zayavka_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Выберите одно действие", reply_markup=inline_keyboard_zayavka
    )
    await callback.answer("")


@router1.callback_query(F.data == "Отчет")  # курьер
async def reglament_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Выберите одно действие", reply_markup=inline_keyboard_otchet
    )
    await callback.answer("")


@router1.callback_query(F.data == "Подтвердить_отчет")  # курьер
async def reglament_callback(callback: CallbackQuery):
    with open("add_otchet.txt", "r", encoding="utf-8") as file:
        buf = []
        for line in file:
            row = line.strip().split()
            buf.append(row)

    worksheet = sh.worksheet("Отчет")

    worksheet.append_rows(buf)

    with open("add_otchet.txt", "w") as file:
        pass

    # ------------------------------------------------------------------------------
    sheet_sort = sh.worksheet("Сортировка")
    sheet_otchet = sh.worksheet("Отчет")

    sorti = sheet_sort.get_all_records()
    otchet = sheet_otchet.get_all_records()

    inventory1 = {
        row["Наименование"]: {
            "id товара": row["id товара"],
            "Количество": row["Количество"],
            "Цена": row["Цена"],
        }
        for row in sorti
    }
    inventory2 = {row["Наименование"]: row["Количество"] for row in otchet}

    result_inventory = {}
    for name, data in inventory1.items():
        id_ = data["id товара"]
        qty1 = data["Количество"]
        price = data["Цена"]
        qty2 = inventory2.get(name, 0)

        result_inventory[name] = {
            "id товара": id_,
            "Количество": qty1 - qty2,
            "Цена": price,
        }

    new_data = [
        [data["id товара"], name, data["Количество"], data["Цена"]]
        for name, data in result_inventory.items()
    ]

    sheet_sort.batch_clear(["A2:Z"])
    sheet_sort.append_rows(new_data, value_input_option="RAW")
    # -----------------------------------------------------------------------------
    await callback.message.edit_text(text=f"Отчет отправлен в таблицу")
    await callback.answer("")


@router1.callback_query(F.data == "Добавить_отчет")  # админ_склада
async def reglament_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Otchet.text)
    await callback.message.edit_text(
        text="Отчет : Введите Адрес Владельца Наименование Количество"
    )
    await callback.answer("")


@router1.message(Otchet.text)
async def reglament_process_callback(message: Message, state: FSMContext):
    data = message.text
    await state.clear()
    with open("add_otchet.txt", "a") as file:
        file.writelines(f"{data}\n")

    await message.answer(
        f"Добавлено, нажмите подтвердить чтобы отправить в таблицу",
        reply_markup=inline_keyboard_otchet,
    )


@router1.callback_query(F.data == "Заново_отчет")  # админ_склада
async def reglament_callback(callback: CallbackQuery):
    with open("add_otchet.txt", "w") as file:
        pass
    await callback.message.edit_text(text="Отчет очищен")
    await callback.answer("")


@router1.callback_query(F.data == "День_окончен")  # курьер
async def reglament_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "Нажмите подтвердить чтобы очистить", reply_markup=inline_keyboard_denoc
    )
    await callback.answer("")


@router1.callback_query(F.data == "Подтвердить_день")
async def reglament_callback(callback: CallbackQuery):
    worksheet_otch = sh.worksheet("Отчет")
    worksheet_zada = sh.worksheet("Задание")
    worksheet_vse = sh.worksheet("Общее количество")

    existing_data = worksheet_otch.get_all_values()[1:]
    if existing_data:
        pass

    worksheet_otch.batch_clear(["A2:D"])
    worksheet_zada.batch_clear(["A2:G"])
    await callback.message.edit_text(text="Отчет и Задание очищены")
    await callback.answer("")


@router1.callback_query(F.data == "Подтвердить_заявка")  # курьер
async def reglament_callback(callback: CallbackQuery):
    with open("add_zayavka.txt", "r", encoding="utf-8") as file:
        buf = []
        for line in file:
            row = line.strip().split()
            buf.append(row)

    worksheet = sh.worksheet("Заявки")

    worksheet.append_rows(buf)

    with open("add_zayavka.txt", "w") as file:
        pass

    await callback.message.edit_text(text=f"Заявка отправлена в таблицу")
    await callback.answer("")


@router1.callback_query(F.data == "Добавить_заявка")  # админ_склада
async def reglament_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Zayavka.text)
    await callback.message.edit_text(
        text="Введите Адрес Владельца Наименование Количество"
    )
    await callback.answer("")


@router1.message(Zayavka.text)
async def reglament_process_callback(message: Message, state: FSMContext):
    data = message.text
    await state.clear()
    with open("add_zayavka.txt", "a") as file:
        file.writelines(f"{data}\n")

    await message.answer(
        f"Добавлено, нажмите подтвердить чтобы отправить в таблицу",
        reply_markup=inline_keyboard_zayavka,
    )


@router1.callback_query(F.data == "Заново_заявка")  # админ_склада
async def reglament_callback(callback: CallbackQuery):
    with open("add_zayavka.txt", "w") as file:
        pass

    await callback.message.edit_text(text="Заявка очищена!")
    await callback.answer("")


@router1.callback_query(F.data == "Обновить_пользователей")  # админ
async def reglament_callback(callback: CallbackQuery):
    await remove_users()
    await get_users()
    await callback.message.answer(text=f"Пользователи обновлены")
    await callback.answer("")


def find_address(address):
    if address:
        url = f"https://yandex.ru/maps/?text={'+'.join(address.split())}"
        message_text = f"{url}"
        return message_text
    else:
        return "Адрес не найден"


def create_whatsapp_link(phone_number):
    # Уберите любые символы кроме цифр
    normalized_number = "".join(filter(str.isdigit, phone_number))
    # Создайте ссылку
    return f"https://wa.me/{normalized_number}"
