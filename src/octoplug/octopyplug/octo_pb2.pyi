from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class OctoRequest(_message.Message):
    __slots__ = ("json_message",)
    JSON_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    json_message: str
    def __init__(self, json_message: _Optional[str] = ...) -> None: ...

class OctoResponse(_message.Message):
    __slots__ = ("json_message", "test")
    JSON_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TEST_FIELD_NUMBER: _ClassVar[int]
    json_message: str
    test: str
    def __init__(self, json_message: _Optional[str] = ..., test: _Optional[str] = ...) -> None: ...

class GetDataRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
