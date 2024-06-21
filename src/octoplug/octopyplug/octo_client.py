# octo_client.py
import argparse
from datetime import datetime
import os
import grpc
import json  # Stellen Sie sicher, dass das json-Modul importiert ist
import _credentials
import octopyplug.octo_pb2 as octo_pb2
import octopyplug.octo_pb2_grpc as octo_pb2_grpc
from classes.loghandler import LogHandler
import classes.const as const

log_handler = LogHandler(os.path.basename(__file__)[:-3])
logger = log_handler.get_logger()
_SERVER_ADDR_TEMPLATE = "192.168.178.48:%d"
_CLIENT_REQUEST_TYPES = ["SendMessage", "GetFormat", "History"]


def create_client_channel(addr: str) -> grpc.Channel:
    """
    Erstellt einen sicheren gRPC-Kanal mit Authentifizierung über SSL und Zugriffstokens.
    Dies wird verwendet, um eine verschlüsselte und sichere Verbindung zum Server zu gewährleisten.

    Args:
        addr (str): Die Serveradresse im Format "host:port".

    Returns:
        grpc.Channel: Ein gRPC-Kanalobjekt für die sichere Kommunikation.

    Raises:
        Exception: Allgemeine Fehler während der Kanalerstellung werden geloggt und weitergereicht.
    """
    try:
        credentials = grpc.ssl_channel_credentials(_credentials.ROOT_CERTIFICATE)
        call_credentials = grpc.access_token_call_credentials("test_token")
        composite_credentials = grpc.composite_channel_credentials(
            credentials, call_credentials
        )
        return grpc.secure_channel(addr, composite_credentials)
    except Exception as e:
        logger.error(f"Failed to create client channel: {e}")
        raise


def is_file_recent(file_path: str, days: int = 5) -> bool:
    """
    Überprüft, ob eine Datei innerhalb der letzten `days` Tage modifiziert wurde.
    Diese Funktion wird genutzt, um zu entscheiden, ob aktuelle oder veraltete Daten verwendet werden.

    Args:
        file_path (str): Pfad zur Datei.
        days (int): Anzahl der Tage, innerhalb derer die Datei als aktuell betrachtet wird.

    Returns:
        bool: True, wenn die Datei kürzlich modifiziert wurde, sonst False.

    Raises:
        Exception: Fehler beim Zugriff auf das Dateisystem werden geloggt.
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"File {file_path} does not exist.")
            return False
        file_time = os.path.getmtime(file_path)
        current_time = datetime.now().timestamp()
        is_recent = (current_time - file_time) / 86400 <= days
        logger.info(f"File {file_path} is {'recent' if is_recent else 'not recent'}.")
        return is_recent
    except Exception as e:
        logger.error(f"Failed to check if file is recent: {e}")
        return False


def run(channel: grpc.Channel, json_msg: dict, type: str) -> any:
    stub = octo_pb2_grpc.MessageServiceStub(channel)
    metadata = [("authorization", "Bearer test_token")]
    response = None  # Initialisieren Sie die Variable response

    Args:
        channel (grpc.Channel): Der gRPC-Kanal.
        json_message (dict): Die zu sendende Nachricht, verpackt als JSON.
        type (str): Der Typ der Anfrage, z.B. 'SendMessage' oder 'GetFormat'.

    Returns:
        any: Die Antwort des Servers oder None bei einem Fehler.

    Raises:
        grpc.RpcError: Spezifische gRPC Fehler werden erfasst und geloggt.
        Exception: Allgemeine Fehler während der Ausführung werden erfasst und geloggt.
    """
    stub = octo_pb2_grpc.MessageServiceStub(channel)
    json_string = json.dumps(json_message)
    logger.info(f"Running {type} request with data: {json_string}")
    try:
        if type == "SendMessage":
            json_string = json.dumps(json_msg)
            logger.info(f"Running {type} request with data: {json_string}")
            request = octo_pb2.OctoRequest(json_message=json_string)
            response = stub.OctoMessage(request, metadata=metadata)
            logger.info(f"Received response: {response.json_message}")
            print(response.json_message)

        elif type == "History":
            json_string = json.dumps(json_msg)
            logger.info(f"Running {type} request with data: {json_string}")
            request = octo_pb2.OctoRequest(json_message=json_string)
            response = stub.OctoMessage(request, metadata=metadata)
            logger.info(f"Received response: {response.json_message}")
            print(response.json_message)

        elif type == "GetFormat":
            if not is_file_recent("dataschema.json"):
                response = stub.GetDataFormat(octo_pb2.OctoRequest(), metadata=metadata)
                with open("dataschema.json", "w") as file:
                    file.write(response.json_message)
                logger.info("Updated dataschema.json from server.")
            else:
                with open("dataschema.json", "r") as file:
                    response = octo_pb2.OctoResponse(json_message=file.read())
                logger.info(f"Received response: {response.json_message}")
            return response

    except grpc.RpcError as e:
        logger.error(f"RPC failed with status: {e.code()}, details: {e.details()}")
        print(f"RPC failed: {e.code()}, {e.details()}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during '{type}' request: {e}")
        return None


def main():
    """
    Hauptfunktion des Programms, die beim Ausführen des Scripts aktiviert wird.
    Verarbeitet die Kommandozeilenargumente und führt die gRPC-Anfrage durch.

    Raises:
        Exception: Erfasst und loggt alle Fehler, die während der Hauptausführung auftreten.
    """
    parser = argparse.ArgumentParser(
        description="Client to communicate with OctoServer"
    )
    parser.add_argument("port", type=int, default=const.ServerPort, help="Server port")
    parser.add_argument(
        "json_message",
        type=json.loads,
        default="{}",
        help="JSON message to send as dict",
    )
    parser.add_argument(
        "type",
        choices=_CLIENT_REQUEST_TYPES,
        default=_CLIENT_REQUEST_TYPES[0],
        help="Type of request",
    )
    args = parser.parse_args()

    try:
        address = f"{_SERVER_ADDR_TEMPLATE % args.port}"
        channel = create_client_channel(address)
        response = run(channel, args.json_message, args.type)
        logger.info(f"Final response: {response}")
        print(response)
    except KeyboardInterrupt:
        logger.info("Client was interrupted manually (SIGINT).")
        print("Client was interrupted manually.")
    except Exception as e:
        logger.error(f"Error in main function: {e}")


if __name__ == "__main__":
    main()
