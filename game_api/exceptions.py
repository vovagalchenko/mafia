class InvalidAPICallException(Exception):
    method = ""
    endpoint = ""
    
    def __init__(self, method, endpoint, msg):
        Exception.__init__(self, msg)
        self.method = method
        self.endpoint = endpoint

    def as_string(self):
        return "Invalid API call {%s %s}: %s" % (self.method, self.endpoint, self.args[0])

    def http_status(self):
        return "400 Bad Request"
    
class InvalidAPIMethodException(InvalidAPICallException):
    def http_status(self):
        return "405 Method Not Allowed"
