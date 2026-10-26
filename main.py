from db import init_db, add_task, get_tasks
from datetime import datetime
from zoneinfo import ZoneInfo
from tzlocal import get_localzone_name

import asyncio

from scheduler import scheduler


def main():

    init_db()



    while True:
        print()
        print("1. добавить задачу")
        print("2. список задач")
        print("3. запустить диспетчера")
        print("0. выход")


        choice = input("> ").strip()


        if choice == "1":
            try:
                create_task()
            except Exception as error:
                print("ошибка:", error)



        elif choice == "2":
            show_tasks()
        
        elif choice == "3":
            try:
                asyncio.run(scheduler())

            except KeyboardInterrupt:
                print("\nдиспетчер остановлен")

        elif choice == "0":
            break

        else:
            print("неизвестная команда")







def show_tasks():

    tasks = get_tasks()


    if not tasks:
        print("задач нет")
        return




    for task in tasks:

        timezone = ZoneInfo(task["timezone"])


        # переводим utc обратно в часовой пояс клиента
        start = datetime.fromisoformat(
            task["start_at"]
        ).astimezone(timezone)

        end = datetime.fromisoformat(
            task["end_at"]
        ).astimezone(timezone)


        print(
            f"{task['id']} | "
            f"{task['model']} | "
            f"{start:%d.%m %H:%M} - {end:%H:%M} | "
            f"{task['timezone']} | "
            f"{task['status']}"
        )

        if task["error_reason"]:
            print("ошибка:", task["error_reason"])







def create_task():


    model = input("что сделать: ").strip()
    date = input("дата, например 28.10: ").strip()
    start = input("время начала: ").strip()
    end = input("время конца: ").strip()


    print()
    print("1. ввести часовой пояс")
    print("2. взять из системы")


    choice = input("> ").strip()


    if choice == "1":
        timezone = input(
            "часовой пояс, например Europe/Moscow: "
        ).strip()


    elif choice == "2":
        timezone = get_localzone_name()
        print("используется:", timezone)

    else:
        print("неверный выбор")
        return



    add_task(
        model,
        date,
        start,
        end,
        timezone
    )

    print("задача добавлена")









if __name__ == "__main__":
    main()