import asyncio
import logging.config
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.types import BotCommand

from basic_handlers import router as base_router
from errors_handler import router as errors_router
from middlewares.updates_dumper_middleware import UpdatesDumperMiddleware
from settings import get_logging_config, get_settings


async def set_bot_commands(bot: Bot) -> None:
    default_commands = [BotCommand(command="/start", description="Начать заново")]

    await bot.set_my_commands(default_commands)


async def main():
    logs_directory = Path("logs")
    logs_directory.mkdir(parents=True, exist_ok=True)
    logging_config = get_logging_config("bot")
    logging.config.dictConfig(logging_config)
    settings = get_settings()
    bot = Bot(
        token=settings.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    logging.info("bot started")
    storage = MemoryStorage()
    dispatcher = Dispatcher(storage=storage, events_isolation=SimpleEventIsolation())
    dispatcher.startup.register(set_bot_commands)
    dispatcher.update.outer_middleware(UpdatesDumperMiddleware())

    # dispatcher.include_routers(base_router, errors_router)

    @dispatcher.message()
    async def global_handler(msg: types.Message):
        await msg.answer("Приём заявок окончен.\nСпасибо за участие!")

    @dispatcher.callback_query()
    async def global_handler(msg: types.CallbackQuery):
        await msg.message.answer("Приём заявок окончен.\nСпасибо за участие!")

    await dispatcher.start_polling(bot)


def run_main():
    asyncio.run(main())


if __name__ == "__main__":
    run_main()
