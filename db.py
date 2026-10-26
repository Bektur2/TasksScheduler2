import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo


db = "tasks.db"


def init_db():
    # создаём таблицу задач, если её ещё нет
    with sqlite3.connect(db) as conn:


        conn.execute("""
            create table if not exists tasks (
                id integer primary key autoincrement,
                model text not null,
                start_at text not null,
                end_at text not null,
                timezone text not null,
                status text not null default 'pending',
                error_reason text
            )
        """)


def parse_datetime(date_text, time_text, timezone):

    # переводим введённую дату и время в datetime с часовым поясом
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)



    if time_text.isdigit():
        time_text = f"{time_text}:00"


    day, month = map(int, date_text.split("."))
    hour, minute = map(int, time_text.split(":"))



    result = datetime(
        year=now.year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        tzinfo=tz
    )



    if result < now:
        result = result.replace(year=now.year + 1)



    return result



def add_task(model, date_text, start_text, end_text, timezone):

    start = parse_datetime(date_text, start_text, timezone)
    end = parse_datetime(date_text, end_text, timezone)



    if end <= start:
        raise ValueError("конец должен быть позже начала")
    

    # внутри базы храним время в utc
    start_utc = start.astimezone(ZoneInfo("UTC"))
    end_utc = end.astimezone(ZoneInfo("UTC"))



    with sqlite3.connect(db) as conn:

        conn.execute("""
            insert into tasks (
                model,
                start_at,
                end_at,
                timezone
            )
            values (?, ?, ?, ?)
        """, (
            model,
            start_utc.isoformat(),
            end_utc.isoformat(),
            timezone
        ))