from os import getenv
from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from database import Database
from repositories import GameRepository
from model import Player, Game

from typing import List
from pydantic import BaseModel, Field
import random

from fastapi.middleware.cors import CORSMiddleware


db_uri = getenv("DB_URI")
if db_uri is not None:
    db = Database(db_uri=db_uri)
else:
    db = Database()
db.create_tables()
app = FastAPI()
game_repo = GameRepository(db.session())

# Agregar el middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Permitir todos los orígenes (puedes restringirlo a dominios específicos)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los encabezados
)


@app.middleware("http")
async def add_game_repo_to_request(request: Request, call_next):
    request.state.game_repo = game_repo
    response = await call_next(request)
    return response


def get_games_repo(request: Request) -> GameRepository:
    return request.state.game_repo


class GameIn(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    max_players: int = Field(ge=2, le=4)
    min_players: int = Field(ge=2, le=4)


class PlayerOut(BaseModel):
    name: str


class GameOut(BaseModel):
    name: str
    max_players: int
    min_players: int
    started: bool
    players: List[PlayerOut]


@app.post("/api/lobby", response_model=GameOut)
async def create_game(
    game_create: GameIn, game_repo: GameRepository = Depends(get_games_repo)
) -> GameOut:

    if game_create.min_players > game_create.max_players:
        raise HTTPException(
            status_code=412,
            detail="El número mínimo de jugadores no puede ser mayor al máximo",
        )

    new_game = Game(
        name=game_create.name,
        max_players=game_create.max_players,
        min_players=game_create.min_players,
        started=False,
    )

    game_repo.save(new_game)

    players_out = [PlayerOut(name=player.name) for player in new_game.players]

    return GameOut(
        name=new_game.name,
        max_players=new_game.max_players,
        min_players=new_game.min_players,
        started=new_game.started,
        players=players_out,
    )
