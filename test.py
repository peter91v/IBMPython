import json
import logging
import os
import subprocess
from pathlib import Path
import sys

import octopyplug.octo_client as client


# def run_client(json_string, type):
#     module_path = (
#         Path(__file__).resolve().parent / "src" / "octo_pyplug" / "octo_client.py"
#     )
#     print("Pfad zur Moduldatei:", module_path, type)
#     command = ["python", str(module_path), json_string, type]
#     result = subprocess.run(command, capture_output=True, text=True)
#     return result.stdout.strip()


def run_client(json_string, type):
    response = client.run(json_string, type)
    return response


if __name__ == "__main__":
    logging.basicConfig()
    # if len(sys.argv) != 2:
    #     print("Usage: python test.py <json_message>")
    #     sys.exit(1)
    # Datene holen.
    # json_message = json.loads(sys.argv[1])
    json_data = {
        "101": {
            "id": "hrkaltw",
            "text": "Heizraum Kaltwasser",
            "status": 0,
            "grad": 19.19,
            "class": "wasser",
            "loc": "hz",
            "datum": "2024-03-02",
            "zeit": "15:14:02",
            "sid": "10C0AA0A020800C8",
            "code": 101,
        },
        "102": {
            "id": "hrbwoben",
            "text": "Brauchwasser oben",
            "status": 0,
            "grad": 45.69,
            "class": "wasser",
            "loc": "hz",
            "datum": "2024-03-02",
            "zeit": "15:14:02",
            "sid": "100C3F5E02080099",
            "code": 102,
        },
    }

    json_string = json.dumps(json_data)
    print("Sending JSON string to client:")
    print(json_string)

    response = run_client(json_string, "SendMessage")
    print("\nResponse from client 1:" + response)
    # print(response)
    response = run_client(json_string, "GetFormat")
    # updated_response = json.dumps(response)
    print("\nResponse from client 2:" + response)
    response_dict = json.loads(response)

    # Wert ändern
    response_dict[""]["id"] = "hrbwoben"
    print(response_dict[""])

    # Aktualisierten JSON-String erstellen
    updated_response = json.dumps(response_dict)
    print("Check successful.")
    print("\nResponse edited:" + updated_response)

    response = run_client(updated_response, "SendMessage")
    print("\nResponse from client 3:" + response)
