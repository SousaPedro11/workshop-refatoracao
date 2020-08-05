from test.conftest import client
from util import __genUUID__


def test_lance_valido(client):
    resp = client.post(
        '/leiloes/1/lances/',
        json={'valor': 2050},
        headers={'x_id_usuario': __genUUID__()}
    )
    assert resp.status_code == 204
