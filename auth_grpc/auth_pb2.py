# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: auth.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nauth.proto\x12\x0bgrpc_server\"%\n\x05Token\x12\r\n\x05token\x18\x01 \x01(\t\x12\r\n\x05roles\x18\x02 \x03(\t\"\'\n\x11HasAccessResponse\x12\x12\n\nhas_access\x18\x01 \x01(\x08\x32J\n\x05Unary\x12\x41\n\tHasAccess\x12\x12.grpc_server.Token\x1a\x1e.grpc_server.HasAccessResponse\"\x00\x62\x06proto3')



_TOKEN = DESCRIPTOR.message_types_by_name['Token']
_HASACCESSRESPONSE = DESCRIPTOR.message_types_by_name['HasAccessResponse']
Token = _reflection.GeneratedProtocolMessageType('Token', (_message.Message,), {
  'DESCRIPTOR' : _TOKEN,
  '__module__' : 'auth_pb2'
  # @@protoc_insertion_point(class_scope:grpc_server.Token)
  })
_sym_db.RegisterMessage(Token)

HasAccessResponse = _reflection.GeneratedProtocolMessageType('HasAccessResponse', (_message.Message,), {
  'DESCRIPTOR' : _HASACCESSRESPONSE,
  '__module__' : 'auth_pb2'
  # @@protoc_insertion_point(class_scope:grpc_server.HasAccessResponse)
  })
_sym_db.RegisterMessage(HasAccessResponse)

_UNARY = DESCRIPTOR.services_by_name['Unary']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _TOKEN._serialized_start=27
  _TOKEN._serialized_end=64
  _HASACCESSRESPONSE._serialized_start=66
  _HASACCESSRESPONSE._serialized_end=105
  _UNARY._serialized_start=107
  _UNARY._serialized_end=181
# @@protoc_insertion_point(module_scope)
