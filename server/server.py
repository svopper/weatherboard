import os
import locale
import logging
from io import BytesIO
from composer import ImageComposer
from flask import Flask, send_file, request, jsonify
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.flask.flask_middleware import FlaskMiddleware

app = Flask(__name__)

# Enable Application Insights
instrumentation_key = f"InstrumentationKey={os.environ.get('APPINSIGHTS_INSTRUMENTATIONKEY')}"
print(instrumentation_key)
middleware = FlaskMiddleware(
    app,
    exporter=AzureExporter(connection_string=instrumentation_key),
    sampler=ProbabilitySampler(rate=1.0),
)

locale.setlocale(locale.LC_ALL, 'da_DK.UTF-8')

@app.route("/")
def index():
    # Get API key
    api_key = request.args.get("api_key")
    if not api_key:
        return jsonify({"error": "no_api_key"}), 400

    # Render
    composer = ImageComposer(
        api_key,
        lat=request.args.get("latitude", "39.75"),
        long=request.args.get("longitude", "-104.90"),
        timezone=request.args.get("timezone", "Europe/Copenhagen"),
    )
    output = composer.render()
    logging.log(2, "Created image for %s" % request.remote_addr)
    # Send to client
    output.seek(0)
    return send_file(output, mimetype="image/png")

@app.route("/health")
def health():
    return "OK"