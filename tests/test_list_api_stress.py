import pytest
from app import app, resources_store, resources_lock, idempotency_store, idempotency_lock


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with resources_lock:
        resources_store.clear()
    with idempotency_lock:
        idempotency_store.clear()
    with app.test_client() as client:
        yield client


@pytest.fixture
def populated_store(client):
    resources = []
    for i in range(25):
        response = client.post('/resources', json={
            'name': f'item-{i}',
            'data': {'category': f'cat-{i % 3}', 'value': i * 10}
        })
        resources.append(response.get_json())
    return resources


class TestListEndpointBasicContract:
    def test_list_returns_200(self, client):
        response = client.get('/resources')
        assert response.status_code == 200

    def test_list_returns_json(self, client):
        response = client.get('/resources')
        assert response.content_type == 'application/json'

    def test_list_has_items_and_total_fields(self, client):
        response = client.get('/resources')
        data = response.get_json()
        assert 'items' in data
        assert 'total' in data

    def test_list_items_is_list(self, client):
        response = client.get('/resources')
        data = response.get_json()
        assert isinstance(data['items'], list)

    def test_list_total_is_integer(self, client):
        response = client.get('/resources')
        data = response.get_json()
        assert isinstance(data['total'], int)


class TestPaginationContract:
    def test_pagination_default_page_and_per_page(self, populated_store):
        with app.test_client() as client:
            response = client.get('/resources')
            data = response.get_json()
            assert len(data['items']) == data['total']

    def test_pagination_per_page_limits_items(self, populated_store):
        with app.test_client() as client:
            response = client.get('/resources?per_page=5')
            data = response.get_json()
            assert len(data['items']) == 5

    def test_pagination_page_offset(self, populated_store):
        with app.test_client() as client:
            page1 = client.get('/resources?per_page=10&page=1').get_json()
            page2 = client.get('/resources?per_page=10&page=2').get_json()
            assert len(page1['items']) == 10
            assert len(page2['items']) == 10
            assert page1['items'][0]['id'] != page2['items'][0]['id']

    def test_pagination_total_unaffected_by_per_page(self, populated_store):
        with app.test_client() as client:
            resp1 = client.get('/resources?per_page=5').get_json()
            resp2 = client.get('/resources?per_page=10').get_json()
            resp3 = client.get('/resources').get_json()
            assert resp1['total'] == resp2['total'] == resp3['total'] == 25

    def test_pagination_boundary_last_page(self, populated_store):
        with app.test_client() as client:
            response = client.get('/resources?per_page=10&page=3')
            data = response.get_json()
            assert len(data['items']) == 5
            assert data['total'] == 25

    def test_pagination_boundary_empty_page(self, populated_store):
        with app.test_client() as client:
            response = client.get('/resources?per_page=10&page=4')
            data = response.get_json()
            assert len(data['items']) == 0
            assert data['total'] == 25

    def test_pagination_no_off_by_one_first_page(self, populated_store):
        with app.test_client() as client:
            response = client.get('/resources?per_page=25&page=1')
            data = response.get_json()
            assert len(data['items']) == 25

    def test_pagination_page_zero_or_negative_error(self, client):
        response = client.get('/resources?page=0')
        assert response.status_code == 400
        data = response.get_json()
        assert 'code' in data

    def test_pagination_per_page_zero_or_negative_error(self, client):
        response = client.get('/resources?per_page=0')
        assert response.status_code == 400
        data = response.get_json()
        assert 'code' in data

    def test_pagination_per_page_exceeds_max_returns_error(self, client):
        response = client.get('/resources?per_page=1000')
        assert response.status_code == 400
        data = response.get_json()
        assert 'code' in data


class TestFilteringContract:
    def test_filter_by_name_exact_match(self, populated_store):
        with app.test_client() as client:
            response = client.get('/resources?filter=name:item-5')
            data = response.get_json()
            assert len(data['items']) == 1
            assert data['items'][0]['name'] == 'item-5'
            assert data['total'] == 1

    def test_filter_by_name_prefix(self, populated_store):
        with app.test_client() as client:
            response = client.get('/resources?filter=name:item-1*')
            data = response.get_json()
            assert data['total'] == 11

    def test_filter_by_nested_field(self, populated_store):
        with app.test_client() as client:
            response = client.get('/resources?filter=data.category:cat-0')
            data = response.get_json()
            assert data['total'] == 9

    def test_filter_total_reflects_filtered_dataset(self, populated_store):
        with app.test_client() as client:
            unfiltered = client.get('/resources').get_json()
            filtered = client.get('/resources?filter=data.category:cat-0').get_json()
            assert filtered['total'] < unfiltered['total']
            assert filtered['total'] == 9

    def test_filter_empty_results(self, populated_store):
        with app.test_client() as client:
            response = client.get('/resources?filter=name:nonexistent')
            data = response.get_json()
            assert len(data['items']) == 0
            assert data['total'] == 0

    def test_filter_invalid_field_returns_error(self, client):
        response = client.get('/resources?filter=invalid_field:value')
        assert response.status_code == 400
        data = response.get_json()
        assert 'code' in data

    def test_filter_invalid_syntax_returns_error(self, client):
        response = client.get('/resources?filter=malformed')
        assert response.status_code == 400
        data = response.get_json()
        assert 'code' in data


