#!/usr/bin/env python3
"""Простой инспектор базы данных для проверки содержимого."""

from modules.database.db_manager import DatabaseManager


def dump_db(db_path='data/users.db'):
    db = DatabaseManager(db_path)

    print('=== USERS ===')
    users = db.get_all_users()
    if not users:
        print('(пользователи отсутствуют)')
    for u in users:
        print(f'id={u.id}, username={u.username}, created_at={u.created_at}')

    print('\n=== GAME SESSIONS ===')
    if users:
        for u in users:
            history = db.get_game_history(u.id, limit=100)
            if not history:
                print(f'user={u.username} (id={u.id}): нет сессий')
                continue
            for s in history:
                print(f'user={u.username} id={u.id}, session_id={s.id}, game_type={s.game_type}, score={s.score}, level={s.level}, duration={s.duration}, played_at={s.played_at}')
    else:
        print('(сессии отсутствуют, потому что нет пользователей)')

    print('\n=== LEADERBOARD (всех игр) ===')
    for row in db.get_leaderboard(limit=20):
        print(row)


if __name__ == '__main__':
    dump_db()
