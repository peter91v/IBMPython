# OctoPyPlug
    git clone git@github.com:peter91v/OctoPyPlug.git .
    .\octovenv\Scripts\activate
    
    python.exe -m pip install --upgrade pip
    pip install flask
    pip install flask_cors
    pip install grpcio-tools
    pip install watchdog
    pip install certifi
    pip install --editable src/octoplug
    python .\pathsetter.py

    für test:
        ordner erstellen (Bsp.: google_rcp)
        cd google_rcp
        git clone git@github.com:grpc/grpc.git
        cd .\google_rcp\grpc\examples\python\auth
        cp credentials  ..\..\..\..\..\OctoPyPlug\src\octoplug\octopyplug