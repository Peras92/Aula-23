import os
from sqla_wrapper import SQLAlchemy
from flask import request

db_url = os.getenv("DATABASE_URL", "sqlite:///db.sqlite").replace("postgres://", "postgresql://", 1)
db = SQLAlchemy(db_url)

# cria objecto user, que é guardado na BD
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    session_token = db.Column(db.String)
    activo = db.Column(db.Boolean, default = True)

class Mensagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utilizador = db.Column(db.String, unique=False)
    texto = db.Column(db.String, unique=False)

#função para validar se o utilizar está logado
def utilizador_reg():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token, activo=True).first()
    else:
        user = None
    return user