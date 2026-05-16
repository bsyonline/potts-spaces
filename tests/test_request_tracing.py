import pytest
import logging
import uuid
import threading
import time
from io import StringIO
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_response_includes_x_request_id_header(client):
    response = client.get('/health')
    assert 'X-Request-ID' in response.headers
    request_id = response.headers['X-Request-ID']
    assert len(request_id) > 0


def test_request_id_generated_if_not_provided(client):
    response = client.get('/health')
    request_id = response.headers['X-Request-ID']
    assert request_id is not None
    assert len(request_id) == 36
    uuid.UUID(request_id)


def test_request_id_accepted_from_upstream_header(client):
    upstream_id = 'test-request-id-12345'
    response = client.get('/health', headers={'X-Request-ID': upstream_id})
    assert response.headers['X-Request-ID'] == upstream_id


def test_request_id_case_insensitive_header_handling(client):
    upstream_id = 'case-test-id-98765'
    response = client.get('/health', headers={'x-request-id': upstream_id})
    assert response.headers['X-Request-ID'] == upstream_id


def test_request_id_appears_in_logs(client):
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger = logging.getLogger('app')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    upstream_id = 'log-test-id-abcde'
    response = client.get('/health', headers={'X-Request-ID': upstream_id})
    
    log_contents = log_stream.getvalue()
    assert upstream_id in log_contents


def test_concurrent_requests_have_different_ids():
    results = {}
    
    def make_request(thread_id):
        app.config['TESTING'] = True
        with app.test_client() as client:
            response = client.get('/health')
            results[thread_id] = response.headers.get('X-Request-ID')
    
    threads = []
    for i in range(10):
        t = threading.Thread(target=make_request, args=(i,))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    ids = list(results.values())
    assert len(ids) == 10
    assert len(set(ids)) == 10


def test_request_ids_do_not_leak_between_concurrent_requests():
    start_event = threading.Event()
    continue_event = threading.Event()
    request_ids_during_overlap = {}
    
    def overlapping_request(thread_id, request_ids_during_overlap):
        app.config['TESTING'] = True
        with app.test_client() as client:
            start_event.wait()
            response = client.get('/health')
            captured_id = response.headers.get('X-Request-ID')
            request_ids_during_overlap[thread_id] = captured_id
            continue_event.wait()
    
    threads = []
    for i in range(5):
        t = threading.Thread(target=overlapping_request, args=(i, request_ids_during_overlap))
        threads.append(t)
        t.start()
    
    start_event.set()
    time.sleep(0.05)
    ids_at_overlap_point = dict(request_ids_during_overlap)
    continue_event.set()
    
    for t in threads:
        t.join()
    
    ids = list(ids_at_overlap_point.values())
    assert len(ids) == 5
    assert len(set(ids)) == 5


def test_existing_health_behavior_preserved(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.data == b'OK'
    assert 'X-Request-ID' in response.headers


def test_existing_live_behavior_preserved(client):
    response = client.get('/live')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert 'uptime_seconds' in data
    assert 'X-Request-ID' in response.headers


def test_existing_ready_behavior_preserved(client):
    response = client.get('/ready')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert 'X-Request-ID' in response.headers