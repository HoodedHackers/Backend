from os import getenv
from fastapi import FastAPI, Response, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from database import Database
from repositories import GameRepository

# from respositories.player import PlayerRepository
from repositories.game import GameRepository

# from pydantic import BaseModel #
from model import Player, Game  #

from typing import List  #
from pydantic import BaseModel  #
import random


db_uri = getenv("DB_URI")
if db_uri is not None:
    db = Database(db_uri=db_uri)
else:
    db = Database()


db.create_tables()
app = FastAPI()
game_repo = GameRepository(db.session())


@app.middleware("http")
async def add_game_repo_to_request(request: Request, call_next):
    request.state.game_repo = game_repo
    response = await call_next(request)
    return response


def get_games_repo(request: Request) -> GameRepository:
    return request.state.game_repo


# endpoing juguete, borralo cuando haya uno de verdad
@app.get("/api/borrame")
async def borrame(games_repo: GameRepository = Depends(get_games_repo)):
    games = games_repo.get_many(10)
    return {"games": games}


class GameIn(BaseModel):  # Heredar de BaseModel
    name: str
    max_players: int
    min_players: int


class GameOut(BaseModel):
    id: int
    name: str
    max_players: int
    min_players: int
    started: bool
    players: List[Player]

    class Config:
        arbitrary_type_allowed = True


@app.post("/api/lobby")
async def create_game(
    game_create: GameIn, game_repo: GameRepository = Depends(get_games_repo)
) -> GameOut:
    if game_create.min_players < 2 or game_create.max_players > 4:
        raise HTTPException(
            status_code=412, detail="El número de jugadores debe ser entre 2 y 4"
        )
    elif game_create.min_players > game_create.max_players:
        raise HTTPException(
            status_code=412,
            detail="El número mínimo de jugadores no puede ser mayor al máximo",
        )
    elif game_create.min_players == game_create.max_players:
        raise HTTPException(
            status_code=412,
            detail="El número mínimo de jugadores no puede ser igual al máximo",
        )
    elif not game_create.name:
        raise HTTPException(
            status_code=412, detail="El nombre de la partida no puede estar vacío"
        )

    nueva_partida = Game(
        name=game_create.name,
        max_players=game_create.max_players,
        min_players=game_create.min_players,
        started=False,
    )

    game_repo.save(nueva_partida)

    return GameOut(
        id=nueva_partida.id,  # no creo que este bien esta parte?
        name=nueva_partida.name,
        max_players=nueva_partida.max_players,
        min_players=nueva_partida.min_players,
        started=nueva_partida.started,
        players=nueva_partida.players,  # tampoco se si esta bien
    )


"""sortear jugadores"""

"""""
class GamePlayerResponse(BaseModel):
    game_id: int
    players: List[Player]


@app.post("/api/start_game", response_model=Game)
async def sortear_jugadores(
    game_id: int, game_repo: GameRepository = Depends(get_games_repo)
):

    game = game_repo.get(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Partida no encontrada")

    if len(game.players) < game.min_players:
        raise HTTPException(
            status_code=412,
            detail="No se puede sortear jugadores si no hay suficientes jugadores",
        )

    random.shuffle(game.players)
    game_repo.save(game)

    return GamePlayerResponse(game_id=game_id, players=game.players)
""" ""
