"""
Модели данных для работы с базой.
Определяют структуру таблиц и объектное представление записей.
"""

from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """Модель пользователя."""
    id: Optional[int]
    username: str
    created_at: datetime
    
    def __init__(self, username: str, user_id: Optional[int] = None, created_at: Optional[datetime] = None):
        self.id = user_id
        self.username = username
        self.created_at = created_at or datetime.now()
    
    @classmethod
    def from_db_row(cls, row):
        """Создаёт объект User из строки SQLite."""
        return cls(
            user_id=row[0],
            username=row[1],
            created_at=datetime.fromisoformat(row[2]) if isinstance(row[2], str) else row[2]
        )


@dataclass
class GameSession:
    """Модель игровой сессии."""
    id: Optional[int]
    user_id: int
    game_type: str      # 'match_pairs', 'sequence', 'digits'
    score: int
    level: int          # уровень сложности (1-3)
    duration: int       # время в секундах
    played_at: datetime
    
    def __init__(self, user_id: int, game_type: str, score: int, level: int, duration: int,
                 session_id: Optional[int] = None, played_at: Optional[datetime] = None):
        self.id = session_id
        self.user_id = user_id
        self.game_type = game_type
        self.score = score
        self.level = level
        self.duration = duration
        self.played_at = played_at or datetime.now()
    
    @classmethod
    def from_db_row(cls, row):
        """Создаёт объект GameSession из строки SQLite."""
        return cls(
            session_id=row[0],
            user_id=row[1],
            game_type=row[2],
            score=row[3],
            level=row[4],
            duration=row[5],
            played_at=datetime.fromisoformat(row[6]) if isinstance(row[6], str) else row[6]
        )
