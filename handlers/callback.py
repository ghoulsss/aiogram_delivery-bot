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

    await callback.message.answer(text=f"{buffer}", disable_web_page_preview=True)
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

    # Получаем значение из ячейки A2 и преобразуем в целое число
    total_quantity_cell = sh.worksheet("Общее количество").cell(2, 1).value
    print(f"Значение из ячейки A2: '{total_quantity_cell}'")  # Отладочная информация

    try:
        current_total_quantity = int(total_quantity_cell)
    except ValueError:
        await callback.message.answer(
            "Ошибка: значение в ячейке A2 не является числом."
        )
        return  # Завершаем выполнение при ошибке

    # Проверяем, достаточно ли товара для вычитания
    if current_total_quantity >= total_deducted:
        new_total_quantity = current_total_quantity - total_deducted
        print(
            f"Обновляем ячейку A2 значением: {new_total_quantity}"
        )  # Отладочная информация
        # Обновляем значение в Google Sheets
        sh.worksheet("Общее количество").update("A2", [[new_total_quantity]])
        await callback.message.answer(
            f"Общее количество товара обновлено. Остаток: {new_total_quantity}"
        )
    else:
        await callback.message.answer(
            "Недостаточно товара для выполнения данного задания."
        )
    await callback.message.edit_text(text=f"Задание отправлено в таблицу")
    await callback.answer("")


@router1.callback_query(F.data == "Добавить_задание")  # админ_склада
async def reglament_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Zadanie.text)
    await callback.message.edit_text(text="Введите Адрес Владельца Количество Телефон")
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
            row.append(int(row[3]) - int(row[2]))
            buf.append(row)

    # Загрузка данных из таблицы заданий
    tasks_worksheet = sh.worksheet("Задание")
    tasks_data = tasks_worksheet.get_all_values()

    # Создаем словарь для быстрого поиска по адресу
    tasks_dict = {row[0]: int(row[2]) for row in tasks_data[1:]}  # Пропускаем заголовок

    for entry in buf:
        address = entry[0]  # Адрес из отчета
        quantity_before = int(entry[2])  # "Было" из отчета
        quantity_now = int(entry[3])  # "Стало" из отчета
        quantity_to_deduct = (
            quantity_before + quantity_now
        )  # Вычисляем, сколько нужно вычесть

        if address in tasks_dict:
            # Вычисляем новое количество
            new_quantity = tasks_dict[address] - quantity_to_deduct

            # Обновляем запись в таблице заданий
            row_index = next(
                (
                    index
                    for index, row in enumerate(tasks_data[1:])
                    if row[0] == address
                ),
                None,
            )

            if row_index is not None:
                tasks_worksheet.update_cell(
                    row_index + 2, 3, max(new_quantity, 0)
                )  # Обновляем количество

    worksheet = sh.worksheet("Отчет")

    worksheet.append_rows(buf)

    with open("add_otchet.txt", "w") as file:
        pass

    await callback.message.edit_text(text=f"Отчет отправлен в таблицу")
    await callback.answer("")


@router1.callback_query(F.data == "Добавить_отчет")  # админ_склада
async def reglament_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Otchet.text)
    await callback.message.edit_text(text="Введите Адрес Владельца Было Стало")
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

    existing_data = worksheet_otch.get_all_values()[1:]
    if existing_data:
        pass

    worksheet_otch.batch_clear(["A2:E"])
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
    normalized_number = "".join(filter(str.isdigit, phone_number))
    return f"https://wa.me/{normalized_number}"
