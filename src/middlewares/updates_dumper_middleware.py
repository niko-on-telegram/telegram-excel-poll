import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.types import TelegramObject


class UpdatesDumperMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        json_event = event.model_dump_json(exclude_unset=True)

        res = await handler(event, data)
        if res is UNHANDLED:
            logging.warning("Unhandled: %s", str(json_event))
        else:
            logging.debug(json_event)
        return res
