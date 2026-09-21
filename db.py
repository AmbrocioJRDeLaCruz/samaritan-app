import sqlite3
from datetime import datetime
from functools import wraps

from flask import current_app, g, session, redirect

def get_db():
  if "db" not in g:
    g.db = sqlite3.connect(
      current_app.config["DATABASE"],
      detect_types=sqlite3.PARSE_DECLTYPES
    )
    g.db.row_factory = sqlite3.Row
  return g.db
    
def close_db(e=None):
  db = g.pop("db", None)
  
  if db is not None:
    db.close()
    
def init_db():
  db = get_db()
  
  with current_app.open_resource("schema.sql") as f:
    db.executescript(f.read().decode("utf-8"))

sqlite3.register_converter(
  "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def login_required(f):
  """
    Decorador para proteger rutas que requieren autenticación.
    Si el usuario no ha iniciado sesión en session["user_id"], redirige a /login.
  """
  @wraps(f)
  def wrapper(*args, **kwargs):
    if session.get("user_id") is None:
      return redirect("/login")
    return f(*args, **kwargs)
  return wrapper