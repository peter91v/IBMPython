# octo_server.py
import argparse
from concurrent import futures
import contextlib
import grpc
import os
import signal
import sys
import json
import _credentials
import octopyplug.octo_pb2 as octo_pb2
import octopyplug.octo_pb2_grpc as octo_pb2_grpc
import classes.const as const
from classes.loghandler import LogHandler
import classes.persistent.sensorlst as SensorLst
import classes.persistent.sensor as Sensor
import classes.base.databasecontroller as DBController

_LISTEN_ADDRESS_TEMPLATE = "0.0.0.0:%d"
_AUTH_HEADER_KEY = "authorization"
_AUTH_HEADER_VALUE = "Bearer test_token"

log_handler = LogHandler(os.path.basename(__file__)[:-3])
logger = log_handler.get_logger()

db_controller = DBController.DatabaseController()


class SignatureValidationInterceptor(grpc.ServerInterceptor):
    def __init__(self):
        super().__init__()
        self._abort_handler = grpc.unary_unary_rpc_method_handler(
            self._abort_with_unauthenticated
        )

    def _abort_with_unauthenticated(self, request, context):
        context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid signature")

    def intercept_service(self, continuation, handler_call_details):
        try:
            metadata = dict(handler_call_details.invocation_metadata)
            if metadata.get(_AUTH_HEADER_KEY) == _AUTH_HEADER_VALUE:
                return continuation(handler_call_details)
            logger.info("Authorization header validated successfully.")
        except Exception as e:
            logger.exception("Failed to validate signature: %s", str(e))
        return self._abort_handler


class MessageService(octo_pb2_grpc.MessageServiceServicer):
    def OctoMessage(self, request, context):
        # sensor_instance = Sensor.sensor()
        # sensor_instance.STANDORTID = (102,)
        # sensor_instance.TEMPERATURE = (25.1,)
        # sensor_instance.save()
        # sensor_instance.save_to_json(const.DataPath)
        sensorlist = SensorLst.sensorlst()

        json_message = json.loads(request.json_message)
        logger.info("json_message: %s", json_message)

        sensorlist.populate_from_json(request.json_message)
        # sensorlist.process_and_save_historical_data(request.json_message)
        logger.info("sensorlst: %s", sensorlist)

        sensorlist.save_all()
        count = sensorlist.count()
        logger.info("count: %s", count)
        # sensorlist.load_all()
        # sensorlist.save_all_to_json(const.DataPath)
        logger.info("Received message from client: %s", json_message)
        response = octo_pb2.OctoResponse(json_message="Message received successfully")
        logger.info(f"Sending response back to client: {response.json_message}")
        return response

    def GetDataFormat(self, request, context):
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
    def handle_sigint(sig, frame):
        logger.info("Server was interrupted manually (SIGINT).")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

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
