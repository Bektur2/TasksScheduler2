import sqlite3



db = "tasks.db"


def init_db():

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