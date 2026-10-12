"""Task Manager REST API (Flask + SQLAlchemy). MySQL by default, SQLite for quick local runs/tests."""
import os
from datetime import date, datetime

from flask import Flask, jsonify, request
from sqlalchemy import (Column, Date, DateTime, ForeignKey, Integer, String, Text,
                        create_engine, func, select)
from sqlalchemy.orm import declarative_base, relationship, scoped_session, sessionmaker

Base = declarative_base()
VALID_STATUS = {"todo", "in_progress", "done"}


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), nullable=False, default="todo")
    due_date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="tasks")

    def to_dict(self):
        return {"id": self.id, "title": self.title, "description": self.description,
                "status": self.status, "due_date": self.due_date.isoformat() if self.due_date else None,
                "user_id": self.user_id}


def error(message, code):
    return jsonify({"error": message}), code


def create_app(database_url=None):
    # e.g. mysql+pymysql://user:password@localhost:3306/taskdb
    url = database_url or os.getenv("DATABASE_URL", "sqlite:///tasks.db")
    engine = create_engine(url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(bind=engine))

    app = Flask(__name__)

    @app.teardown_appcontext
    def close_session(_exc):
        Session.remove()

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    # ---- Users ----
    @app.post("/users")
    def create_user():
        data = request.get_json(silent=True) or {}
        name, email = (data.get("name") or "").strip(), (data.get("email") or "").strip().lower()
        if not name or "@" not in email:
            return error("name and a valid email are required", 400)
        s = Session()
        if s.scalar(select(User).where(User.email == email)):
            return error("email already registered", 409)
        user = User(name=name, email=email)
        s.add(user); s.commit()
        return jsonify(user.to_dict()), 201

    @app.get("/users/<int:user_id>")
    def get_user(user_id):
        user = Session().get(User, user_id)
        return jsonify(user.to_dict()) if user else error("user not found", 404)

    # ---- Tasks ----
    @app.post("/tasks")
    def create_task():
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        if not title:
            return error("title is required", 400)
        status = data.get("status", "todo")
        if status not in VALID_STATUS:
            return error(f"status must be one of {sorted(VALID_STATUS)}", 400)
        due = None
        if data.get("due_date"):
            try:
                due = date.fromisoformat(data["due_date"])
            except ValueError:
                return error("due_date must be YYYY-MM-DD", 400)
        s = Session()
        if not s.get(User, data.get("user_id")):
            return error("user_id does not exist", 400)
        task = Task(title=title, description=data.get("description"), status=status,
                    due_date=due, user_id=data["user_id"])
        s.add(task); s.commit()
        return jsonify(task.to_dict()), 201

    @app.get("/tasks")
    def list_tasks():
        q = select(Task)
        if request.args.get("status"):
            q = q.where(Task.status == request.args["status"])
        if request.args.get("user_id", type=int):
            q = q.where(Task.user_id == request.args.get("user_id", type=int))
        page = max(request.args.get("page", 1, type=int), 1)
        size = min(max(request.args.get("size", 10, type=int), 1), 100)
        s = Session()
        total = s.scalar(select(func.count()).select_from(q.subquery()))
        rows = s.scalars(q.order_by(Task.id).limit(size).offset((page - 1) * size)).all()
        return jsonify({"page": page, "size": size, "total": total, "items": [t.to_dict() for t in rows]})

    @app.get("/tasks/<int:task_id>")
    def get_task(task_id):
        task = Session().get(Task, task_id)
        return jsonify(task.to_dict()) if task else error("task not found", 404)

    @app.put("/tasks/<int:task_id>")
    def update_task(task_id):
        s = Session()
        task = s.get(Task, task_id)
        if not task:
            return error("task not found", 404)
        data = request.get_json(silent=True) or {}
        if "title" in data:
            if not str(data["title"]).strip():
                return error("title cannot be empty", 400)
            task.title = data["title"].strip()
        if "description" in data:
            task.description = data["description"]
        if "status" in data:
            if data["status"] not in VALID_STATUS:
                return error(f"status must be one of {sorted(VALID_STATUS)}", 400)
            task.status = data["status"]
        if "due_date" in data:
            try:
                task.due_date = date.fromisoformat(data["due_date"]) if data["due_date"] else None
            except ValueError:
                return error("due_date must be YYYY-MM-DD", 400)
        s.commit()
        return jsonify(task.to_dict())

    @app.delete("/tasks/<int:task_id>")
    def delete_task(task_id):
        s = Session()
        task = s.get(Task, task_id)
        if not task:
            return error("task not found", 404)
        s.delete(task); s.commit()
        return "", 204

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
