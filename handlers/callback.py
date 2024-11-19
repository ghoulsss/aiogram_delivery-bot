from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from sheets import *
from keyboards.inline import *
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from datetime import datetime
from pytz import timezone


router1 = Router()


class Zadanie(StatesGroup):
    text = State()


class Otchet(StatesGroup):
    text = State()


class Zayavka(StatesGroup):
    text = State()


class Case1(StatesGroup):
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
        buffer += f"{i[0]}: Адрес: {find_address(i[1])}\nВладелец: {i[2]}\nТелефон: {create_whatsapp_link(i[3])}\nПримечание: {i[4]}\n\n"

    await callback.message.answer(text=f"{buffer}", disable_web_page_preview=True)
    await callback.answer("")


@router1.callback_query(F.data == "Заявка")  # админ_склада вывод
async def zayavka_callback(callback: CallbackQuery):
    # Получаем доступ к таблице "Заявки"
    worksheet_zayavki = sh.worksheet("Заявки")

    # Получаем все данные из таблицы
    zayavki_data = worksheet_zayavki.get_all_values()

    # Инициализируем буфер для хранения строк
    buffer = ""

    # Проходим по всем строкам, начиная со второй (пропуская заголовок)
    for i in zayavki_data[1:]:
        # Получаем значения из ячеек
        address = find_address(i[0])  # Предполагается, что адрес в первой колонке
        owner = i[1]  # Предполагается, что владелец во второй колонке
        quantity = i[2]  # Предполагается, что количество в третьей колонке

        # Проверяем, не пустые ли значения и формируем строку
        if address and owner and quantity:
            buffer += (
                f"Адрес: {address}\n"
                f"Владелец: {owner}\n"
                f"Количество: {quantity}\n\n"
            )

    await callback.message.answer(text=f"{buffer}", disable_web_page_preview=True)
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
            buffer += f"Адрес: {find_address(i[0])}\nВладелец: {i[1]}\nТелефон: {create_whatsapp_link(i[2])}\n\n"
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
        total_deducted = 0  # Переменная для суммирования
        for line in file:
            row = line.strip().split()
            buf.append(row)
            if len(row) > 2:  # Убедитесь, что в строке есть хотя бы 3 столбца
                try:
                    total_deducted += int(
                        row[2]
                    )  # Суммируем количество из третьего столбца
                except ValueError:
                    pass  # Если значение нельзя преобразовать в int, просто пропускаем

    worksheet = sh.worksheet("Задание")
    worksheet.append_rows(buf)

    with open("add_zadanie.txt", "w") as file:
        pass

    await callback.message.edit_text(text=f"Задание отправлено в таблицу")
    await callback.answer("")


@router1.callback_query(F.data == "Добавить_задание")  # админ_склада
async def reglament_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Zadanie.text)
    await callback.message.edit_text(text="Введите Адрес Владельца Телефон")
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
        total_to_deduct = 0
        for line in file:
            row = line.strip().split()
            row.append(int(row[2]) - int(row[1]))
            total_to_deduct += int(row[2]) - int(row[1])
            buf.append(row)

    worksheet_zada = sh.worksheet("Задание")
    try:
        d2_value = int(worksheet_zada.cell(2, 4).value)
    except (ValueError, AttributeError):
        print("Error: Cell D2 in 'Задание' sheet is not a valid integer or is empty.")
        d2_value = 0

    # Subtract the total to deduct from D2
    new_d2_value = max(d2_value - total_to_deduct, 0)  # Prevent negative values

    worksheet_zada.update_cell(2, 4, new_d2_value)

    worksheet = sh.worksheet("Отчет")

    worksheet.append_rows(buf)

    with open("add_otchet.txt", "w") as file:
        pass

    await callback.message.edit_text(text=f"Отчет отправлен в таблицу")
    await callback.answer("")


@router1.callback_query(F.data == "Добавить_отчет")  # админ_склада
async def reglament_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Otchet.text)
    await callback.message.edit_text(text="Введите Адрес Было Стало")
    await callback.answer("")


