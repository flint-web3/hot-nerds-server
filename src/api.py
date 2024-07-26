from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .storage import UserRepository, QuizRepository, UserScoreRepository

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/user/{account_name}")
async def user_get(account_name: str):
    user_repo = UserRepository()
    user = user_repo.get(account_name)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.model_dump()


@app.post("/user/{account_name}")
async def user_create(account_name: str, request: Request):
    user_repo = UserRepository()

    request_body: Dict[str, Any] = await request.json()
    user = user_repo.get_or_create(account_name, request_body.get("private_key"))
        
    return user.model_dump()


@app.get("/user/{account_name}/join_quiz/{quiz_id}")
async def quiz_join(account_name: str, quiz_id: int):
    user_repo = UserRepository()
    user_score_repo = UserScoreRepository()

    user = user_repo.get(account_name)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_score = user_score_repo.create(user.id, quiz_id)

    return user_score.model_dump()


@app.get("/user/{account_name}/quiz_questions/{quiz_id}")
async def quiz_questions(account_name: str, quiz_id: int):
    user_repo = UserRepository()
    quiz_repo = QuizRepository()

    user = user_repo.get(account_name)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    questions = quiz_repo.get_questions(quiz_id)

    return questions


@app.put("/user/{account_name}/quiz_score/{quiz_id}")
async def quiz_score(account_name: str, quiz_id: int, request: Request):
    request_body: Dict[str, Any] = await request.json()
    user_repo = UserRepository()
    user_score_repo = UserScoreRepository()

    user = user_repo.get(account_name)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_score_repo.update(user.id, quiz_id, score=request_body.get('score', 0))

    return {"status": "ok"}


@app.get("/user/{account_name}/quizzes")
async def quiz_list(account_name: str):
    user_score_repo = UserScoreRepository()
    quiz_repo = QuizRepository()
    user_repo = UserRepository()

    user = user_repo.get(account_name)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_scores = user_score_repo.get_by_user_id(user.id)
    quizzes = quiz_repo.list() # list(map(lambda q: q.model_dump(), ))
    result: List[Dict] = []
    for quiz in quizzes:
        is_participating = list(filter(lambda s: s.quiz_id == quiz.id, user_scores))
        quiz_dict = quiz.model_dump()
        quiz_dict['is_participating'] = bool(is_participating)
        result.append(quiz_dict)
    
    return result


@app.get("/quiz/{quiz_id}/leaderboard")
async def get_leaderboard(quiz_id: int):
    user_score_repo = UserScoreRepository()
    return list(map(lambda q: q.model_dump(), user_score_repo.list(quiz_id)))
