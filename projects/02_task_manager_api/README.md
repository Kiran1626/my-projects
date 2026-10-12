# Task Manager REST API

**Stack:** Python, Flask, SQLAlchemy, MySQL, Postman, Git/GitHub

A REST API for users and tasks with validation, filtering and pagination.

## Run
```bash
pip install -r requirements.txt
# Option A: quick start with SQLite (no setup)
python app.py
# Option B: MySQL
mysql -u root -p < schema.sql
export DATABASE_URL="mysql+pymysql://root:yourpassword@localhost:3306/taskdb"
python app.py
```
Test: `python -m pytest -q` (5 tests, uses in-memory SQLite). Import `postman_collection.json` into Postman to try every endpoint.

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | /health | Health check |
| POST | /users | Create user (name, email; 409 on duplicate email) |
| GET | /users/{id} | Get user |
| POST | /tasks | Create task (title, user_id, optional status, due_date, description) |
| GET | /tasks?status=&user_id=&page=&size= | List with filter and pagination |
| GET | /tasks/{id} | Get task |
| PUT | /tasks/{id} | Update task |
| DELETE | /tasks/{id} | Delete task (204) |

Status values: `todo`, `in_progress`, `done`. Errors return JSON `{"error": "..."}` with 400/404/409.

## Design notes
Normalised schema with a foreign key from `tasks.user_id` to `users.id` and an index on `(user_id, status)`. Input is validated before it reaches the database.
