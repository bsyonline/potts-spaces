import pytest
import threading
import time
from app import app, ConfigManager, reload_config, get_config, validate_config


class TestConfigReload:
    def test_config_reload_valid_succeeds(self):
        with app.test_client() as client:
            new_config = {
                'max_requests_per_second': 100,
                'timeout_seconds': 30,
                'feature_flags': {'new_api': True}
            }
            response = client.post('/admin/config/reload', json={'config': new_config})
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            assert data['config']['max_requests_per_second'] == 100
            
    def test_config_reload_invalid_rejected_without_partial_apply(self):
        with app.test_client() as client:
            invalid_config = {
                'max_requests_per_second': -10,
                'timeout_seconds': 0,
                'feature_flags': {}
            }
            old_config = client.get('/admin/config').get_json()['config']
            response = client.post('/admin/config/reload', json={'config': invalid_config})
            assert response.status_code == 400
            data = response.get_json()
            assert 'errors' in data
            assert len(data['errors']) > 0
            
            current_config = client.get('/admin/config').get_json()['config']
            assert current_config == old_config
            
    def test_config_reload_concurrent_reads_no_interruption(self):
        errors = []
        read_count = 0
        
        def concurrent_reader():
            nonlocal read_count
            with app.test_client() as client:
                for _ in range(50):
                    response = client.get('/admin/config')
                    if response.status_code != 200:
                        errors.append(f'Read failed: {response.status_code}')
                    data = response.get_json()
                    if 'config' not in data:
                        errors.append('Missing config in response')
                    read_count += 1
                    
        reader_thread = threading.Thread(target=concurrent_reader)
        reader_thread.start()
        
        time.sleep(0.01)
        
        with app.test_client() as client:
            new_config = {'max_requests_per_second': 200, 'timeout_seconds': 60}
            client.post('/admin/config/reload', json={'config': new_config})
            
        reader_thread.join()
        
        assert len(errors) == 0, f'Errors during concurrent reads: {errors}'
        assert read_count == 50
        
    def test_validate_config_actionable_errors(self):
        invalid_config = {
            'max_requests_per_second': -5,
            'timeout_seconds': -1
        }
        errors = validate_config(invalid_config)
        assert len(errors) >= 2
        for error in errors:
            assert 'field' in error
            assert 'message' in error
            assert 'expected' in error or 'constraint' in error

    def test_config_manager_rollback_restores_previous_config(self):
        manager = ConfigManager()
        original_config = manager.get_config()
        new_config = {'max_requests_per_second': 999, 'timeout_seconds': 99}
        manager.reload_config(new_config)
        assert manager.get_config()['max_requests_per_second'] == 999
        manager.rollback(original_config)
        assert manager.get_config() == original_config

    def test_config_manager_rollback_thread_safe(self):
        manager = ConfigManager()
        original_config = manager.get_config()
        new_config = {'max_requests_per_second': 500, 'timeout_seconds': 50}
        manager.reload_config(new_config)
        errors = []

        def concurrent_rollback():
            try:
                for _ in range(20):
                    manager.rollback(original_config)
                    manager.reload_config(new_config)
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=concurrent_rollback) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f'Thread safety errors: {errors}'
        final_config = manager.get_config()
        assert 'max_requests_per_second' in final_config
