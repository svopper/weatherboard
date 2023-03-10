from io import BytesIO

import locale

from flask import Flask, send_file, request

from composer_2 import ImageComposer2
from composer_7 import ImageComposer7

app = Flask(__name__)

locale.setlocale(locale.LC_ALL, 'da_DK.UTF-8')

@app.route("/")
def index():
    print("hello")
    # Get API key
    api_key = request.args.get("api_key")
    if not api_key:
        return '{"error": "no_api_key"}'
    # Render
    if request.args.get("style", "2") == "7":
        composer = ImageComposer7(
            api_key,
            lat=request.args.get("latitude", "39.75"),
            long=request.args.get("longitude", "-104.90"),
            timezone=request.args.get("timezone", "Europe/Copenhagen"),
        )
        output = composer.render()
    else:
        composer = ImageComposer2(
            api_key,
            lat=request.args.get("latitude", "39.75"),
            long=request.args.get("longitude", "-104.90"),
            timezone=request.args.get("timezone", "Europe/Copenhagen"),
        )
        image = composer.render()
        output = BytesIO()
        image.save(output, "PNG")
    # Send to client
    output.seek(0)
    return send_file(output, mimetype="image/png")
