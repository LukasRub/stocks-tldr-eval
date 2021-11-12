import json
from pathlib import Path
from flask import Flask, request, render_template, abort, Markup    

ARTICLE_DIR = "data/articles"


app = Flask(__name__)


def read_json_file(path):
    with open(path, "r") as fp:
        return json.load(fp)


def parse_doc_id(path):
    return int(path.name.split(".")[0])


@app.route("/")
@app.route("/task-one/")
@app.route("/task-one/article/")
@app.route("/task-one/article/<int:doc_id>", methods=["GET", "POST"])
def get_article(article_dir=str(ARTICLE_DIR), doc_id=None):
    
    # Sorting out paths
    article_paths = sorted(list(Path(article_dir).glob("*.json")),
                           key=parse_doc_id)
    
    # Reading in articles
    articles = {parse_doc_id(path):read_json_file(path) 
                for path in article_paths}

    # Route logic
    if request.method == "GET":
        if doc_id is None:
            return render_template("article.html.jinja2", 
                                   articles=articles,
                                   article=articles[0])
        else:
            if doc_id in articles.keys():
                article = articles[doc_id]
                article["contents"] = [
                    Markup(content_line) for content_line in article["contents"]
                ]
                return render_template(f"article.html.jinja2", 
                                    articles=articles,
                                    article=articles[doc_id])
            else:
                abort(404, description="Article not found")