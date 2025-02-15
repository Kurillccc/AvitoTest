from flask import Flask
from app.routes import bp
from app.extensions import db, jwt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:newpassword@localhost:5432/kurillccc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "your_jwt_secret_key"

db.init_app(app)
jwt.init_app(app)

app.register_blueprint(bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
