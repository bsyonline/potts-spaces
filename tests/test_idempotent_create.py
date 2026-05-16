import pytest
import threading
import time
from app import app, idempotency_store


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clear_store():
    idempotency_store.clear()


def test_idempotent_create_returns_same_result_for_same_key_and_payload(client):
    payload = {'name': 'test-resource', 'data': 'value'}
    headers = {'X-Idempotency-Key': 'key-123'}
    
    response1 = client.post('/resources', json=payload, headers=headers)
    response2 = client.post('/resources', json=payload, headers=headers)
    
    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response1.json['id'] == response2.json['id']
    assert response1.json['name'] == response2.json['name']


def test_idempotent_create_conflict_for_same_key_different_payload(client):
    payload1 = {'name': 'test-resource', 'data': 'value1'}
    payload2 = {'name': 'test-resource', 'data': 'value2'}
    headers = {'X-Idempotency-Key': 'key-123'}
    
    response1 = client.post('/resources', json=payload1, headers=headers)
    response2 = client.post('/resources', json=payload2, headers=headers)
    
    assert response1.status_code == 201
    assert response2.status_code == 409
    assert 'conflict' in response2.json['error'].lower()


def test_create_without_idempotency_key_creates_new_resource(client):
    payload = {'name': 'test-resource', 'data': 'value'}
    
    response1 = client.post('/resources', json=payload)
    response2 = client.post('/resources', json=payload)
    
    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response1.json['id'] != response2.json['id']


def test_concurrent_requests_with_same_key_no_duplicates(client):
    payload = {'name': 'concurrent-test', 'data': 'value'}
    headers = {'X-Idempotency-Key': 'concurrent-key-123'}
    results = []
    errors = []
    
    def make_request():
        with app.test_client() as thread_client:
            with app.app_context():
                try:
                    response = thread_client.post('/resources', json=payload, headers=headers)
                    results.append((response.status_code, response.json if response.json else {}))
                except Exception as e:
                    errors.append(str(e))
    
    threads = [threading.Thread(target=make_request) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert len(errors) == 0
    successful_results = [r for r in results if r[0] == 201]
    assert len(successful_results) >= 1
    
    created_ids = [r[1]['id'] for r in successful_results]
    assert len(set(created_ids)) == 1


def test_idempotency_key_expiry(client):
    payload = {'name': 'expiry-test', 'data': 'value'}
    headers = {'X-Idempotency-Key': 'expiry-key-123'}
    
    response1 = client.post('/resources', json=payload, headers=headers)
    assert response1.status_code == 201
    original_id = response1.json['id']
    
    time.sleep(2)
    
    response2 = client.post('/resources', json=payload, headers=headers)
    assert response2.status_code == 201
    assert response2.json['id'] == original_id