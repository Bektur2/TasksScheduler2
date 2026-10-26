import asyncio
import sqlite3

from datetime import datetime
from zoneinfo import ZoneInfo

from db import db


async def scheduler():
    print("диспетчер запущен")



    while True:
        # все сравнения времени делаем в utc
        now = datetime.now(ZoneInfo("UTC"))



        with sqlite3.connect(db) as conn:
            conn.row_factory = sqlite3.Row


            tasks = conn.execute("""
                select *
                from tasks
                where status in ('pending', 'running')
            """).fetchall()




            for task in tasks:
                start = datetime.fromisoformat(task["start_at"])
                end = datetime.fromisoformat(task["end_at"])


                if task["status"] == "pending" and start <= now < end:
                    # меняем статус только если задача всё ещё pending
                    cursor = conn.execute("""
                        update tasks
                        set status = 'running'
                        where id = ?
                        and status = 'pending'
                    """, (task["id"],))
                    # если строка изменилась, значит именно этот цикл запустил задачу
                    if cursor.rowcount == 1:
                        print("задача запущена:", task["id"])



                elif task["status"] == "running" and now >= end:
                    
                    # время задачи закончилось
                    conn.execute("""
                        update tasks
                        set status = 'completed'
                        where id = ?
                    """, (task["id"],))




        # проверяем задачи раз в 3 секунды
        await asyncio.sleep(3)