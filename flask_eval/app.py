import json
from pathlib import Path
from flask import (Flask, request, render_template,
                   abort, Markup, redirect, url_for, jsonify)

ARTICLE_DIR = "data/articles"


app = Flask(__name__)


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


def parse_doc_id(path):
    return path.name.split(".")[0]


def get_rating_numeric(str_value):
    return int(str_value.split("-")[-1])


@app.route("/")
@app.route("/task-one/")
@app.route("/task-one/article/")
@app.route("/task-one/article/<doc_id>", methods=["GET", "POST"])
def get_article(article_dir=str(ARTICLE_DIR), doc_id=None):
    # Sorting out paths
    article_paths = sorted(list(Path(article_dir).glob("*.json")),
                           key=parse_doc_id)
    
    # Reading in articles
    articles = {parse_doc_id(path):read_json_file(path, keys=["title", "summary"]) 
                for path in article_paths}

    # Hadle requests
    if request.method == "GET":
        if doc_id is None:
            article_path = get_article_path(article_paths, doc_id=0)
            article = read_json_file(article_path)
            article["contents"] = [Markup(line) for line in article["contents"]]
            print(article)
            return render_template("article.html.jinja2", articles=articles, article=article)

        elif doc_id in articles.keys():
            article_path = get_article_path(article_paths, doc_id=doc_id)
            article = read_json_file(article_path)
            article["contents"] = [Markup(line) for line in article["contents"]]
            print(article["doc_id"])
            return render_template(f"article.html.jinja2", articles=articles, article=article)
        else:
            abort(404, description="Article not found")

    elif request.method == "POST":
        doc_id = request.json["doc_id"]
        rating = get_rating_numeric(request.json["value"])
        optional_reasons = request.json["optional_reasons"]
        print(doc_id, rating, optional_reasons)
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
        # return redirect(url_for('get_article', doc_id=0))

