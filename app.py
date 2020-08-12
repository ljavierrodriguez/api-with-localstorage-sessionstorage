import datetime
from flask import Flask, request, jsonify, render_template
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from models import db, Role, User

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['ENV'] = "development"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['JWT_SECRET_KEY'] = "super-secret"

db.init_app(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
Migrate(app, db)
CORS(app)
manager = Manager(app)
manager.add_command("db", MigrateCommand)


@app.route("/")
def main():
    return render_template('index.html')

@app.route("/api/login", methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.json.get("username", None)
        password = request.json.get("password", None)

        if not username:
            return jsonify({"msg": "Username is required"}), 400
        if not password:
            return jsonify({"msg": "Password is required"}), 400

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"msg": "Username/Password are incorrect"}), 400

        if not bcrypt.check_password_hash(user.password, password):
            return jsonify({"msg": "Username/Password are incorrect"}), 400

        expires = datetime.timedelta(days=3)
        data = {
            "access_token": create_access_token(identity=username, expires_delta=expires),
            "user": user.serialize()
        }

        return jsonify(data), 200


@manager.command
def load_roles():

    role = Role()
    role.name = "Client"
    role.save()

    print("Roles loaded")


@manager.command
def create_user():
    print("Creando un usuario")
    username = input("Ingrese username: \n")
    password = input("Ingrese password: \n")

    user = User()
    user.username = username
    user.password = bcrypt.generate_password_hash(password)
    user.role_id = 2
    user.save()

    if user.id > 0:
        print("Usuario created")
    else:
        print("Error")


if __name__ == "__main__":
    manager.run()