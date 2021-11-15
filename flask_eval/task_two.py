import json
from pathlib import Path

from flask import (Blueprint, flash, g, request, render_template,
                   abort, Markup, redirect, url_for, jsonify)

from flask_eval.db import get_db

STOCKS_PATH = "data/stocks/stocks.json"
VALID_RATINGS = ["rating-none", "rating-1", "rating-2", "rating-3", "rating-4", 
                 "rating-5"]
VALID_OPTIONAL = ["optional-reason-1", "optional-reason-2", "optional-reason-3",
                  "optional-reason-4", "optional-reason-5"]
bp = Blueprint('task_two', __name__, url_prefix='/task-two')


def read_json_file(path, keys=None):
    with open(path, "r") as fp:
        if keys is None:
            return json.load(fp)
        else:
            return {k:v for k,v in json.load(fp).items()
                    if k in keys}


@bp.route("/")
@bp.route("/stock/")
@bp.route("/stock/<ticker_symbol>", methods=["GET", "POST"])
def get_stock(stocks_file=Path(STOCKS_PATH), ticker_symbol=None):

    # Reading in stocks
    stocks_dict = read_json_file(stocks_file)
    # stocks_list = sorted(stocks_dict.values(), key=lambda x: x["ticker_symbol"])
    
    # Setting eval counts to zero
    for _, stock in stocks_dict.items():
        stock["count"] = 0

    # Fetching rating counts
    db = get_db()
    res = db.execute('SELECT ticker_symbol, Count(rating) AS count FROM stock_evals GROUP BY ticker_symbol').fetchall()
    for row in res:
        id = row["ticker_symbol"]
        stocks_dict[id]["count"] = row["count"]
    stocks_list = sorted(stocks_dict.values(), key=lambda x: x["count"], reverse=False)

    if request.method == "GET":
        if ticker_symbol == None:
            stock = stocks_list[0]
            print(stock.keys())
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
            try:
                db.execute("INSERT INTO stock_evals (ticker_symbol, rating, optional_reasons) VALUES (?, ?, ?)",
                           (ticker_symbol, rating, str(optional_reasons)))
                db.commit()
                res = db.execute('SELECT ticker_symbol, Count(rating) AS count FROM stock_evals GROUP BY ticker_symbol').fetchall()
                for row in res:
                    id = row["ticker_symbol"]
                    stocks_dict[id]["count"] = row["count"]
                stocks_list = sorted(stocks_dict.values(), key=lambda x: x["count"], reverse=False)
            except db.IntegrityError as error:
                flash(error)
            else:
                redirect_to = stocks_list[0]["ticker_symbol"]
                return json.dumps(dict(success=True, redirect_to=redirect_to)), 200, {'ContentType':'application/json'}