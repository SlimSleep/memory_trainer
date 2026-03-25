"""
Менеджер базы данных SQLite.
Обеспечивает CRUD операции для пользователей и статистики.
"""

import sqlite3
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import User, GameSession


class DatabaseManager:
    """
    Singleton-менеджер для работы с SQLite.
    Автоматически создаёт таблицы при первом подключении.
    """
    
    _instance = None
    
    def __new__(cls, db_path: str = "data/users.db"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = "data/users.db"):
        if self._initialized:
            return
        
        self.db_path = db_path
        self._ensure_db_directory()
        self._connection = None
        self._init_tables()
        self._initialized = True
    
    def _ensure_db_directory(self):
        """Создаёт директорию для БД, если её нет."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def _get_connection(self):
        """Возвращает соединение с БД (создаёт при необходимости)."""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def close(self):
        """Закрывает соединение с БД."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def _init_tables(self):
        """Создаёт таблицы, если они не существуют."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Таблица игровых сессий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                game_type TEXT NOT NULL,
                score INTEGER NOT NULL,
                level INTEGER NOT NULL,
                duration INTEGER NOT NULL,
                played_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Индексы для быстрых запросов
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON game_sessions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_game_type ON game_sessions(game_type)')
        
        conn.commit()
    
    # ========== ПОЛЬЗОВАТЕЛИ ==========
    
    def create_user(self, username: str) -> Optional[User]:
        """
        Создаёт нового пользователя.
        Возвращает User с id или None при дубликате имени.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (username, created_at) VALUES (?, ?)",
                (username, datetime.now().isoformat())
            )
            conn.commit()
            user_id = cursor.lastrowid
            return self.get_user_by_id(user_id)
        except sqlite3.IntegrityError:
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Возвращает пользователя по ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row:
            return User(
                user_id=row['id'],
                username=row['username'],
                created_at=datetime.fromisoformat(row['created_at'])
            )
        return None
    
    def get_user_by_name(self, username: str) -> Optional[User]:
        """Возвращает пользователя по имени."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, created_at FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if row:
            return User(
                user_id=row['id'],
                username=row['username'],
                created_at=datetime.fromisoformat(row['created_at'])
            )
        return None
    
    def get_all_users(self) -> List[User]:
        """Возвращает список всех пользователей."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, created_at FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        return [
            User(
                user_id=row['id'],
                username=row['username'],
                created_at=datetime.fromisoformat(row['created_at'])
            )
            for row in rows
        ]
    
    def user_exists(self, username: str) -> bool:
        """Проверяет существование пользователя."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        return cursor.fetchone() is not None
    
    # ========== ИГРОВЫЕ СЕССИИ ==========
    
    def save_game_session(self, session: GameSession) -> int:
        """
        Сохраняет игровую сессию.
        Возвращает ID новой записи.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO game_sessions (user_id, game_type, score, level, duration, played_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session.user_id,
            session.game_type,
            session.score,
            session.level,
            session.duration,
            session.played_at.isoformat()
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Возвращает агрегированную статистику для пользователя.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Общая статистика
        cursor.execute('''
            SELECT 
                COUNT(*) as total_games,
                AVG(score) as avg_score,
                MAX(score) as best_score,
                AVG(duration) as avg_duration
            FROM game_sessions
            WHERE user_id = ?
        ''', (user_id,))
        
        overall = cursor.fetchone()
        
        # Статистика по типам игр
        cursor.execute('''
            SELECT 
                game_type,
                COUNT(*) as games_played,
                AVG(score) as avg_score,
                MAX(score) as best_score
            FROM game_sessions
            WHERE user_id = ?
            GROUP BY game_type
        ''', (user_id,))
        
        by_game = [dict(row) for row in cursor.fetchall()]
        
        # Последние 10 игр
        cursor.execute('''
            SELECT id, game_type, score, level, duration, played_at
            FROM game_sessions
            WHERE user_id = ?
            ORDER BY played_at DESC
            LIMIT 10
        ''', (user_id,))
        
        recent = [
            GameSession(
                session_id=row['id'],
                user_id=user_id,
                game_type=row['game_type'],
                score=row['score'],
                level=row['level'],
                duration=row['duration'],
                played_at=datetime.fromisoformat(row['played_at'])
            )
            for row in cursor.fetchall()
        ]
        
        return {
            'total_games': overall['total_games'] or 0,
            'avg_score': round(overall['avg_score'], 1) if overall['avg_score'] else 0,
            'best_score': overall['best_score'] or 0,
            'avg_duration': round(overall['avg_duration'], 1) if overall['avg_duration'] else 0,
            'by_game': by_game,
            'recent': recent
        }
    
    def get_game_history(self, user_id: int, game_type: Optional[str] = None, limit: int = 20) -> List[GameSession]:
        """
        Возвращает историю игр пользователя.
        Можно фильтровать по типу игры.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if game_type:
            cursor.execute('''
                SELECT id, user_id, game_type, score, level, duration, played_at
                FROM game_sessions
                WHERE user_id = ? AND game_type = ?
                ORDER BY played_at DESC
                LIMIT ?
            ''', (user_id, game_type, limit))
        else:
            cursor.execute('''
                SELECT id, user_id, game_type, score, level, duration, played_at
                FROM game_sessions
                WHERE user_id = ?
                ORDER BY played_at DESC
                LIMIT ?
            ''', (user_id, limit))
        
        return [
            GameSession(
                session_id=row['id'],
                user_id=row['user_id'],
                game_type=row['game_type'],
                score=row['score'],
                level=row['level'],
                duration=row['duration'],
                played_at=datetime.fromisoformat(row['played_at'])
            )
            for row in cursor.fetchall()
        ]
    
    def get_leaderboard(self, game_type: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Возвращает таблицу лидеров.
        Если game_type указан — по конкретной игре, иначе общий рейтинг.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if game_type:
            cursor.execute('''
                SELECT u.username, MAX(gs.score) as best_score, COUNT(gs.id) as games_played
                FROM game_sessions gs
                JOIN users u ON gs.user_id = u.id
                WHERE gs.game_type = ?
                GROUP BY u.id
                ORDER BY best_score DESC, games_played DESC
                LIMIT ?
            ''', (game_type, limit))
        else:
            cursor.execute('''
                SELECT u.username, MAX(gs.score) as best_score, COUNT(gs.id) as games_played
                FROM game_sessions gs
                JOIN users u ON gs.user_id = u.id
                GROUP BY u.id
                ORDER BY best_score DESC, games_played DESC
                LIMIT ?
            ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
