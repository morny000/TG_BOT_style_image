from aiogram.fsm.state import StatesGroup, State

class Aktiv(StatesGroup):
    start_state = State()
    expectation_image_one = State()
    expectation_image_two = State()
    ready_image = State()
