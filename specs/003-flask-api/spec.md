# Feature Spec: Flask REST API

**Feature ID**: 003-flask-api
**Status**: Implemented

## Overview

Build a Flask REST API that exposes the quantum simulation engine and SQLite database to the
React frontend. The API provides four endpoints: list circuits, run a simulation, retrieve a
past simulation by ID, and retrieve simulation history. All responses are JSON. All errors
return a consistent `{"error": "...", "code": "..."}` shape.

## User Stories

- As a frontend developer, I want `GET /api/circuits` to return all available quantum circuits.
- As a user, I want `POST /api/simulate` to run a circuit and return measurement counts.
- As a user, I want `GET /api/results/<id>` to retrieve a past simulation by ID.
- As a user, I want `GET /api/history` to see my recent simulations.
- As a developer, I want all validation errors to return structured JSON with HTTP error codes.

## Endpoints

### GET /api/circuits
Returns list of all 4 circuits from the database.
Response 200: `{"circuits": [{id, name, num_qubits, description, difficulty}, ...]}`

### POST /api/simulate
Request body: `{"circuit": "bell", "error_rate": 0.05, "shots": 1024}`
Response 200: `{simulation_id, circuit, circuit_name, error_rate, shots, counts, ideal_counts, noise_label}`
Errors: 400 (missing/invalid fields), 422 (out of range), 500 (simulation failure)

### GET /api/results/<int:simulation_id>
Response 200: `{"simulation": {...}, "results": [{state, count}, ...]}`
Response 404: if simulation_id doesn't exist

### GET /api/history
Query params: `?limit=10&circuit=bell`
Response 200: `{"simulations": [...], "total": N}`

## Requirements

1. `circuit` field: required string, must be one of VALID_CIRCUITS.
2. `error_rate` field: required float, must be in [0.0, 0.20].
3. `shots` field: optional int, clamped to [100, 8192], defaults to 1024.
4. Request body must be a JSON object (dict), not array or primitive.
5. CORS enabled; `ALLOWED_ORIGINS` env var restricts origins in production.
6. Global handlers return JSON 404/405/500 (not Flask's default HTML pages).

## Acceptance Criteria

- [ ] `GET /api/circuits` returns 200 with 4 circuits
- [ ] `POST /api/simulate` with valid body returns 200 with counts dict
- [ ] `POST /api/simulate` with missing `circuit` returns 400 `MISSING_FIELD`
- [ ] `POST /api/simulate` with `error_rate=0.5` returns 422 `OUT_OF_RANGE`
- [ ] `GET /api/results/99999` returns 404 `NOT_FOUND`
- [ ] `GET /api/history` returns 200 with simulations list
