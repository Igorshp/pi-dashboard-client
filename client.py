import io
import os
import json
from flask import Flask, send_file, request, send_from_directory, jsonify
from chromote import Chromote
from PIL import Image
from flask_cors import CORS
import subprocess
import uuid
import time


chomote = False


app = Flask(__name__)
CORS(app)
os.environ["DISPLAY"] = ":0"

DATA_FOLDER = "data"
HISTORY_FILE = f"{DATA_FOLDER}/history.txt"
CURRENT_URL_FILE = f"{DATA_FOLDER}/current_url.txt"
HISTORY_SIZE = 10


def save_current_url_to_file(url):
    print(f"saving current url to file: {url}")
    with open(CURRENT_URL_FILE, "w") as f:
        f.write(f"{url}")


def load_last_url_from_file():
    if not os.path.isfile(CURRENT_URL_FILE):
        print(f"{CURRENT_URL_FILE} does not exist")
        return None
    print("loading last used url from file")
    with open(CURRENT_URL_FILE, "r") as f:
        return f.readline().strip()


def load_recent_history():
    if not os.path.isfile(HISTORY_FILE):
        print("history file not found")
        return []
    with open(HISTORY_FILE, "r") as f:
        history = [x.strip() for x in f.readlines()]
        print("====")
        print(history)
        history.reverse()
        # deduplicate
        # items already seen (older ones) are removed
        history = [x for i, x in enumerate(history) if i == history.index(x)]

        return history[-HISTORY_SIZE:]


@app.route("/history")
def history():
    history = load_recent_history()
    return jsonify(history)


# this function enforces history file on every write.
# changes to size are goverened by load_recent_history
def add_to_history(url):
    history = load_recent_history()
    history.reverse()  # history already gets reversed when loading from file, to ensure consistency reverse it here
    history.append(url)
    with open(HISTORY_FILE, "w") as f:
        for line in history:
            f.write(f"{line}\n")


def resize_image(img_data, basewidth=300):
    with Image.open(img_data) as img:
        wpercent = basewidth / float(img.size[0])
        hsize = int((float(img.size[1]) * float(wpercent)))
        return img.resize((basewidth, hsize), Image.ANTIALIAS)


@app.route("/home")
def hello_world():
    # show current playing page, recent urls and option to set a new one
    # uses the below api under the hood
    # return send_from_directory("./", "index.html")
    return send_file("TV.png", attachment_filename="tv.png", mimetype="image/png")


def set_chrome_url(url):
    tab = chrome.tabs[0]
    tab.set_url(url)
    add_to_history(url)


def get_chrome_url():
    tab = chrome.tabs[0]
    return tab.url


@app.route("/url", methods=["GET", "POST"])
def url():
    new_url = request.args.get("url")
    if new_url:
        set_chrome_url(new_url)
        save_current_url_to_file(new_url)
    return get_chrome_url()


@app.route("/playlist/add", methods=["GET"])
def add_to_playlist():
    pass


@app.route("/playlist", methods=["GET"])
def playlist_view():
    pass


@app.route("/screenshot")
def screenshot():
    try:
        screenshot_file = "/tmp/screenshot-{}.png".format(uuid.uuid4())
        subprocess.call(["scrot", screenshot_file, "-q", "75"])

        img = resize_image(screenshot_file)

        img_io = io.BytesIO()
        img.save(img_io, "png", quality="70")
        img_io.seek(0)

        return send_file(
            img_io, attachment_filename="screenshot.png", mimetype="image/png"
        )
    except FileNotFoundError:
        return send_file(
            "error-no-screenshot.png",
            attachment_filename="error.png",
            mimetype="image/png",
        )
    finally:
        if os.path.isfile(screenshot_file):
            os.remove(screenshot_file)


@app.route("/images/<filename>")
def images(filename):
    return send_file(filename, attachment_filename=filename, mimetype="image/png",)


@app.route("/")
def info():
    print("Rasspbery pi dashboard")
    # show informationa about this pi
    # hostname, ip address, uptime, user
    return json.dumps(load_recent_history())


@app.route("/restart")
def restart():
    pass


@app.route("/shutdown", methods=["POST"])
def shutdown():
    pass


if __name__ == "__main__":
    while True:
        try:
            chrome = Chromote()
            break
        except Exception as e:
            print(
                "Failed to connect to chrome remote debugger, waiting for chrome to start",
                e,
            )
            time.sleep(1)
            continue
    try:
        last_url = load_last_url_from_file()
        if last_url:
            print(f"Recovered last known url, setting it on startup: {last_url}")
            set_chrome_url(last_url)
    except Exception as e:
        print(f"Failed to recover url: {e}")

    app.run(host="0.0.0.0", port="5000")
