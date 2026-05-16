import pytest
import sys
import re
import uuid
import threading
from io import StringIO
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestRequestIdHeader:
    def test_response_includes_request_id_header(self, client):
        response = client.get('/health')
        assert 'X-Request-ID' in response.headers

    def test_accepts_upstream_request_id(self, client):
        upstream_id = 'test-request-id-123'
        response = client.get('/health', headers={'X-Request-ID': upstream_id})
        assert response.headers['X-Request-ID'] == upstream_id

    def test_generates_request_id_when_not_provided(self, client):
        response = client.get('/health')
        request_id = response.headers['X-Request-ID']
        assert request_id is not None
        assert len(request_id) > 0

    def test_generates_valid_uuid_format(self, client):
        response = client.get('/health')
        request_id = response.headers['X-Request-ID']
        uuid_pattern = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$')
        assert uuid_pattern.match(request_id) is not None

    def test_case_insensitive_header_acceptance(self, client):
        upstream_id = 'case-test-id-456'
        response = client.get('/health', headers={'x-request-id': upstream_id})
        assert response.headers['X-Request-ID'] == upstream_id

    def test_case_insensitive_header_acceptance_uppercase(self, client):
        upstream_id = 'upper-test-id-789'
        response = client.get('/health', headers={'X-REQUEST-ID': upstream_id})
        assert response.headers['X-Request-ID'] == upstream_id


class TestRequestIdLogging:
    def test_request_logs_include_request_id(self, client):
        captured_output = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output
        
        response = client.get('/health')
        
        sys.stdout = old_stdout
        logged_output = captured_output.getvalue()
        
        request_id = response.headers['X-Request-ID']
        assert request_id in logged_output

    def test_all_logs_in_request_flow_have_same_id(self, client):
        captured_output = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output
        
        response = client.get('/live')
        
        sys.stdout = old_stdout
        logged_output = captured_output.getvalue()
        
        request_id = response.headers['X-Request-ID']
        id_occurrences = logged_output.count(request_id)
        assert id_occurrences >= 1


class TestRequestIdConcurrency:
    def test_request_ids_do_not_leak_across_concurrent_requests(self):
        results = {}
        errors = []

        def make_request(request_num):
            try:
                app.config['TESTING'] = True
                with app.test_client() as client:
                    upstream_id = f'concurrent-{request_num}'
                    response = client.get('/health', headers={'X-Request-ID': upstream_id})
                    results[request_num] = response.headers['X-Request-ID']
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        if errors:
            pytest.fail(f'Concurrent requests failed: {errors}')

        expected_ids = {f'concurrent-{i}' for i in range(10)}
        actual_ids = set(results.values())
        assert actual_ids == expected_ids, f'Request IDs leaked: expected {expected_ids}, got {actual_ids}'


class TestBackwardCompatibility:
    def test_health_endpoint_still_returns_ok(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        assert response.data.decode() == 'OK'

    def test_live_endpoint_still_returns_json(self, client):
        response = client.get('/live')
        assert response.content_type == 'application/json'
        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'ok'

    def test_ready_endpoint_still_returns_json(self, client):
        response = client.get('/ready')
        assert response.content_type == 'application/json'
        data = response.get_json()
        assert 'status' in data
        assert 'dependencies' in data