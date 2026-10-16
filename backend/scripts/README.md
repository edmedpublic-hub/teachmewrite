# Backend Scripts

Utility scripts for development, testing, and maintenance. These are not part of the Django application — they're support tools.

## Test Scripts

| Script | Purpose |
|--------|---------|
| `complete_backend_test.py` | End-to-end backend test — exercises the full API surface |
| `quick_test.py` | Quick smoke test — verifies core endpoints work |
| `test_engine.py` | Unit tests for the mastery engine logic |

## Development Utilities

| Script | Purpose |
|--------|---------|
| `refresh_db.py` | Resets the local database and re-runs migrations |
| `migrate_fresh.ps1` | Windows helper for fresh migration + seed workflow |

## Usage

All scripts should be run from the `backend/` directory with the virtual environment activated:

```bash
cd backend
.\venv\Scripts\activate    # Windows
python scripts/complete_backend_test.py