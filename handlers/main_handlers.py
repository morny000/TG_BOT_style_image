from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from preload.states import Aktiv
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
import os
from preload.functions import image_merge


router = Router()


@router.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext) -> None:
    builder = InlineKeyboardBuilder()
    builder.button(text="Слияние 🖼️ + 🖼️ = 🖼️🖼️", callback_data="merge_image")
    sent_message = await message.answer("Привет!🤚"
                         "\nЭто бот для слияния Ваших двух картинок в одну!"
                          "\n💞Мы заранее благодарим Вас за использование нашего бота!"
                          '\n\nДля начала работы, пожалуйста, нажмите кнопку!',
                         reply_markup=builder.as_markup())
    await state.update_data(delete_id=sent_message.message_id)


@router.callback_query(F.data == "merge_image")
async def start_merge(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    delete_id = data.get("delete_id")
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=delete_id)

    sent_message = await callback.message.answer("Отправьте фото объекта")
    await state.update_data(delete_id=sent_message.message_id)
    await state.set_state(Aktiv.expectation_image_one)
    await callback.answer()


@router.message(Aktiv.expectation_image_one)
async def get_image_one(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    delete_id = data.get("delete_id")
    await bot.delete_message(chat_id=message.chat.id, message_id=delete_id)

    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    image_path = f"{photo.file_id}.jpg"
    await bot.download_file(file_info.file_path, image_path)

    await state.update_data(one_foto=image_path)
    sent_message = await message.answer("Отправьте фото стиля") #надо писать sent перед await
    await state.update_data(delete_id=sent_message.message_id) #обновляет айди стейта
    await state.set_state(Aktiv.expectation_image_two)


@router.message(Aktiv.expectation_image_two)
async def get_image_two(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    delete_id = data.get("delete_id")
    await bot.delete_message(chat_id=message.chat.id, message_id=delete_id)

    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    image_path = f"{photo.file_id}.jpg"
    await bot.download_file(file_info.file_path, image_path)

    await state.update_data(two_foto=image_path)
    data = await state.get_data()
    one_foto = data.get("one_foto")
    two_foto = data.get("two_foto")

    image_merge(one_foto, two_foto)


    image_from_pc = FSInputFile("image.jpg")
    await message.answer_photo(image_from_pc, caption="Результат слияния ваших фото")


    await state.clear()
    if os.path.exists(one_foto):
        os.remove(one_foto)
    if os.path.exists(two_foto):
        os.remove(two_foto)
    if os.path.exists("image.jpg"):
        os.remove("image.jpg")

