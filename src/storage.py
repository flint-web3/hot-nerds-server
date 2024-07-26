import logging

from contextlib import contextmanager
from typing import Dict, List, Optional
from sqlalchemy import Column, Boolean, ForeignKey, String, Integer, Float, DateTime, create_engine, literal
from sqlalchemy.orm import sessionmaker, declarative_base

from src.settings import get_settings
from src.models import User, Quiz, UserScore

settings = get_settings()
enigne = create_engine(f"sqlite:///{settings.db_name}", echo=True)

Base = declarative_base()
Session = sessionmaker(enigne)

questions = [
    [
        {
            "question": "Какое самое маленькое государство в мире по площади?",
            "answers": ["Ватикан", "Монако", "Сан-Марино", "Лихтенштейн"],
            "correct_answer": 0
        },
        {
            "question": "Какой химический элемент обозначается символом 'O'?",
            "answers": ["Азот", "Водород", "Кислород", "Углерод"],
            "correct_answer": 2
        },
        {
            "question": "Как называется столица Франции?",
            "answers": ["Рим", "Берлин", "Лондон", "Париж"],
            "correct_answer": 3
        },
        {
            "question": "Сколько планет в нашей Солнечной системе?",
            "answers": ["9", "8", "7", "10"],
            "correct_answer": 1
        },
        {
            "question": "Какое животное является символом России?",
            "answers": ["Медведь", "Лев", "Орёл", "Волк"],
            "correct_answer": 0
        },
    ],
    [
        {
            "question": "Кто написал роман 'Война и мир'?",
            "answers": ["Лев Толстой", "Фёдор Достоевский", "Антон Чехов", "Александр Пушкин"],
            "correct_answer": 0
        },
        {
            "question": "Какое самое высокое здание в мире?",
            "answers": ["Бурдж-Халифа", "Эйфелева башня", "Эмпайр-стейт-билдинг", "Токийская телебашня"],
            "correct_answer": 0
        },
        {
            "question": "Какой континент является самым большим по площади?",
            "answers": ["Азия", "Африка", "Северная Америка", "Европа"],
            "correct_answer": 0
        },
        {
            "question": "Как называется столица Японии?",
            "answers": ["Токио", "Пекин", "Сеул", "Бангкок"],
            "correct_answer": 0
        },
        {
            "question": "Какой океан является самым большим?",
            "answers": ["Тихий океан", "Атлантический океан", "Индийский океан", "Северный Ледовитый океан"],
            "correct_answer": 0
        },
    ],
]

class DBAdapter:
    @contextmanager
    def get_session(self):
        try:
            session = Session()
            yield session
        except:
            session.rollback()
            raise
        else:
            session.commit()
        finally:
            session.close()


class DBUser(Base): # type: ignore
    __tablename__ = "user"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    account_name = Column("account_name", String, unique=True)
    private_key = Column("private_key", String, nullable=True)


class DBQuiz(Base): # type: ignore
    __tablename__ = "quiz"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String, nullable=True)
    price = Column("price", Float)
    due = Column("due", DateTime)
    is_finished = Column("is_finished", Boolean, default=False)


class DBUserScore(Base): # type: ignore
    __tablename__ = "user_score"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    score = Column("score", Integer, default=0)
    quiz_id = Column("quiz_id", Integer, ForeignKey("quiz.id"))
    user_id = Column("user_id", Integer, ForeignKey("user.id"))
    shard = Column("shard", String, nullable=True, default=None)


class UserRepository:
    def __init__(self) -> None:
        self._db_adapter = DBAdapter()

    def get_or_create(self, account_name: str, private_key: Optional[str] = None) -> User:
        with self._db_adapter.get_session() as session:
            q = session.query(DBUser).filter_by(account_name=account_name)
            is_user = session.query(literal(True)).filter(q.exists()).scalar()
            if not is_user:
                user = DBUser(account_name=account_name, private_key=private_key)
                session.add(user)

            user = User.model_validate(q.one_or_none().__dict__) # type: ignore
            return user

    def get(self, account_name: str) -> Optional[User]:
        with self._db_adapter.get_session() as session:
            user = session.query(DBUser).filter_by(account_name=account_name).one_or_none()
            if user:
                user = User.model_validate(user.__dict__)
            return user

    def update(self, account_name: str, **kwargs) -> None:
        with self._db_adapter.get_session() as session:
            update_fields = {getattr(DBUser, k): v for k, v in kwargs.items()}
            session.query(DBUser).filter_by(account_name=account_name).update(update_fields)

    def delete(self, account_name: str) -> None:
        with self._db_adapter.get_session() as session:
            session.query(DBUser).filetr_by(account_name=account_name).delete()


class QuizRepository:
    def __init__(self) -> None:
        self._db_adapter = DBAdapter()

    def list(self) -> List[Quiz]:
        with self._db_adapter.get_session() as session:
            quizzes = session.query(DBQuiz).filter_by(is_finished=False).all()
            quizzes = list(map(lambda q: Quiz.model_validate(q.__dict__), quizzes))
            return quizzes
    
    def get_questions(self, quiz_id: int) -> List[Dict]:
        result = questions[quiz_id - 1]
        return result


class UserScoreRepository:
    def __init__(self) -> None:
        self._db_adapter = DBAdapter()

    def get_by_user_id(self, user_id: int) -> List[UserScore]:
        with self._db_adapter.get_session() as session:
            scores = session.query(DBUserScore).filter_by(user_id=user_id).all()
            scores = list(map(lambda q: UserScore.model_validate(q.__dict__), scores))
            return scores

    def create(self, user_id: int, quiz_id: int) -> UserScore:
        with self._db_adapter.get_session() as session:
            q = session.query(DBUserScore).filter_by(user_id=user_id, quiz_id=quiz_id)
            is_score = session.query(literal(True)).filter(q.exists()).scalar()
            if not is_score:
                score = DBUserScore(user_id=user_id, quiz_id=quiz_id)
                logging.info(f"{score}")
                session.add(score)

            score = UserScore.model_validate(q.one_or_none().__dict__) # type: ignore
            return score
    
    def list(self, quiz_id: int) -> List[UserScore]:
        with self._db_adapter.get_session() as session:
            scores = session.query(DBUserScore).filter_by(quiz_id=quiz_id).order_by(DBUserScore.score.desc()).all()
            scores = list(map(lambda q: UserScore.model_validate(q.__dict__), scores))
            return scores

    def update(self, user_id: int, quiz_id: int, **kwargs) -> None:
        with self._db_adapter.get_session() as session:
            update_fields = {getattr(DBUserScore, k): v for k, v in kwargs.items()}
            session.query(DBUserScore).filter_by(user_id=user_id, quiz_id=quiz_id).update(update_fields)

