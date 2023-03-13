import locale
from io import BytesIO
from composer_7 import ImageComposer7
from flask import Flask, send_file, request, jsonify

app = Flask(__name__)

locale.setlocale(locale.LC_ALL, 'da_DK.UTF-8')

@app.route("/")
def index():
    # Get API key
    api_key = request.args.get("api_key")
    if not api_key:
        return jsonify({"error": "no_api_key"}), 400

    # Render
    composer = ImageComposer7(
        api_key,
        lat=request.args.get("latitude", "39.75"),
        long=request.args.get("longitude", "-104.90"),
        timezone=request.args.get("timezone", "Europe/Copenhagen"),
    )
    output = composer.render()
    # Send to client
    output.seek(0)
    return send_file(output, mimetype="image/png")
