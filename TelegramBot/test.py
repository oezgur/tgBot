import logging
import asyncio
import sys
from datetime import datetime
import pyautogui
from io import BytesIO
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, DialogCalendar, DialogCalendarCallback, \
    get_user_locale
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.utils.markdown import hbold

# ENV testtorch

#from config import API_TOKEN
my_locale = 'en_US.utf8'
with open('./.key', 'r') as file:
    API_TOKEN = file.read().strip()


# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


# initialising keyboard, each button will be used to start a calendar with different initial settings
kb = [
    [   # 1 row of buttons for Navigation calendar
        # where user can go to next/previous year/month
        KeyboardButton(text='Navigation Calendar'),
        KeyboardButton(text='Navigation Calendar w month'),
        KeyboardButton(text='Photo'),
    ],
    [   # 2 row of buttons for Dialog calendar
        # where user selects year first, then month, then day
        KeyboardButton(text='Dialog Calendar'),
        KeyboardButton(text='Dialog Calendar w year'),
        KeyboardButton(text='Dialog Calendar w month'),
    ],
]
start_kb = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


# when user sends `/start` command, answering with inline calendar
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
        #This handler receives messages with `/start` command """"""
    
    await message.reply(f"Hello, {hbold(message.from_user.full_name)}! Pick a calendar", reply_markup=start_kb)


# default way of displaying a selector to user - date set for today
@dp.message(F.text.lower() == 'navigation calendar')
async def nav_cal_handler(message: Message):
    await message.answer(
        "Please select a date: ",
        reply_markup=await SimpleCalendar(locale=my_locale).start_calendar()
    )

@dp.message(F.text.lower() == 'photo')
async def anan(message: Message):
    screenshot = pyautogui.screenshot()
    bio = BytesIO()
    screenshot.save(bio, format='PNG')
    bio.seek(0)
    await bot.send_photo(chat_id=message.chat.id, photo=bio)

    
# can be launched at specific year and month with allowed dates range
@dp.message(F.text.lower() == 'navigation calendar w month')
async def nav_cal_handler_date(message: Message):
    calendar = SimpleCalendar(
        locale=my_locale, show_alerts=True
    )
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    await message.answer(
        "Calendar opened on feb 2023. Please select a date: ",
        reply_markup=await calendar.start_calendar(year=2023, month=2)
    )


# simple calendar usage - filtering callbacks of calendar format
@dp.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData):
    calendar = SimpleCalendar(
        locale=my_locale, show_alerts=True
    )
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'You selected {date.strftime("%d/%m/%Y")}',
            reply_markup=start_kb
        )


@dp.message(F.text.lower() == 'dialog calendar')
async def dialog_cal_handler(message: Message):
    await message.answer(
        "Please select a date: ",
        reply_markup=await DialogCalendar(
            locale=my_locale
        ).start_calendar()
    )


# starting calendar with year 1989
@dp.message(F.text.lower() == 'dialog calendar w year')
async def dialog_cal_handler_year(message: Message):
    await message.answer(
        "Calendar opened years selection around 1989. Please select a date: ",
        reply_markup=await DialogCalendar(
            locale=my_locale
        ).start_calendar(1989)
    )


# starting dialog calendar with year 1989 & month
@dp.message(F.text.lower() == 'dialog calendar w month')
async def dialog_cal_handler_month(message: Message):
    await message.answer(
        "Calendar opened on sep 1989. Please select a date: ",
        reply_markup=await DialogCalendar(
            locale=my_locale
        ).start_calendar(year=1989, month=9)
    )


# dialog calendar usage
@dp.callback_query(DialogCalendarCallback.filter())
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: CallbackData):
    selected, date = await DialogCalendar(
        locale=my_locale
    ).process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'You selected {date.strftime("%d/%m/%Y")}',
            reply_markup=start_kb
        )


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
