import subprocess


def generate_grpc_code():
    command = [
        "python",
        "-m",
        "grpc_tools.protoc",
        "-I.",
        "--python_out=../octo_pyplug",
        "--pyi_out=../octo_pyplug/",
        "--grpc_python_out=../octo_pyplug",
        "octo.proto",
    ]
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
        return result
    except subprocess.CalledProcessError as e:
        return f"Error generating gRPC code: {e.output}"


if __name__ == "__main__":
    result = generate_grpc_code()
    if "Error" not in result:
        print("gRPC code generation successful!")
    else:
        print(result)
