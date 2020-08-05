from contextlib import contextmanager
from flask import appcontext_pushed, g
import pytest

import app
import db


@contextmanager
def conexao_precarregada(app, conn):
    def handler(_sender, **kwargs):
        g.conexao = conn
    with appcontext_pushed.connected_to(handler, app):
        yield


@pytest.fixture
def conn():
    try:
        conexao = db.abrir_conexao()
        yield conexao
    finally:
        conexao.close()


@pytest.fixture
def client(conn):
    app.app.config['TESTING'] = True
    with conexao_precarregada(app.app, conn):
        with app.app.test_client() as client:
            yield client
