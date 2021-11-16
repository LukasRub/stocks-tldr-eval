import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext


app = Flask(__name__)
db = SQLAlchemy(app)


class ArticleEval(db.Model):
    __tablename__ = "article_evals"

    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.String())
    rating = db.Column(db.String())
    optional_reasons = db.Column(db.String())

    def __repr__(self):
        return ("<Article_rating(id='{}', doc_id='{}', rating='{}')>"
                    .format(self.id, self.doc_id, self.rating))


class StockEval(db.Model):
    __tablename__ = "stock_evals"

    id = db.Column(db.Integer, primary_key=True)
    ticker_symbol = db.Column(db.String())
    rating = db.Column(db.String())
    optional_reasons = db.Column(db.String())

    def __repr__(self):
        return ("<Stock_rating(id='{}', ticker_symbol='{}', rating='{}')>"
                    .format(self.id, self.ticker_symbol, self.rating))


if __name__ == "__main__":
    app = Flask(__name__)
    db = SQLAlchemy(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://wiruisxmoktlwj:3d4337c024090a3677e6fa43571b041c6d9cd978a3d1d4c43878871534fd9ebe@ec2-54-195-246-55.eu-west-1.compute.amazonaws.com:5432/d3hs5t3ohu0s0g"
    db.create_all()