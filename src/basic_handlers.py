from aiogram import Router, types, F, Bot
from aiogram import md
from aiogram.enums import ChatType, MessageEntityType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from categories import categories
from excel_pusher import put_data_to_excel, DataToPut
from states import States

router = Router()


@router.message(CommandStart(), F.chat.type != ChatType.PRIVATE)
async def start_message_group(message: types.Message) -> None:
    await message.answer("⚠️ The /start command can only be used *in private chats.*")


@router.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def start_message_private(message: types.Message, state: FSMContext) -> None:
    await state.clear()

    btns = [
        [InlineKeyboardButton(text=name, callback_data=str(i))] for i, name in enumerate(categories)
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=btns)

    start_header = f"{md.bold('Выберите категорию:')} \n\n"

    await message.answer(
        text=start_header,
        reply_markup=markup
    )
    await state.set_state(States.SELECTING_CATEGORY)


@router.message(States.SELECTING_CATEGORY)
async def category_error_handle(message: types.Message):
    await message.answer("Выберите категорию нажав на кнопку в чате")


@router.callback_query(States.SELECTING_CATEGORY)
async def category_input(callback: types.CallbackQuery, state: FSMContext):
    category_id = int(callback.data)
    await state.update_data(category_id=category_id)

    await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[[]]))
    await callback.message.edit_text(f"{md.bold('Вы выбрали категорию:')}\n{categories[category_id]}")

    msg = await callback.message.answer("Отправьте имя человека для номинирования")
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(States.ENTERING_NAME)


@router.message(States.ENTERING_NAME)
async def name_input_handler(message: types.Message, state: FSMContext, bot: Bot):
    if not message.text:
        await message.answer("Ввод не распознан, отправьте имя человека текстом")
        return

    await state.update_data(name=message.text)
    data = await state.get_data()

    await bot.edit_message_text(f"{md.bold('Вы номинировали:')}\n{message.text}", chat_id=message.chat.id,
                                message_id=data['last_msg_id'])
    await message.delete()

    msg = await message.answer("Отправьте ссылку на этого человека в любой соцсети")
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(States.ENTERING_LINK)


@router.message(States.ENTERING_LINK)
async def link_input_handler(message: types.Message, state: FSMContext, bot: Bot):
    if not message.entities:
        await message.answer("Ссылка не найдена, попробуйте ещё раз")
        return

    url = None
    for ent in message.entities:
        if ent.type == MessageEntityType.URL:
            url = ent.extract_from(message.text)

    if not url:
        await message.answer("Ссылка не найдена, попробуйте ещё раз")
        return

    await state.update_data(url=url)
    data = await state.get_data()
    await bot.edit_message_text(f"{md.bold('Вы отправили ссылку:')}\n{url}", chat_id=message.chat.id,
                                message_id=data['last_msg_id'])
    await message.delete()

    msg = await message.answer("Напишите, почему вы считаете что данный человек достоин победы в этой номинации?")

    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(States.ENTERING_REASON)


@router.message(States.ENTERING_REASON)
async def reason_input_handler(message: types.Message, state: FSMContext, bot: Bot):
    if not message.text:
        await message.answer(
            "Ввод не распознан, пожалуйста, напишите текстом, почему вы считаете что данный человек достоин "
            "победы в этой номинации?")
        return

    data = await state.get_data()
    data['reason'] = message.text

    await bot.edit_message_text(f"{md.bold('Вы написали:')}\n{message.text}", chat_id=message.chat.id,
                                message_id=data['last_msg_id'])
    await message.delete()

    await state.set_state(None)
    await message.answer("Спасибо за участие в голосовании!")

    data_to_put = DataToPut(**data)
    put_data_to_excel(data_to_put)
