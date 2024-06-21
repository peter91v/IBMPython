# Die Basis für den octo_server stammt von https://github.com/grpc/grpc
import argparse
from concurrent import futures
import contextlib
import logging
import json
import grpc
import os
import _credentials  # Import von benutzerdefinierten Anmeldeinformationen für SSL/TLS.
import octopyplug.octo_pb2 as octo_pb2  # Import der generierten Protokollklassen.
import octopyplug.octo_pb2_grpc as octo_pb2_grpc  # Import der generierten gRPC-Dienste.
import classes.const as const
from classes.loghandler import (
    LogHandler,
)  # Importiert eine benutzerdefinierte Klasse für Logging.

# Server-Adresse und Authentifizierungskonfiguration.
_LISTEN_ADDRESS_TEMPLATE = "localhost:%d"
_AUTH_HEADER_KEY = "authorization"
_AUTH_HEADER_VALUE = "Bearer test_token"

# Logger-Konfiguration für das Erfassen von Systemmeldungen.
log_handler = LogHandler(os.path.basename(__file__)[:-3])
logger = log_handler.get_logger()


class SignatureValidationInterceptor(grpc.ServerInterceptor):
    """
    Ein Interceptor für gRPC-Server, der die Authentifizierung von eingehenden Anfragen überprüft.
    Verwendet HTTP-Headers zur Bestätigung der Authentizität der Anfrage.
    """

    def __init__(self):
        super().__init__()
        # Handler, der aufgerufen wird, wenn die Authentifizierung fehlschlägt.
        self._abort_handler = grpc.unary_unary_rpc_method_handler(
            self._abort_with_unauthenticated
        )

    def _abort_with_unauthenticated(self, request, context):
        """Beendet die Anfrage mit einem Authentifizierungsfehler."""
        context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid signature")

    def intercept_service(self, continuation, handler_call_details):
        """Überprüft, ob der Authentifizierungsheader in den Metadaten der Anfrage vorhanden ist."""
        try:
            metadata = dict(handler_call_details.invocation_metadata)
            if metadata.get(_AUTH_HEADER_KEY) == _AUTH_HEADER_VALUE:
                return continuation(handler_call_details)
            logger.info("Authorization header validated successfully.")
        except Exception as e:
            logger.exception("Failed to validate signature: %s", str(e))
        return self._abort_handler


class MessageService(octo_pb2_grpc.MessageServiceServicer):
    """
    Implementiert die gRPC-Dienste, die von den Clients verwendet werden, um Nachrichten zu senden und Datenformate abzurufen.
    """

    def OctoMessage(self, request, context):
        """Empfängt Nachrichten von Clients und gibt eine Bestätigung zurück."""
        json_message = json.loads(request.json_message)
        logger.info("Received message from client: %s", json_message)
        response = octo_pb2.OctoResponse(json_message="Message received successfully")
        logger.info(f"Sending response back to client: {response.json_message}")
        return response

    def GetDataFormat(self, request, context):
        """Gibt ein standardisiertes JSON-Datenformat zurück."""
        try:
            json_format = {
                "id": "",
                "text": "",
                "status": 0,
                "grad": 0,
                "class": "",
                "loc": "",
                "datum": "",
                "zeit": "",
                "sid": "",
                "code": 0,
            }
            logger.info("Generated JSON format successfully.")
            return octo_pb2.OctoResponse(json_message=json.dumps(json_format))
        except Exception as e:
            logger.exception("Failed to generate data format: %s", str(e))
            context.abort(grpc.StatusCode.INTERNAL, "Failed to provide data format")


@contextlib.contextmanager
def run_server(port):
    """
    Konfiguriert und startet den gRPC-Server.
    Verwendet SSL/TLS zur Sicherung der Kommunikation und setzt Interceptoren zur Überprüfung der Authentizität.
    """
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=(SignatureValidationInterceptor(),),
    )
    octo_pb2_grpc.add_MessageServiceServicer_to_server(MessageService(), server)
    try:
        server_credentials = grpc.ssl_server_credentials(
            ((_credentials.SERVER_CERTIFICATE_KEY, _credentials.SERVER_CERTIFICATE),)
        )
        server.add_secure_port(_LISTEN_ADDRESS_TEMPLATE % port, server_credentials)
        server.start()
        logger.info(f"Server started successfully on port {port}.")
        yield server, port
    except Exception as e:
        logger.exception("Failed to start server: %s", str(e))
    finally:
        server.stop(None)


def main():
    """
    Hauptfunktion, die den Server initialisiert und auf Client-Anfragen wartet.
    Die Konfiguration des Ports erfolgt über Kommandozeilenargumente.
    """
    parser = argparse.ArgumentParser(description="Starts a secure gRPC server.")
    parser.add_argument(
        "--port",
        type=int,
        default=const.ServerPort,
        help="The port the server will listen on.",
    )
    args = parser.parse_args()
    try:
        with run_server(args.port) as (server, _):
            logger.info("Server is listening at port %d", args.port)
            server.wait_for_termination()
    except Exception as e:
        logger.exception("Unexpected error in main: %s", str(e))


if __name__ == "__main__":
    main()
