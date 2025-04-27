from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile


router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):