from game_api.http_response_builder import HTTP_Response_Builder, HTTP_Response

class create_game(HTTP_Response_Builder):
    def run(self):
        return HTTP_Response('200 OK', {'wing too' : 'low'})