class TestSortingContract:
    def test_sort_by_name_asc(self, populated_store):
        with app.test_client() as client:
            response = client.get('/resources?sort=name:asc')
            data = response.get_json()
            names = [item['name'] for item in data['items']]
            assert names == sorted(names)

    def test_sort_by_name_desc(self, populated_store):
        with app.test_client() as client:
            response = client.get('/resources?sort=name:desc')
            data = response.get_json()
            names = [item['name'] for item in data['items']]
            assert names == sorted(names, reverse=True)

    def test_sort_by_nested_field(self, populated_store):
        with app.test_client() as client:
            response = client.get('/resources?sort=data.value:asc')
            data = response.get_json()
            values = [item['data']['value'] for item in data['items']]
            assert values == sorted(values)

    def test_sort_default_direction_asc(self, populated_store):
        with app.test_client() as client:
            response = client.get('/resources?sort=name')
            data = response.get_json()
            names = [item['name'] for item in data['items']]
            assert names == sorted(names)

    def test_sort_invalid_field_returns_error(self, client):
        response = client.get('/resources?sort=invalid_field:asc')
        assert response.status_code == 400
        data = response.get_json()
        assert 'code' in data

    def test_sort_invalid_direction_returns_error(self, client):
        response = client.get('/resources?sort=name:invalid')
        assert response.status_code == 400
        data = response.get_json()
        assert 'code' in data


class TestCombinedFilterSortPagination:
    def test_combined_filter_sort_pagination(self, populated_store):
        with app.test_client() as client:
            response = client.get('/resources?filter=data.category:cat-0&sort=data.value:desc&per_page=3&page=1')
            data = response.get_json()
            assert len(data['items']) == 3
            assert data['total'] == 9
            values = [item['data']['value'] for item in data['items']]
            assert values == sorted(values, reverse=True)[:3]

    def test_combined_filter_pagination_consistent_total(self, populated_store):
        with app.test_client() as client:
            page1 = client.get('/resources?filter=data.category:cat-0&per_page=5&page=1').get_json()
            page2 = client.get('/resources?filter=data.category:cat-0&per_page=5&page=2').get_json()
            assert page1['total'] == page2['total'] == 9

    def test_combined_filter_sort_empty_results(self, populated_store):
        with app.test_client() as client:
            response = client.get('/resources?filter=name:nonexistent&sort=name:asc&page=1')
            data = response.get_json()
            assert len(data['items']) == 0
            assert data['total'] == 0


class TestTieBreakOrdering:
    def test_tie_break_by_id_when_values_equal(self, client):
        client.post('/resources', json={'name': 'a', 'data': {'value': 100}})
        client.post('/resources', json={'name': 'b', 'data': {'value': 100}})
        client.post('/resources', json={'name': 'c', 'data': {'value': 100}})
        response = client.get('/resources?sort=data.value:asc')
        data = response.get_json()
        ids = [item['id'] for item in data['items']]
        assert ids == sorted(ids)

    def test_tie_break_deterministic_across_pages(self, client):
        for i in range(15):
            client.post('/resources', json={'name': f'item-{i}', 'data': {'value': 50}})
        page1 = client.get('/resources?sort=data.value:asc&per_page=10&page=1').get_json()
        page2 = client.get('/resources?sort=data.value:asc&per_page=10&page=2').get_json()
        all_ids = [item['id'] for item in page1['items']] + [item['id'] for item in page2['items']]
        assert all_ids == sorted(all_ids)


class TestInvalidQueryParameters:
    def test_invalid_filter_operator_returns_error(self, client):
        response = client.get('/resources?filter=name>>value')
        assert response.status_code == 400

    def test_invalid_sort_format_returns_error(self, client):
        response = client.get('/resources?sort=name:asc:extra')
        assert response.status_code == 400

    def test_multiple_filter_errors_aggregated(self, client):
        response = client.get('/resources?filter=invalid_field1:val1&filter=invalid_field2:val2')
        assert response.status_code == 400
        data = response.get_json()
        assert 'errors' in data or 'code' in data

    def test_unsupported_query_param_returns_error(self, client):
        response = client.get('/resources?unknown_param=value')
        assert response.status_code == 400


class TestEmptyStoreBehavior:
    def test_empty_store_returns_empty_list(self, client):
        response = client.get('/resources')
        data = response.get_json()
        assert data['items'] == []
        assert data['total'] == 0

    def test_empty_store_pagination_returns_empty(self, client):
        response = client.get('/resources?page=1&per_page=10')
        data = response.get_json()
        assert data['items'] == []
        assert data['total'] == 0

    def test_empty_store_filter_returns_empty(self, client):
        response = client.get('/resources?filter=name:test')
        data = response.get_json()
        assert data['items'] == []
        assert data['total'] == 0

    def test_empty_store_sort_returns_empty(self, client):
        response = client.get('/resources?sort=name:asc')
        data = response.get_json()
        assert data['items'] == []
        assert data['total'] == 0