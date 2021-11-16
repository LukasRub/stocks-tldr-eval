import json
from pathlib import Path

from flask import (Blueprint, flash, g, request, render_template,
                   abort, Markup, redirect, url_for, jsonify, current_app)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from .models import ArticleEval


ARTICLE_DIR = "data/articles"
VALID_RATINGS = ["rating-1", "rating-2", "rating-3", "rating-4", "rating-5"]
VALID_OPTIONAL = ["optional-reason-1", "optional-reason-2", "optional-reason-3",
                  "optional-reason-4", "optional-reason-5", "optional-reason-6"]


bp = Blueprint('task_one', __name__, url_prefix='/task-one')
app = current_app



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


def fetching_eval_counts():
    with app.app_context():
        evaluations = (ArticleEval
                        .query
                        .with_entities(ArticleEval.doc_id, 
                                       func.count(ArticleEval.doc_id))
                        .group_by(ArticleEval.doc_id)
                        .all())
        return evaluations


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
    # db = SQLAlchemy(current_app)
    for (doc_id_, count) in fetching_eval_counts():
        articles_dict[doc_id_]["count"] = count
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
            with app.app_context():
                evaluation = ArticleEval(doc_id=doc_id, rating=rating, 
                                         optional_reasons=str(optional_reasons))
                db.session.add(evaluation)
                db.session.commit()

            # Fetching rating counts
            for (doc_id_, count) in fetching_eval_counts(db):
                articles_dict[doc_id_]["count"] = count
            articles_list = sorted(articles_dict.values(), key=lambda x: x["count"])  

            redirect_to = articles_list[0]["doc_id"]
            return json.dumps(dict(success=True, redirect_to=redirect_to)), 200, {'ContentType':'application/json'}