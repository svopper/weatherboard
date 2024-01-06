import locale
import logging
from composer import ImageComposer
from flask import Flask, send_file, request, jsonify

app = Flask(__name__)

locale.setlocale(locale.LC_ALL, 'da_DK.UTF-8')

@app.route("/")
def index():
    # Get API key
    api_key = request.args.get("api_key")
    if not api_key:
        return jsonify({"error": "No query parameter named api_key present"}), 400

    # Render
    composer = ImageComposer(
        api_key,
        lat=request.args.get("latitude", "55.656404"),
        long=request.args.get("longitude", "12.590530"),
        timezone=request.args.get("timezone", "Europe/Copenhagen"),
    )
    output = composer.render()
    logging.log(logging.INFO, "Created image for %s" % request.remote_addr)
    # Send to client
    output.seek(0)
    return send_file(output, mimetype="image/png")

@app.route("/health")
def health():
    return "OK"