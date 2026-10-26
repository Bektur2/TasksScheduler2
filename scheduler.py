import asyncio
import sqlite3

import random


from datetime import datetime
from zoneinfo import ZoneInfo

from db import db


proxies = [
    "proxy1",
    "proxy2",
    "proxy3"
]

def run_viewer(model, proxy):

    # имитируем результат запуска просмотрщика
    result = random.choice([
        "ok",
        "captcha",
        "proxy_dead"
    ])


    print(f"{model} | {proxy} | {result}")


    return result





def set_error(task_id, reason):


    with sqlite3.connect(db) as conn:
        conn.execute("""
            update tasks
            set status = 'error',
                error_reason = ?
            where id = ?
        """, (reason, task_id))





async def run_task(task):


    captcha_attempts = 0
    proxy_index = 0


    while True:
        proxy = proxies[proxy_index]

        result = run_viewer(
            task["model"],
            proxy
        )

        if result == "ok":
            print(f"задача {task['id']} запущена")
            return

        if result == "captcha":
            # captcha можно повторить максимум 3 раза
            captcha_attempts += 1

            if captcha_attempts >= 3:
                set_error(
                    task["id"],
                    "captcha: попытки закончились"
                )
                return

            print(
                f"captcha, попытка {captcha_attempts}/3"
            )

            await asyncio.sleep(2)

        elif result == "proxy_dead":
            # если прокси умер, берём следующий
            proxy_index += 1

            if proxy_index >= len(proxies):
                set_error(
                    task["id"],
                    "рабочие прокси закончились"
                )
                return

            print(
                "меняем прокси на",
                proxies[proxy_index]
            )



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