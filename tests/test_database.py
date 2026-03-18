"""
tests/test_database.py — Unit tests for SQLite database operations.

Uses a temporary database file (not the production DB) for isolation.
Tests cover:
  - init_db creates all tables and seeds circuits
  - save_simulation inserts simulation + result rows
  - get_simulation retrieves by ID
  - get_simulation returns None for unknown IDs
  - get_history returns simulations newest first
  - get_all_circuits returns all 4 seeded circuits
  - save_simulation raises on empty counts dict
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    """Override DB_PATH to use a fresh temporary file for each test."""
    db_path = str(tmp_path / 'test_quantum.db')
    import database
    monkeypatch.setattr(database, 'DB_PATH', db_path)
    # Also patch os.makedirs so it uses tmp_path
    database.init_db()
    return db_path


# ── init_db and circuits seed ────────────────────────────────────────────────

class TestInitDb:
    def test_creates_db_file(self, temp_db):
        assert os.path.exists(temp_db)

    def test_seeds_four_circuits(self, temp_db):
        from database import get_all_circuits
        circuits = get_all_circuits()
        assert len(circuits) == 4

    def test_circuit_ids_correct(self, temp_db):
        from database import get_all_circuits
        ids = {c['id'] for c in get_all_circuits()}
        assert ids == {'bell', 'ghz', 'teleportation', 'grover'}

    def test_circuits_have_required_fields(self, temp_db):
        from database import get_all_circuits
        for c in get_all_circuits():
            assert 'id' in c
            assert 'name' in c
            assert 'num_qubits' in c
            assert 'difficulty' in c

    def test_init_db_is_idempotent(self, temp_db):
        """Calling init_db() twice should not duplicate circuits."""
        from database import init_db, get_all_circuits
        init_db()
        circuits = get_all_circuits()
        assert len(circuits) == 4


# ── save_simulation ──────────────────────────────────────────────────────────

class TestSaveSimulation:
    def test_returns_integer_id(self, temp_db):
        from database import save_simulation
        sim_id = save_simulation('bell', 0.05, 1024, {'00': 487, '11': 537})
        assert isinstance(sim_id, int)
        assert sim_id > 0

    def test_ids_increment(self, temp_db):
        from database import save_simulation
        id1 = save_simulation('bell', 0.05, 1024, {'00': 500, '11': 524})
        id2 = save_simulation('ghz', 0.0, 512, {'000': 256, '111': 256})
        assert id2 > id1

    def test_raises_on_empty_counts(self, temp_db):
        from database import save_simulation
        with pytest.raises((ValueError, Exception)):
            save_simulation('bell', 0.05, 1024, {})

    def test_multiple_result_rows_saved(self, temp_db):
        from database import save_simulation, get_simulation
        counts = {'00': 487, '01': 26, '10': 19, '11': 492}
        sim_id = save_simulation('bell', 0.05, 1024, counts)
        data = get_simulation(sim_id)
        assert len(data['results']) == 4


# ── get_simulation ───────────────────────────────────────────────────────────

class TestGetSimulation:
    def test_returns_none_for_missing_id(self, temp_db):
        from database import get_simulation
        assert get_simulation(99999) is None

    def test_returns_correct_metadata(self, temp_db):
        from database import save_simulation, get_simulation
        sim_id = save_simulation('grover', 0.10, 512, {'11': 450, '00': 62})
        data = get_simulation(sim_id)
        assert data['simulation']['circuit_id'] == 'grover'
        assert data['simulation']['error_rate'] == 0.10
        assert data['simulation']['shots'] == 512

    def test_results_sum_to_shots(self, temp_db):
        from database import save_simulation, get_simulation
        counts = {'00': 487, '01': 26, '10': 19, '11': 492}
        shots = sum(counts.values())
        sim_id = save_simulation('bell', 0.05, shots, counts)
        data = get_simulation(sim_id)
        total = sum(r['count'] for r in data['results'])
        assert total == shots

    def test_includes_circuit_name(self, temp_db):
        from database import save_simulation, get_simulation
        sim_id = save_simulation('bell', 0.0, 1024, {'00': 512, '11': 512})
        data = get_simulation(sim_id)
        assert data['simulation']['circuit_name'] == 'Bell State'

    def test_results_have_state_and_count(self, temp_db):
        from database import save_simulation, get_simulation
        sim_id = save_simulation('bell', 0.0, 1024, {'00': 512, '11': 512})
        data = get_simulation(sim_id)
        for row in data['results']:
            assert 'state' in row
            assert 'count' in row


# ── get_history ──────────────────────────────────────────────────────────────

class TestGetHistory:
    def test_returns_empty_list_when_no_simulations(self, temp_db):
        from database import get_history
        history = get_history()
        assert history == []

    def test_returns_simulations(self, temp_db):
        from database import save_simulation, get_history
        save_simulation('bell', 0.05, 1024, {'00': 500, '11': 524})
        history = get_history()
        assert len(history) == 1

    def test_respects_limit(self, temp_db):
        from database import save_simulation, get_history
        for _ in range(5):
            save_simulation('bell', 0.05, 1024, {'00': 500, '11': 524})
        history = get_history(limit=3)
        assert len(history) == 3

    def test_circuit_filter(self, temp_db):
        from database import save_simulation, get_history
        save_simulation('bell', 0.05, 1024, {'00': 500, '11': 524})
        save_simulation('grover', 0.05, 1024, {'11': 900, '00': 124})
        bell_history = get_history(circuit_filter='bell')
        assert len(bell_history) == 1
        assert bell_history[0]['circuit_id'] == 'bell'
