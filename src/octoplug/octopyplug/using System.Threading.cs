using System.Threading.Tasks;
using Grpc.Net.Client;
using OctoClient; // Stellen Sie sicher, dass dieses Namespace mit Ihrem csharp_namespace in der .proto-Datei übereinstimmt.

// Setzen Sie diese Einstellung, um nicht-verschlüsselte HTTP/2-Verbindungen zu erlauben (nur wenn Ihr gRPC-Server nicht SSL/TLS verwendet).
AppContext.SetSwitch("System.Net.Http.SocketsHttpHandler.Http2UnencryptedSupport", true);

var httpHandler = new HttpClientHandler();
// Diese Zeile ist nur für Tests geeignet, bei der Verwendung in Produktionsumgebungen sollte eine ordnungsgemäße Validierung von Zertifikaten erfolgen.
httpHandler.ServerCertificateCustomValidationCallback = HttpClientHandler.DangerousAcceptAnyServerCertificateValidator;

var channel = GrpcChannel.ForAddress("http://localhost:5000", new GrpcChannelOptions { HttpHandler = httpHandler });

var client = new MessageService.MessageServiceClient(channel);

// Senden einer Nachricht mit dem korrekten Feldnamen 'json_message'
var request = new OctoRequest { JsonMessage = "Hello from the client!" };
var reply = await client.OctoMessageAsync(request);

Console.WriteLine("Received from server: " + reply.JsonMessage);
Console.WriteLine("Press any key to exit...");
Console.ReadKey();
