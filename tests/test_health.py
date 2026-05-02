from potts_spaces.app import app


def test_health_endpoint_returns_200():
    environ = {
        "PATH_INFO": "/health",
        "REQUEST_METHOD": "GET",
    }
    
    responses = {}
    
    def start_response(status, headers):
        responses["status"] = status
        responses["headers"] = headers
    
    body = app(environ, start_response)
    
    assert responses["status"] == "200 OK"
    assert body == [b"OK"]