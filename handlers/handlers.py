from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from keyboards.inline import *
from sheets import *


router = Router()


@router.message(Command(commands=["start", "menu"]))
async def start(message: Message):
    if message.from_user.id in roles["Админ склада"]:
        await message.answer(
            "Меню Админа склада", reply_markup=inline_keyboard_menu_admin_sklada
        )
    elif message.from_user.id in roles["Супер юзер"]:
        await message.answer("Меню Админа", reply_markup=inline_keyboard_menu_admin)
    elif message.from_user.id in roles["Курьер"]:
        await message.answer("Меню Курьера", reply_markup=inline_keyboard_menu_courier)
