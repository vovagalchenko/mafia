from json import dumps

class HTTP_Response_Builder(object):

    def __init__(self):
        pass
    
    def run(self):
        return HTTP_Response('200 OK', {'ho lee' : 'fuk'})

class HTTP_Response(object):
    status = '200 OK'
    body = ''
    headers = []
    
    def __init__(self, status_string, json_serializable_body):
        self.status = status_string
        self.body = dumps(json_serializable_body)
        self.headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(self.body)))
        ]
