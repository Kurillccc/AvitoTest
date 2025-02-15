from app.extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Integer, default=1000)

    def __repr__(self):
        return f'<User {self.username}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_transactions')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_transactions')

    def __repr__(self):
        return f'<Transaction from {self.sender_id} to {self.receiver_id}, Amount: {self.amount}>'

class Merch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Merch {self.name}, Price: {self.price}>'

def seed_merch():
    merch_items = [
        {"name": "t-shirt", "price": 80},
        {"name": "cup", "price": 20},
        {"name": "book", "price": 50},
        {"name": "pen", "price": 10},
        {"name": "powerbank", "price": 200},
        {"name": "hoody", "price": 300},
        {"name": "umbrella", "price": 200},
        {"name": "socks", "price": 10},
        {"name": "wallet", "price": 50},
        {"name": "pink-hoody", "price": 500}
    ]

    for item in merch_items:
        if not Merch.query.filter_by(name=item["name"]).first():
            db.session.add(Merch(name=item["name"], price=item["price"]))

    db.session.commit()