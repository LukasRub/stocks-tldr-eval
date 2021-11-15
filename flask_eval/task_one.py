import json
from pathlib import Path

from flask import (Blueprint, flash, g, request, render_template,
                   abort, Markup, redirect, url_for, jsonify)

from flask_eval.db import get_db


ARTICLE_DIR = "data/articles"
VALID_RATINGS = ["rating-1", "rating-2", "rating-3", "rating-4", "rating-5"]
VALID_OPTIONAL = ["optional-reason-1", "optional-reason-2", "optional-reason-3",
                  "optional-reason-4", "optional-reason-5", "optional-reason-6"]
bp = Blueprint('task_one', __name__, url_prefix='/task-one')


def get_article_path(paths, doc_id):
    for path in paths:
        if path.stem == str(doc_id):
            return path


def read_json_file(path, keys=None):
    with open(path, "r") as fp:
        return json.load(fp)


def get_rating_numeric(str_value):
    return int(str_value.split("-")[-1])


def key(path):
    stem = path.stem
    if stem.startswith("oos"):
        return int(stem[-1])
    else:
        return int(stem)


@bp.route("/")
@bp.route("/article/")
@bp.route("/article/<doc_id>", methods=["GET", "POST"])
def get_article(article_dir=str(ARTICLE_DIR), doc_id=None):
    # Sorting out paths
    article_paths = sorted(list(Path(article_dir).glob("*.json")), key=key)
    
    # Reading in articles
    articles_dict = dict()
    for path in article_paths:
        article = read_json_file(path)
        article["count"] = 0
        articles_dict[str(article["doc_id"])] = article

    # Fetching rating counts
    db = get_db()
    res = db.execute('SELECT doc_id, Count(rating) AS count FROM article_evals GROUP BY doc_id').fetchall()
    for row in res:
        id = row["doc_id"]
        articles_dict[id]["count"] = row["count"]
    articles_list = sorted(articles_dict.values(), key=lambda x: x["count"])

    # Handle requests
    if request.method == "GET":
        if doc_id is None:
            article = articles_list[0]
            article["contents"] = [Markup(line) for line in article["contents"]]
            return render_template("article.html.jinja2", articles=articles_list, article=article)

        elif doc_id in articles_dict.keys():
            article_path = get_article_path(article_paths, doc_id=doc_id)
            article = read_json_file(article_path)
            article["contents"] = [Markup(line) for line in article["contents"]]
            return render_template(f"article.html.jinja2", articles=articles_list, article=article)
        else:
            abort(404, description="Article not found")

    elif request.method == "POST":
        doc_id = request.json["doc_id"]
        rating = request.json["value"]
        optional_reasons = [reason for reason in request.json["optional_reasons"] 
                            if reason in VALID_OPTIONAL]
        
        if str(doc_id) in articles_dict.keys() and rating in VALID_RATINGS:
            try:
                db.execute("INSERT INTO article_evals (doc_id, rating, optional_reasons) VALUES (?, ?, ?)",
                           (doc_id, rating, str(optional_reasons)))
                db.commit()
                res = db.execute("SELECT doc_id, Count(rating) AS count FROM article_evals GROUP BY doc_id").fetchall()
                for row in res:
                    id = row["doc_id"]
                    articles_dict[id]["count"] = row["count"]
                articles_list = sorted(articles_dict.values(), key=lambda x: x["count"])
            except db.IntegrityError as error:
                flash(error)
            else:
                redirect_to = articles_list[0]["doc_id"]
                return json.dumps(dict(success=True, redirect_to=redirect_to)), 200, {'ContentType':'application/json'} 
