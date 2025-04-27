from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from preload.states import Aktiv
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
import PIL.Image
import numpy as np


router = Router()


@router.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    builder = InlineKeyboardBuilder()
    builder.button(text="Слияние 🖼️ + 🖼️ = 🖼️🖼️", callback_data="merge_image")
    await message.answer("Привет!🤚"
                         "\nЭто бот для слияния Ваших двух картинок в одну!"
                          "\n💞Мы заранее благодарим Вас за использование нашего бота!"
                          '\n\nДля начала работы, пожалуйста, нажмите кнопку!',
                         reply_markup=builder.as_markup())


@router.callback_query(F.data == "merge_image")
async def start_merge(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Отправьте фото объекта")
    await state.set_state(Aktiv.expectation_image_one)
    await callback.answer()


@router.message(Aktiv.expectation_image_one)
async def get_image_one(message: types.Message, state: FSMContext, bot: Bot):
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    image_path = f"{photo.file_id}.jpg"
    await bot.download_file(file_info.file_path, image_path)


    await state.update_data(one_foto=image_path)
    await message.answer("Отправьте фото стиля")
    await state.set_state(Aktiv.expectation_image_two)


@router.message(Aktiv.expectation_image_two)
async def get_image_two(message: types.Message, state: FSMContext, bot: Bot):
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    image_path = f"{photo.file_id}.jpg"
    await bot.download_file(file_info.file_path, image_path)

    await state.update_data(two_foto=image_path)
    data = await state.get_data()
    one_foto = data.get("one_foto")
    two_foto = data.get("two_foto")

    def tensor_to_image(tensor):
        tensor = tensor * 255
        tensor = np.array(tensor, dtype=np.uint8)
        if np.ndim(tensor) > 3:
            assert tensor.shape[0] == 1
            tensor = tensor[0]
        return PIL.Image.fromarray(tensor)

    def save_image(tensor, path):
        tensor = tensor * 255
        tensor = np.array(tensor, dtype=np.uint8)
        if np.ndim(tensor) > 3:
            assert tensor.shape[0] == 1
            tensor = tensor[0]
        image = PIL.Image.fromarray(tensor)
        image.save(path + '.jpg')

    content_path = one_foto
    style_path = two_foto

    def load_img(path_to_img):
        max_dim = 512
        img = tf.io.read_file(path_to_img)
        img = tf.image.decode_image(img, channels=3)
        img = tf.image.convert_image_dtype(img, tf.float32)

        shape = tf.cast(tf.shape(img)[:-1], tf.float32)
        long_dim = max(shape)
        scale = max_dim / long_dim

        new_shape = tf.cast(shape * scale, tf.int32)

        img = tf.image.resize(img, new_shape)
        img = img[tf.newaxis, :]
        return img

    def imshow(image, title=None):
        if len(image.shape) > 3:
            image = tf.squeeze(image, axis=0)

        plt.imshow(image)
        if title:
            plt.title(title)

    import matplotlib.pyplot as plt
    import matplotlib as mpl

    content_image = load_img(content_path)
    style_image = load_img(style_path)

    plt.subplot(1, 2, 1)
    imshow(content_image, 'Content Image')

    plt.subplot(1, 2, 2)
    imshow(style_image, 'Style Image')

    import tensorflow_hub as hub
    hub_model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
    stylized_image = hub_model(tf.constant(content_image), tf.constant(style_image))[0]
    save_image(stylized_image, "image")
    tensor_to_image(stylized_image)
    image_from_pc = FSInputFile("image.jpg")
    await message.answer_photo(image_from_pc, caption="Результат слияния ваших фото")

