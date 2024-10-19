import unittest
from os import getenv
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import UUID, uuid4

import asserts
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

from database import Database
from main import app, game_repo, get_games_repo, player_repo
from model import Game, Player
from repositories import GameRepository, PlayerRepository
from repositories.player import PlayerRepository

client = TestClient(app)


class TestGameExits(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.dbs = Database().session()
        self.games_repo = GameRepository(self.dbs)
        self.player_repo = PlayerRepository(self.dbs)
        self.host = Player(name="Ely")
        self.player_repo.save(self.host)

        self.players = [
            Player(name="Lou"),
            Player(name="Lou^2"),
            Player(name="Andy"),
        ]
        for p in self.players:
            self.player_repo.save(p)

        self.game = Game(
            id=1,
            name="Game of Falls",
            current_player_turn=0,
            max_players=4,
            min_players=2,
            started=False,
            players=[],
            host=self.host,
            host_id=self.host.id,
        )
        self.games_repo.save(self.game)

    def tearDown(self):
        self.dbs.query(Game).delete()
        self.dbs.query(Player).delete()
        self.dbs.commit()
        self.dbs.close()

    def test_deal_cards(self):
        with patch("main.game_repo", self.games_repo), patch(
            "main.player_repo", self.player_repo
        ):
            player1 = self.players[0]
            player2 = self.players[1]
            id0 = self.players[0].id
            id1 = self.players[1].id

            self.game.add_player(player1)
            self.game.add_player(player2)
            self.game.player_info[id0].hand_fig = [1]
            self.game.player_info[id1].hand_fig = [2, 3, 4]

            with client.websocket_connect(f"/ws/lobby/{self.game.id}/figs") as websocket:
                websocket.send_json({"receive": "cards"})
                rsp = websocket.receive_json()

                

            rsp = self.client.post(
                f"/api/lobby/{self.game.id}/deal_cards",
                json={"identifier": str(self.game.host.identifier)},
            )
            self.assertEqual(rsp.status_code, 200)
            
"""
    def test_exit_invalid_game(self):
        with patch("main.game_repo", self.games_repo), patch(
            "main.player_repo", self.player_repo
        ):
            rsp = self.client.post(
                f"/api/lobby/777/exit",
                json={"identifier": str(self.game.host.identifier)},
            )
            self.assertEqual(rsp.status_code, 404)

"""
