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
        if keys is None:
            return json.load(fp)
        else:
            return {k:v for k,v in json.load(fp).items()
                    if k in keys}



def get_rating_numeric(str_value):
    return int(str_value.split("-")[-1])


@bp.route("/")
@bp.route("/task-one/")
@bp.route("/task-one/article/")
@bp.route("/task-one/article/<doc_id>", methods=["GET", "POST"])
def get_article(article_dir=str(ARTICLE_DIR), doc_id=None):
    # Sorting out paths
    article_paths = list(Path(article_dir).glob("*.json"))
    
    # Reading in articles
    keys = ["doc_id", "title", "summary"]
    articles_list = [read_json_file(path, keys=keys) for path in article_paths]

    # Setting eval counts to zero
    for article in articles_list:
        article["count"] = 0

    # Converting to dict for access by key
    articles_dict = {str(article["doc_id"]):article for article in articles_list}

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
            article_path = get_article_path(article_paths, doc_id=0)
            article = read_json_file(article_path)
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
        
        print(doc_id)
        if str(doc_id) in articles_dict.keys() and rating in VALID_RATINGS:
            try:
                db.execute("INSERT INTO article_evals (doc_id, rating, optional_reasons) VALUES (?, ?, ?)",
                           (doc_id, rating, str(optional_reasons)))
                db.commit()
            except db.IntegrityError as error:
                flash(error)
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
        # return redirect(url_for('get_article', doc_id=0))