@router1.message(Otchet.text)
async def reglament_process_callback(message: Message, state: FSMContext):
    moscow_tz = timezone("Europe/Moscow")
    current_date = datetime.now(moscow_tz).strftime("%d-%m-%Y")  # время %H:%M:%S
    data = message.text
    await state.clear()
    with open("add_otchet.txt", "a") as file:
        file.writelines(f"{data} {current_date}\n")

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
    worksheet_total = sh.worksheet("Общее количество")

    # tasks_data = worksheet_zada.get_all_values()
    # total_quantity = 0
    # for row in tasks_data[1:]:
    #     try:
    #         total_quantity += int(row[2])
    #     except (ValueError, IndexError):
    #         continue

    # current_total_quantity = int(
    #     worksheet_total.cell(2, 1).value
    # )  # Получаем текущее количество из A2

    # # Обновляем ячейку A2 с новым значением
    # new_total_quantity = current_total_quantity + total_quantity
    # worksheet_total.update_cell(2, 1, new_total_quantity)
    # ------------------
    try:
        d2_value = int(worksheet_zada.cell(2, 4).value)  # Get value from D2
    except (ValueError, AttributeError):
        print("Error: Cell D2 in 'Задание' sheet is not a valid integer or is empty.")
        d2_value = 0  # Handle error gracefully

    current_total_quantity = int(worksheet_total.cell(2, 1).value)

    new_total_quantity = current_total_quantity + d2_value
    worksheet_total.update_cell(2, 1, new_total_quantity)
    # ------------------

    worksheet_otch.batch_clear(["A2:F"])
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
    await callback.message.edit_text(text="Введите Адрес Владельца Количество")
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
    normalized_number = "".join(filter(str.isdigit, phone_number))
    return f"https://wa.me/{normalized_number}"


@router1.callback_query(F.data == "Кейс")  # курьер
async def reglament_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Выберите одно действие", reply_markup=inline_keyboard_case
    )
    await callback.answer("")


@router1.callback_query(F.data == "Добавить_кейс")  # админ_склада
async def reglament_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Case1.text)
    await callback.message.edit_text(text="Введите Количество")
    await callback.answer("")


@router1.message(Case1.text)
async def reglament_process_callback(message: Message, state: FSMContext):
    data = message.text
    await state.clear()
    with open("add_case.txt", "a") as file:
        file.writelines(f"{data}\n")

    await message.answer(
        f"Добавлено, нажмите подтвердить чтобы отправить в таблицу",
        reply_markup=inline_keyboard_case,
    )


@router1.callback_query(F.data == "Подтвердить_кейс")  # админ
async def reglament_callback(callback: CallbackQuery):
    # worksheet_zada = sh.worksheet("Задание")
    # worksheet_total = sh.worksheet("Общее количество")
    # with open("add_case.txt", "r", encoding="utf-8") as file:
    #     last_line = ""
    #     for line in file:
    #         last_line = line.strip()

    #     new_quantity = int(last_line)

    # worksheet_zada.update_cell(2, 4, new_quantity)

    # current_total = int(worksheet_total.cell(2, 1).value)
    # new_total = max(0, current_total - new_quantity)
    # worksheet_total.update_cell(2, 1, new_total)

    # await callback.message.answer(text=f"Кейс добавлен")
    # await callback.answer("")
    worksheet_zada = sh.worksheet("Задание")
    worksheet_total = sh.worksheet("Общее количество")

    with open("add_case.txt", "r", encoding="utf-8") as file:
        last_line = ""
        for line in file:
            last_line = line.strip()

    new_quantity = int(last_line)
    # Get the current value from D2
    current_d2_value = worksheet_zada.cell(2, 4).value
    try:
        current_d2_int = int(
            current_d2_value
        )  # Attempt conversion to integer; handles empty cells
    except ValueError:
        current_d2_int = 0  # Default to 0 if cell is empty or contains non-integer data

    # Add new quantity to the current quantity in D2
    updated_d2_value = current_d2_int + new_quantity
    worksheet_zada.update_cell(2, 4, updated_d2_value)

    # Update "Общее количество"
    current_total = int(worksheet_total.cell(2, 1).value)
    new_total = max(0, current_total - new_quantity)  # Prevent negative total
    worksheet_total.update_cell(2, 1, new_total)
    await callback.message.answer(
        text=f"Кейс добавлен. Новое значение в: {updated_d2_value}"
    )
    await callback.answer("")


@router1.callback_query(F.data == "Заново_кейс")  # админ_склада
async def reglament_callback(callback: CallbackQuery):
    with open("add_case.txt", "w") as file:
        pass

    await callback.message.edit_text(text="Кейс очищена!")
    await callback.answer("")
