from fastapi.testclient import TestClient
import pytest
import asserts
from database import Database
from model import Player
from main import app

client = TestClient(app)

db = Database()
db.create_tables()
Session = db.get_session()


@pytest.fixture
def name_of_player():

    return {"name": "Alice", "identifier": "80b4a5b03b5d46a1b50fb5cb510d4802"}


@pytest.mark.end2end_test
def test_set_name_endpoint(name_of_player):
    response = client.post("/api/name", json={"name": "Alice"})
    player = (
        Session.query(Player)
        .filter_by(identifier="80b4a5b03b5d46a1b50fb5cb510d4802")
        .first()
    )
    assert player is not None
    assert response.status_code == 201
    assert response.json() == name_of_player
