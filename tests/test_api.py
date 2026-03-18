"""
tests/test_api.py — Integration tests for Flask API endpoints.

Uses Flask's built-in test client (no real HTTP). Quantum simulations are
mocked to keep tests fast and deterministic.

Tests cover:
  - GET /api/circuits returns 200 with 4 circuits
  - POST /api/simulate validation (missing fields, wrong types, out of range)
  - POST /api/simulate success path (mocked simulation)
  - GET /api/results/<id> returns 200 or 404
  - GET /api/history returns 200 with simulations list
  - Global error handlers return JSON (not HTML)
"""

import pytest
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


@pytest.fixture
def app(monkeypatch, tmp_path):
    """Create a Flask test app with a temporary database."""
    # Point database at a temp file
    import database
    monkeypatch.setattr(database, 'DB_PATH', str(tmp_path / 'test.db'))
    database.init_db()

    # Mock run_named_circuit to avoid running Qiskit in API tests
    import quantum_engine
    monkeypatch.setattr(
        quantum_engine,
        'run_named_circuit',
        lambda name, error_rate, shots: {'00': shots // 2, '11': shots - shots // 2}
    )

    import app as flask_app
    flask_app.app.config['TESTING'] = True
    return flask_app.app


@pytest.fixture
def client(app):
    return app.test_client()


# ── GET /api/circuits ────────────────────────────────────────────────────────

class TestApiCircuits:
    def test_returns_200(self, client):
        response = client.get('/api/circuits')
        assert response.status_code == 200

    def test_returns_json(self, client):
        response = client.get('/api/circuits')
        assert response.content_type == 'application/json'

    def test_returns_four_circuits(self, client):
        data = client.get('/api/circuits').get_json()
        assert len(data['circuits']) == 4

    def test_circuits_have_id_field(self, client):
        data = client.get('/api/circuits').get_json()
        for c in data['circuits']:
            assert 'id' in c

    def test_circuit_ids_include_bell(self, client):
        data = client.get('/api/circuits').get_json()
        ids = [c['id'] for c in data['circuits']]
        assert 'bell' in ids


# ── POST /api/simulate — validation ─────────────────────────────────────────

class TestApiSimulateValidation:
    def test_missing_body_returns_400(self, client):
        response = client.post('/api/simulate', data='not json',
                               content_type='application/json')
        assert response.status_code == 400

    def test_missing_circuit_returns_400(self, client):
        response = client.post('/api/simulate',
                               json={'error_rate': 0.05, 'shots': 1024})
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 'MISSING_FIELD'

    def test_missing_error_rate_returns_400(self, client):
        response = client.post('/api/simulate',
                               json={'circuit': 'bell', 'shots': 1024})
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 'MISSING_FIELD'

    def test_invalid_circuit_name_returns_400(self, client):
        response = client.post('/api/simulate',
                               json={'circuit': 'fake_circuit', 'error_rate': 0.05})
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 'INVALID_CIRCUIT'

    def test_error_rate_too_high_returns_422(self, client):
        response = client.post('/api/simulate',
                               json={'circuit': 'bell', 'error_rate': 0.5})
        assert response.status_code == 422
        data = response.get_json()
        assert data['code'] == 'OUT_OF_RANGE'

    def test_error_rate_negative_returns_422(self, client):
        response = client.post('/api/simulate',
                               json={'circuit': 'bell', 'error_rate': -0.1})
        assert response.status_code == 422

    def test_non_string_circuit_returns_400(self, client):
        response = client.post('/api/simulate',
                               json={'circuit': 123, 'error_rate': 0.05})
        assert response.status_code == 400

    def test_non_dict_body_returns_400(self, client):
        response = client.post('/api/simulate',
                               data=json.dumps([1, 2, 3]),
                               content_type='application/json')
        assert response.status_code == 400


# ── POST /api/simulate — success ─────────────────────────────────────────────

class TestApiSimulateSuccess:
    def test_returns_200(self, client):
        response = client.post('/api/simulate',
                               json={'circuit': 'bell', 'error_rate': 0.05})
        assert response.status_code == 200

    def test_response_has_simulation_id(self, client):
        data = client.post('/api/simulate',
                           json={'circuit': 'bell', 'error_rate': 0.05}).get_json()
        assert 'simulation_id' in data
        assert isinstance(data['simulation_id'], int)

    def test_response_has_counts(self, client):
        data = client.post('/api/simulate',
                           json={'circuit': 'bell', 'error_rate': 0.05}).get_json()
        assert 'counts' in data
        assert isinstance(data['counts'], dict)

    def test_response_has_ideal_counts(self, client):
        data = client.post('/api/simulate',
                           json={'circuit': 'bell', 'error_rate': 0.05}).get_json()
        assert 'ideal_counts' in data

    def test_response_has_noise_label(self, client):
        data = client.post('/api/simulate',
                           json={'circuit': 'bell', 'error_rate': 0.05}).get_json()
        assert 'noise_label' in data
        assert isinstance(data['noise_label'], str)

    def test_shots_defaults_to_1024(self, client):
        data = client.post('/api/simulate',
                           json={'circuit': 'bell', 'error_rate': 0.0}).get_json()
        assert data['shots'] == 1024

    def test_custom_shots_respected(self, client):
        data = client.post('/api/simulate',
                           json={'circuit': 'bell', 'error_rate': 0.0, 'shots': 512}).get_json()
        assert data['shots'] == 512


# ── GET /api/results/<id> ────────────────────────────────────────────────────

class TestApiResults:
    def test_missing_id_returns_404(self, client):
        response = client.get('/api/results/99999')
        assert response.status_code == 404
        data = response.get_json()
        assert data['code'] == 'NOT_FOUND'

    def test_existing_id_returns_200(self, client):
        # First create a simulation
        post_data = client.post('/api/simulate',
                                json={'circuit': 'bell', 'error_rate': 0.0}).get_json()
        sim_id = post_data['simulation_id']
        response = client.get(f'/api/results/{sim_id}')
        assert response.status_code == 200

    def test_response_has_simulation_key(self, client):
        post_data = client.post('/api/simulate',
                                json={'circuit': 'bell', 'error_rate': 0.0}).get_json()
        sim_id = post_data['simulation_id']
        data = client.get(f'/api/results/{sim_id}').get_json()
        assert 'simulation' in data
        assert 'results' in data


# ── GET /api/history ─────────────────────────────────────────────────────────

class TestApiHistory:
    def test_returns_200(self, client):
        assert client.get('/api/history').status_code == 200

    def test_returns_simulations_key(self, client):
        data = client.get('/api/history').get_json()
        assert 'simulations' in data
        assert 'total' in data

    def test_total_matches_list_length(self, client):
        data = client.get('/api/history').get_json()
        assert data['total'] == len(data['simulations'])

    def test_invalid_circuit_filter_returns_400(self, client):
        response = client.get('/api/history?circuit=fake')
        assert response.status_code == 400

    def test_limit_param_respected(self, client):
        # Create 3 simulations
        for _ in range(3):
            client.post('/api/simulate', json={'circuit': 'bell', 'error_rate': 0.0})
        data = client.get('/api/history?limit=2').get_json()
        assert len(data['simulations']) <= 2


# ── Error handlers ───────────────────────────────────────────────────────────

class TestErrorHandlers:
    def test_404_returns_json(self, client):
        response = client.get('/api/nonexistent_route_xyz')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data

    def test_405_returns_json(self, client):
        response = client.get('/api/simulate')  # GET on POST-only endpoint
        assert response.status_code == 405
        data = response.get_json()
        assert 'code' in data
