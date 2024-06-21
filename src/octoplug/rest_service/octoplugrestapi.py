import argparse
import json
import logging
import os
import subprocess
from flask_cors import CORS
from flask import Flask, request, jsonify
import classes.const as const
from classes.loghandler import (
    LogHandler,
)  # Importiert eine benutzerdefinierte Klasse für das Logging.
import classes.const as const

app = Flask(__name__)
CORS(app)  # Erlaubt Cross-Origin Requests für die gesamte Flask-App.

# Konfiguriert den Logger.
log_handler = LogHandler(app.name)
LOGGER = log_handler.get_logger()


def run_subprocess(json_string: str):
    """Führt einen externen Python-Prozess aus, basierend auf der Konfiguration.

    Args:
        json_string (str): JSON string, der als Argument an den Subprozess übergeben wird.

    Returns:
        str: Die Ausgabe des Subprozesses.
    """
    try:
        result = subprocess.run(
            [
                const.python_executable,
                const.octo_client_path,
                str(const.ServerPort),
                json_string,
                "SendMessage",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        LOGGER.info(f"Subprocess executed with JSON: {json_string}")
        LOGGER.info(f"Subprocess output: {result.stdout}")
        return result.stdout
    except Exception as e:
        LOGGER.exception(f"Failed to run subprocess: {e}")
        return ""


@app.route("/", methods=["GET"])
def get_json():
    """Verarbeitet GET-Anfragen und gibt die bearbeiteten Daten zurück."""
    try:
        keys = request.args.keys()
        LOGGER.info(f"Received GET request with keys: {list(keys)}")
        params_json = {key: request.args.get(key) for key in keys}
        data = params_json.get("data")

        if data:
            try:
                params_json = json.loads(data)
                json_string = json.dumps(params_json)
            except ValueError:
                json_string = data  # Nimmt an, dass 'data' bereits ein JSON-String ist.
                LOGGER.warning("Data is not a valid JSON string: assuming plain text.")

            result = run_subprocess(json_string)

            try:
                response_data = json.loads(result)
            except json.JSONDecodeError:
                response_data = result.strip()
                LOGGER.warning("Subprocess returned non-JSON data.")
            return jsonify({"received_data": response_data}), 200

        LOGGER.warning("No JSON data provided in GET request.")
        return jsonify({"error": "No JSON data provided in the request"}), 400
    except Exception as e:
        LOGGER.exception("Error processing GET request: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500


@app.route("/post_example", methods=["POST"])
def post_example():
    """Verarbeitet POST-Anfragen und gibt die bearbeiteten Daten zurück."""
    try:
        data = request.json
        LOGGER.info(f"Received POST request with data: {data}")

        if data:
            try:
                json_string = json.dumps(data)
                result = run_subprocess(json_string)
                try:
                    response_data = json.loads(result)
                except json.JSONDecodeError:
                    response_data = result.strip()
                    LOGGER.warning("Subprocess returned non-JSON data.")
                return jsonify({"received_data": response_data}), 200
            except Exception as e:
                LOGGER.exception("Error processing data in POST request: %s", str(e))
                return (
                    jsonify(
                        {"error": "An error occurred while processing the request"}
                    ),
                    500,
                )

        LOGGER.warning("No JSON data provided in POST request.")
        return jsonify({"error": "No JSON data provided in the request"}), 400
    except Exception as e:
        LOGGER.exception("Error processing POST request: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500


def parse_arguments():
    """Parses command-line arguments and logs the server configuration."""
    parser = argparse.ArgumentParser(description="Starts a secure Flask server.")
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="The host of the server"
    )
    parser.add_argument(
        "--port", type=int, default=const.RestPort, help="The port of the server"
    )
    args = parser.parse_args()
    LOGGER.info(f"Starting server at {args.host}:{args.port}")
    return args


if __name__ == "__main__":
    args = parse_arguments()
    try:
        app.run(host=args.host, port=args.port)
        LOGGER.info(f"REST API running on {args.host}:{args.port}")
    except Exception as e:
        LOGGER.exception(
            f"Failed to start Flask server on {args.host}:{args.port}: {e}"
        )
