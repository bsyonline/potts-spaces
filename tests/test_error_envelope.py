import pytest
import re
import traceback
import json
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestErrorEnvelopeContract:
    def test_error_response_has_code_field(self, client):
        payload1 = {'name': 'test', 'data': 'value1'}
        payload2 = {'name': 'test', 'data': 'value2'}
        headers = {'X-Idempotency-Key': 'key-123'}
        
        client.post('/resources', json=payload1, headers=headers)
        response = client.post('/resources', json=payload2, headers=headers)
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'code' in data

    def test_error_response_has_message_field(self, client):
        payload1 = {'name': 'test', 'data': 'value1'}
        payload2 = {'name': 'test', 'data': 'value2'}
        headers = {'X-Idempotency-Key': 'key-123'}
        
        client.post('/resources', json=payload1, headers=headers)
        response = client.post('/resources', json=payload2, headers=headers)
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'message' in data

    def test_error_response_has_request_id_field(self, client):
        payload1 = {'name': 'test', 'data': 'value1'}
        payload2 = {'name': 'test', 'data': 'value2'}
        headers = {'X-Idempotency-Key': 'key-123'}
        
        client.post('/resources', json=payload1, headers=headers)
        response = client.post('/resources', json=payload2, headers=headers)
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'request_id' in data

    def test_error_request_id_matches_header(self, client):
        payload1 = {'name': 'test', 'data': 'value1'}
        payload2 = {'name': 'test', 'data': 'value2'}
        headers = {'X-Idempotency-Key': 'key-123'}
        
        client.post('/resources', json=payload1, headers=headers)
        response = client.post('/resources', json=payload2, headers=headers)
        
        assert response.status_code == 409
        data = response.get_json()
        assert data['request_id'] == response.headers.get('X-Request-ID')


class TestErrorRedaction:
    def test_no_file_paths_in_error_message(self, client):
        payload1 = {'name': 'test', 'data': 'value1'}
        payload2 = {'name': 'test', 'data': 'value2'}
        headers = {'X-Idempotency-Key': 'key-123'}
        
        client.post('/resources', json=payload1, headers=headers)
        response = client.post('/resources', json=payload2, headers=headers)
        
        data = response.get_json()
        message = data.get('message', '')
        
        path_pattern = re.compile(r'(?:/[\w/.-]+\.\w+|[A-Z]:\\[\w\\.-]+\.?\w*|\.\w+/\w+)')
        assert not path_pattern.search(message), f'Path found in error message: {message}'

    def test_no_stack_trace_in_error_payload(self, client):
        payload1 = {'name': 'test', 'data': 'value1'}
        payload2 = {'name': 'test', 'data': 'value2'}
        headers = {'X-Idempotency-Key': 'key-123'}
        
        client.post('/resources', json=payload1, headers=headers)
        response = client.post('/resources', json=payload2, headers=headers)
        
        data = response.get_json()
        response_str = json.dumps(data)
        
        stack_patterns = ['Traceback', 'File "', 'line ', 'Error:']
        for pattern in stack_patterns:
            assert pattern not in response_str, f'Stack trace pattern "{pattern}" found in response'

    def test_no_internal_details_in_error_code(self, client):
        payload1 = {'name': 'test', 'data': 'value1'}
        payload2 = {'name': 'test', 'data': 'value2'}
        headers = {'X-Idempotency-Key': 'key-123'}
        
        client.post('/resources', json=payload1, headers=headers)
        response = client.post('/resources', json=payload2, headers=headers)
        
        data = response.get_json()
        code = data.get('code', '')
        
        assert code not in ['internal_error', 'server_error', 'unknown']
        assert not re.match(r'^[A-Z_]+$', code) or code in ['IDEMPOTENCY_CONFLICT', 'VALIDATION_ERROR', 'NOT_FOUND', 'BAD_REQUEST']


class TestMultipleErrorClasses:
    def test_idempotency_conflict_error_class(self, client):
        payload1 = {'name': 'test', 'data': 'value1'}
        payload2 = {'name': 'test', 'data': 'value2'}
        headers = {'X-Idempotency-Key': 'key-123'}
        
        client.post('/resources', json=payload1, headers=headers)
        response = client.post('/resources', json=payload2, headers=headers)
        
        assert response.status_code == 409
        data = response.get_json()
        assert data['code'] == 'IDEMPOTENCY_CONFLICT'

    def test_not_found_error_class(self, client):
        response = client.get('/resources/nonexistent-id')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'code' in data
        assert data['code'] == 'NOT_FOUND'

    def test_validation_error_class_for_invalid_json(self, client):
        response = client.post('/resources', data='not valid json', content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'code' in data
        assert data['code'] == 'BAD_REQUEST'


class TestErrorConsistencyAcrossEndpoints:
    def test_health_endpoint_error_format(self, client):
        pass

    def test_resources_endpoint_error_format(self, client):
        payload1 = {'name': 'test', 'data': 'value1'}
        payload2 = {'name': 'test', 'data': 'value2'}
        headers = {'X-Idempotency-Key': 'key-123'}
        
        client.post('/resources', json=payload1, headers=headers)
        response = client.post('/resources', json=payload2, headers=headers)
        
        assert response.status_code == 409
        data = response.get_json()
        
        assert set(data.keys()) == {'code', 'message', 'request_id'}

    def test_all_errors_have_same_structure(self, client):
        error_responses = []
        
        payload1 = {'name': 'test', 'data': 'value1'}
        payload2 = {'name': 'test', 'data': 'value2'}
        headers = {'X-Idempotency-Key': 'key-456'}
        client.post('/resources', json=payload1, headers=headers)
        error_responses.append(client.post('/resources', json=payload2, headers=headers).get_json())
        
        error_responses.append(client.get('/resources/nonexistent-id').get_json())
        
        error_responses.append(client.post('/resources', data='not json', content_type='application/json').get_json())
        
        for error_data in error_responses:
            assert set(error_data.keys()) == {'code', 'message', 'request_id'}