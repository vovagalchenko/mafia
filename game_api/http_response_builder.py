from json import dumps, loads
from game_api.exceptions import *
from game_api.parameter import Parameter, Invalid_Parameter_Exception
from urlparse import parse_qsl

class HTTP_Response_Builder(object):
    warnings = []
    resource_id = None

    def __init__(self, query_string, body_stream, content_length, resource_id):
        self.warnings = []
        self.resource_id = resource_id
        passed_in_param_dict= {}
        if content_length > 0:
            body_str = body_stream.read(content_length)
            try:
                passed_in_param_dict = loads(body_str)
            except ValueError as e:
                raise API_Exception("400 Bad Request", "The HTTP body must be JSON-encoded.")
        query_param_list = {}
        if query_string:
            try:
                query_param_list = parse_qsl(query_string, True, True)
            except ValueError as e:
                raise API_Exception("400 Bad Request", "The query string must be URL encoded.")
        for k,v in query_param_list:
            if k in passed_in_param_dict:
                raise Invalid_Parameter_Exception(k, "This parameter is given twice. Between the query string and the HTTP body, every parameter can only be specified once.")
            passed_in_param_dict[k] = v
        for param_name in dir(self):
            param_definition = getattr(self, param_name)
            if not isinstance(param_definition, Parameter):
                continue
            param_value = param_definition.get_value(passed_in_param_dict.get(param_definition.name, None))
            passed_in_param_dict.pop(param_definition.name, None)
            setattr(self, param_name, param_value)
        if any(passed_in_param_dict):
            self.warnings.append({"unused_arguments" : passed_in_param_dict})
        
    def finalize_http_response(self, http_response):
        http_response.add_to_body('warnings', self.warnings)
        return http_response

    def do_controller_specific_work(self):
        return HTTP_Response("200 OK", {"ho lee" : "fuk"})

    def run(self):
        http_response = self.do_controller_specific_work()
        return self.finalize_http_response(http_response)

class HTTP_Response(object):
    
    def __init__(self, status_string, json_serializable_body):
        self.status = status_string
        self.body = json_serializable_body
        self.serialized_body_cache = None
        self.headers = [
            ('Content-Type' , 'application/json')
        ]

    def add_to_body(self, key, value):
        self.body[key] = value
        self.serialized_body_cache = None

    def get_status(self):
        return self.status
    
    def get_body_string(self):
        if self.serialized_body_cache is None:
            self.serialized_body_cache = dumps(self.body)
        return self.serialized_body_cache
    
    def get_headers(self):
        headers = self.headers
        headers.append(('Content-Length', str(len(self.get_body_string()))))
        return headers
