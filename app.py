from flask import Flask, jsonify, Response, request
from http import HTTPStatus

import db


app = Flask(__name__)


@app.route('/leiloes/<id_leilao>/', methods=['GET'])
def get_detalhes_do_leilao(id_leilao):
    with db.abrir_conexao() as conexao, conexao.cursor() as cur:
        cur.execute("""
      SELECT id, descricao, criador, data, diferenca_minima
      FROM leiloes
      WHERE id = %s
    """, (id_leilao, ))
        leilao = cur.fetchone()
        cur.execute("""
      SELECT id, valor, comprador, data
      FROM lances
      WHERE id_leilao = %s
      ORDER BY data DESC
      LIMIT 1
    """, (id_leilao, ))
        lance = cur.fetchone()
        return jsonify({
            'id': leilao[0],
            'descricao': leilao[1],
            'criador': leilao[2],
            'data': leilao[3].isoformat(),
            'diferenca_minima': leilao[4],
            'ultimo_lance': {
                'id': lance[0],
                'valor': lance[1],
                'comprador': lance[2],
                'data': lance[3].isoformat()
            } if lance is not None else None
        })


@app.route('/leiloes/<id_leilao>/lances/', methods=['POST'])
def registrar_lance(id_leilao):
    dados = request.get_json()
    # simulação meia boca de autenticação
    id_usuario = request.headers['X-Id-Usuario']
    with db.abrir_conexao() as conexao, conexao.cursor() as cur:
        cur.execute("""
      SELECT valor
      FROM lances
      WHERE id_leilao = %s
      ORDER BY data DESC
      LIMIT 1
    """, (id_leilao, ))
        ultimo_lance = cur.fetchone()
        if ultimo_lance is not None and ultimo_lance[0] >= dados['valor']:
            return 'Lance deve ser maior que o último.', HTTPStatus.BAD_REQUEST
        cur.execute("""
      INSERT INTO lances (id_leilao, valor, comprador, data)
      VALUES (%s, %s, %s, now())
    """, (id_leilao, dados['valor'], id_usuario))
    return '', HTTPStatus.NO_CONTENT


@app.route('/leiloes/<id_leilao>/lances/minimo/', methods=['POST'])
def registrar_lance_minimo(id_leilao):
    # simulação meia boca de autenticação
    id_usuario = request.headers['X-Id-Usuario']
    with db.abrir_conexao() as conexao, conexao.cursor() as cur:
        cur.execute("""
      SELECT valor
      FROM lances
      WHERE id_leilao = %s
      ORDER BY data DESC
      LIMIT 1
    """, (id_leilao, ))
        ultimo_lance = cur.fetchone()
        valor = 1 if ultimo_lance is None else ultimo_lance[0] + 1
        cur.execute("""
      INSERT INTO lances (id_leilao, valor, comprador, data)
      VALUES (%s, %s, %s, now())
    """, (id_leilao, valor, id_usuario))
    return '', HTTPStatus.NO_CONTENT


@app.route('/leiloes/proximo/', methods=['GET'])
def get_detalhes_do_proximo_leilao():
    with db.abrir_conexao() as conexao, conexao.cursor() as cur:
        cur.execute("""
      SELECT id, descricao, criador, data, diferenca_minima
      FROM leiloes
      ORDER BY data
      LIMIT 1
    """)
        leilao = cur.fetchone()
        id_leilao = leilao[0]
        cur.execute("""
      SELECT id, valor, comprador, data
      FROM lances
      WHERE id_leilao = %s
      ORDER BY data DESC
      LIMIT 1
    """, (id_leilao, ))
        lance = cur.fetchone()
        return jsonify({
            'id': leilao[0],
            'descricao': leilao[1],
            'criador': leilao[2],
            'data': leilao[3].isoformat(),
            'diferenca_minima': leilao[4],
            'ultimo_lance': {
                'id': lance[0],
                'valor': lance[1],
                'comprador': lance[2],
                'data': lance[3].isoformat()
            } if lance is not None else None
        })
