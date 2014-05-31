from game_api.http_response_builder import HTTP_Response_Builder, HTTP_Response
from game_api.parameter import Parameter, String_Parameter_Type

class get_game(HTTP_Response_Builder):
    vova = Parameter('vova', required = True, parameter_type = String_Parameter_Type)

    def do_controller_specific_work(self):
        return HTTP_Response("200 OK", {'game_id' : self.resource_id})
