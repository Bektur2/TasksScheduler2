from db import init_db, add_task



def main():
    init_db()

    model = input("что сделать: ")
    date = input("дата: ")
    start = input("время начала: ")
    end = input("время конца: ")
    timezone = input("часовой пояс: ")

    add_task(
        model,
        date,
        start,
        end,
        timezone
    )


    print("база готова")










if __name__ == "__main__":
    main()