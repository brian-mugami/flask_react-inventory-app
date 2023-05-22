from flask import send_from_directory

from invapp import create_app

app = create_app()

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    if not path.startswith("api/"):  # Exclude API routes
        if path == "":
            return send_from_directory("react/build", "index.html")
        return send_from_directory("react/build", path)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)