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
    optional_reason = db.Column(db.String())

    # def __init__(self, doc_id, rating, optional_reason):
    #     self.doc_id = doc_id
    #     self.rating = rating
    #     self.optional_reason = optional_reason

    def __repr__(self):
        return ("<Article_rating(id='{}', doc_id='{}', rating='{}')>"
                    .format(self.id, self.doc_id, self.rating))


class StockEval(db.Model):
    __tablename__ = "stock_evals"

    id = db.Column(db.Integer, primary_key=True)
    ticker_symbol = db.Column(db.String())
    rating = db.Column(db.String())
    optional_reason = db.Column(db.String())

    # def __init__(self, ticker_symbol, rating, optional_reason):
    #     self.ticker_symbol = doc_id
    #     self.rating = rating
    #     self.optional_reason = optional_reason

    def __repr__(self):
        return ("<Stock_rating(id='{}', ticker_symbol='{}', rating='{}')>"
                    .format(self.id, self.ticker_symbol, self.rating))


if __name__ == "__main__":
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost:5432/evaluations"
    db.create_all()