# local_runner.py

from web_ui import app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=10000, debug=True)
