import json
from pathlib import Path

from flask import (Blueprint, flash, g, request, render_template,
                   abort, Markup, redirect, url_for, jsonify, current_app)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from .models import StockEval, db


STOCKS_PATH = "data/stocks/stocks.json"
VALID_RATINGS = ["rating-none", "rating-1", "rating-2", "rating-3", "rating-4", 
                 "rating-5"]
VALID_OPTIONAL = ["optional-reason-1", "optional-reason-2", "optional-reason-3",
                  "optional-reason-4", "optional-reason-5"]

bp = Blueprint('task_two', __name__, url_prefix='/task-two')
app = current_app


def read_json_file(path, keys=None):
    with open(path, "r") as fp:
        if keys is None:
            return json.load(fp)
        else:
            return {k:v for k,v in json.load(fp).items()
                    if k in keys}


def fetching_eval_counts():
    with app.app_context():
        evaluations = (StockEval
                        .query
                        .with_entities(StockEval.ticker_symbol, 
                                       func.count(StockEval.ticker_symbol))
                        .group_by(StockEval.ticker_symbol)
                        .all())
        return evaluations


@bp.route("/")
@bp.route("/stock/")
@bp.route("/stock/<ticker_symbol>", methods=["GET", "POST"])
def get_stock(stocks_file=Path(STOCKS_PATH), ticker_symbol=None):

    # Reading in stocks
    stocks_dict = read_json_file(stocks_file)
    
    # Setting eval counts to zero
    for _, stock in stocks_dict.items():
        stock["count"] = 0

    # Fetching rating counts
    for (ticker_symbol_, count) in fetching_eval_counts(db):
        stocks_dict[ticker_symbol_]["count"] = count
    stocks_list = sorted(stocks_dict.values(), key=lambda x: x["count"])

    if request.method == "GET":
        if ticker_symbol == None:
            stock = stocks_list[0]
            return render_template("stock.html.jinja2", stocks=stocks_list, stock=stock)
        elif ticker_symbol in stocks_dict.keys():
            stock = stocks_dict[ticker_symbol]
            return render_template("stock.html.jinja2", stocks=stocks_list, stock=stock)
        else:
            abort(404, description="Article not found")

    elif request.method == "POST":
        ticker_symbol = request.json["ticker_symbol"]
        rating = request.json["value"]
        optional_reasons = [reason for reason in request.json["optional_reasons"] 
                            if reason in VALID_OPTIONAL]
        if str(ticker_symbol) in stocks_dict.keys() and rating in VALID_RATINGS:
            with app.app_context():
                evaluation = StockEval(ticker_symbol=ticker_symbol, rating=rating, 
                                       optional_reasons=str(optional_reasons))
                db.session.add(evaluation)
                db.session.commit()
            
            # Fetching rating counts
            for (ticker_symbol_, count) in fetching_eval_counts(db):
                stocks_dict[ticker_symbol_]["count"] = count
            stocks_list = sorted(stocks_dict.values(), key=lambda x: x["count"])

            redirect_to = stocks_list[0]["ticker_symbol"]
            return json.dumps(dict(success=True, redirect_to=redirect_to)), 200, {'ContentType':'application/json'}