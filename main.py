from flask import Flask, render_template, request, make_response, redirect, url_for
from sqlalchemy_pagination import paginate
#from datetime import datetime
import uuid
import hashlib
from modelos import User, db, Mensagem, utilizador_reg

 
app = Flask(__name__)


db.create_all()



@app.route("/")
def index():
    user = utilizador_reg()
    
    return render_template("index.html", user=user)


   
@app.route("/mural/", methods=["GET"])
def mural():
    user = utilizador_reg()

    page = request.args.get("page")

    if not page:
        page=1

    mensagem_filtrada = db.query(Mensagem)

    mensagem = paginate(query=mensagem_filtrada, page=int(page), page_size=5)

    return render_template("mural.html", mensagem=mensagem, user=user)

@app.route("/add-message", methods=["POST"])
def add_message():
    user = utilizador_reg()

    utilizador = user.nome
    texto = request.form.get("texto")

    mensagem = Mensagem(utilizador=utilizador, texto=texto)
    mensagem.save()

    return redirect("/mural")

@app.route("/registo/", methods=["GET", "POST"])
def registo():
    if request.method == "GET":
        return render_template("registo.html")

    else:
        utilizador = request.form.get("utilizador")
        email = request.form.get("email")
        password = request.form.get("password_user")

        # hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = db.query(User).filter_by(email=email).first()

        if not user:
        # create a User object
            user = User(nome=utilizador, email=email, password=hashed_password, activo = True)

        # save the user object into a database
        user.save()

        if hashed_password != user.password:
            return "WRONG PASSWORD! Go back and try again."

        elif hashed_password == user.password:
            # create a random session token for this user
            session_token = str(uuid.uuid4())

            # save the session token in a database
            user.session_token = session_token
            user.save()
            
            # save user's email into a cookie
            response = make_response(redirect(url_for("index")))
            response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

            return response

@app.route("/profile/", methods=["GET"])
def profile():
    user = utilizador_reg()

    if user:
        return render_template("profile.html", user=user)
    else:
        return redirect(url_for("/index"))

@app.route("/profile/edit/", methods=["GET", "POST"])
def profile_edit():
    user = utilizador_reg()

    if request.method == "GET":
        if user:  # if user is found
            return render_template("profile_edit.html", user=user)
        else:
            return redirect(url_for("index"))

    elif request.method == "POST":
        utilizador = request.form.get("utilizador")
        email = request.form.get("email")
        password = request.form.get("password_user")

        # hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user.nome = utilizador
        user.email = email
        user.password = hashed_password
        
        # save the user object into a database
        user.save()

        return redirect(url_for("profile"))

@app.route("/profile/delete/", methods=["GET", "POST"])
def profile_delete():
    user = utilizador_reg()

    if request.method == "GET":
        if user:  # if user is found
            return render_template("profile_delete.html", user=user)
        else:
            return redirect(url_for("index"))

    elif request.method == "POST":
        user.activo = False
        user.save()
        return redirect(url_for("index"))

@app.route("/logout/")
def logout():
    response = redirect(url_for("index"))
    response.delete_cookie("session_token")

    return response


@app.route("/utilizadores/", methods=["GET"])
def utilizadores():
    user = utilizador_reg()
    utilizadores = db.query(User).all()

    return render_template("utilizadores.html", utilizadores=utilizadores, user=user)

@app.route("/utilizadores/<user_id>",  methods=["GET"])
def detalhe_utilizador(user_id):
    user = utilizador_reg()
    detalhe = db.query(User).get(int(user_id))

    return render_template("detalhe_utilizador.html", user=user, detalhe=detalhe)

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()  # if you use the port parameter, delete it before deploying to Heroku