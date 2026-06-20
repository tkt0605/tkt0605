import os
from flask import Flask, send_from_directory

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dist = os.path.join(BASE_DIR, "dist")
public = os.path.join(BASE_DIR, "public")
app = Flask(__name__, template_folder="../templates", static_folder="../dist")


@app.route("/<path:path>")
def send_static(path):
    if path.endswith("/"):
        path = f"{path}index.html"
    try:
        return send_from_directory(dist, path, max_age=0)
    except Exception:
        try: 
            return send_from_directory(dist, f"{path}.html", max_age=0)
        except Exception:
            return send_from_directory(public, path, max_age=60*60*24*365)

@app.route("/")
def index():
    return send_from_directory(dist, "index.html", max_age=0)