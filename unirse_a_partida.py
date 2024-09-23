from pydantic import BaseModel
from typing import Optional
from model import Player, Game
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

class req_in(BaseModel):  
    id_game: int
    id_player: int

def unirse_partida(req: req_in, selec_game: Optional[Game], selec_player: Optional[Player]):
    try:
        if selec_player and selec_game is not None:
            selec_game.add_player(selec_player)
        
        return jsonable_encoder(selec_game)
    except TypeError: 
        raise HTTPException(status_code=500, detail="Problemas severos como accediste a una partida no listado completamente creizi")
    #No es posible que el valor de alguno sea None, a menos que hayan errores en la bd 
    #Falta ver si hay internal errors!
 