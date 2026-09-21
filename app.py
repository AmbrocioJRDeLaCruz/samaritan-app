import os
from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db, init_db, close_db, login_required

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "samaritan-cs50-secret-dev-key")

app.config["DATABASE"] = "samaritan.db"

app.teardown_appcontext(close_db)

@app.after_request
def after_request(response):
    """
    Asegura que las respuestas del servidor no sean cacheadas por el navegador.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
  
@app.route("/")
@login_required
def index():
  """
  Panel Principal (Dashboard)
  Muestra métricas generales y el listado de casos de ayuda comunitarias.
  """
  with get_db() as conn:
    total_beneficiaries = conn.execute("SELECT COUNT(*) FROM beneficiaries").fetchone()[0]
    total_cases = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
    pending_cases = conn.execute("SELECT COUNT(*) FROM cases WHERE status = 'pending'").fetchone()[0]
    in_progress_cases = conn.execute("SELECT COUNT(*) FROM cases WHERE status = 'in_progress'").fetchone()[0]
    completed_cases = conn.execute("SELECT COUNT(*) FROM cases WHERE status = 'complete'").fetchone()[0]
    
    status_filter = request.args.get("status")
    search_query = request.args.get("q")

    base_query ="""
      SELECT c.id, c.case_type, c.category, c.description, c.status, c.created_at,
      b.name AS beneficiary_name
      FROM cases c 
      JOIN beneficiaries b ON c.beneficiary_id = b.id
    """
    
    where_clauses = []
    params = []
    
    if status_filter:
      where_clauses.append("c.status = ?")
      params.append(status_filter)
    if search_query:
      where_clauses.append("(c.description LIKE ? OR b.name LIKE ?)")
      params.extend([f"%{search_query}%", f"%{search_query}%"])
    
    if where_clauses:
      base_query += " WHERE " + " AND ".join(where_clauses)
    
    base_query += " ORDER BY c.created_at DESC;"
    
    with get_db() as conn:
      cases = conn.execute(base_query, params).fetchall()
  
  return render_template(
    "index.html",
    total_beneficiaries=total_beneficiaries,
    total_cases=total_cases,
    pending_cases=pending_cases,
    in_progress_cases=in_progress_cases,
    completed_cases=completed_cases,
    cases=cases
  )
    
@app.route("/register", methods=["GET", "POST"])
def register():
  """Registro de nuevos voluntarios en la plataforma
  """
  if request.method == "POST":
    name = request.form.get("name").strip()
    email = request.form.get("email").strip().lower()
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    
    if not name:
      flash("El nombre es obligatorio.", "error")
      return redirect("/register")
    if not email:
      flash("El correo electrónico es obligatorio.", "error")
      return redirect("/register")
    if not password:
      flash("La contraseña es obligatoria.", "error")
      return redirect("/register")
    if password != confirm_password:
      flash("Las contraseñas no coinciden.", "error")
      return redirect("/register")
    
    hashed_password = generate_password_hash(password)
    
    with get_db() as conn:
      existing_user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
      if existing_user:
        flash("El correo electrónico ya está registrado.", "error")
        return redirect("/register")
      
      conn.execute(
        "INSERT INTO users (name, email, hash) VALUES (?, ?, ?)",
        (name, email, hashed_password)
      )
      conn.commit()
      
      return redirect("/login.html")
    
  return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
  """Inicio de sesión para voluntarios registrados
  """
  if request.method == "POST":
    email = request.form.get("email").strip().lower()
    password = request.form.get("password")
    
    if not email or not password:
      flash("Correo electrónico y contraseña son obligatorios.", "error")
      return redirect("/login")
    
    with get_db() as conn:
      user = conn.execute("SELECT id, name, hash FROM users WHERE email = ?", (email,)).fetchone()
      
      if user is None or not check_password_hash(user["hash"], password):
        flash("Correo electrónico o contraseña incorrectos.", "error")
        return redirect("/login")
      
      session.clear()
      session["user_id"] = user["id"]
      session["user_name"] = user["name"]
      
      return redirect("/")
  
  return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
  """
    Cerrar la sesión del voluntario actual
  """
  session.clear()
  flash("Has cerrado sesión exitosamente.", "success")
  return redirect("/login")

@app.route("/beneficiaries", methods=["GET", "POST"])
@login_required
def beneficiaries():
  if request.method == "POST":
    name = request.form.get("name")
    phone = request.form.get("phone")
    location = request.form.get("location")
    household_size = request.form.get("household_size")
    notes = request.form.get("notes")
    
    if not name:
      flash("Name is required.", "error")
      return redirect("/beneficiaries")
    
    with get_db() as conn:
      conn.execute(
        "INSERT INTO beneficiaries (name, phone, location, household_size, notes) VALUES (?, ?, ?, ?, ?)",
        (name, phone, location, household_size, notes)
      )
      conn.commit()
    
    
    return redirect("/beneficiaries")
  
  with get_db() as conn:
    all_beneficiaries = conn.execute("SELECT * FROM beneficiaries ORDER BY name ASC").fetchall()
    
  return render_template("beneficiaries.html", beneficiaries=all_beneficiaries)

@app.route("/cases/new", methods=["GET", "POST"])
@login_required
def new_case():
  with get_db() as conn:
    if request.method == "POST":
      beneficiary_id = request.form.get("beneficiary_id")
      case_type = request.form.get("case_type")
      category = request.form.get("category")
      description = request.form.get("description")
      
      if not beneficiary_id or not case_type:
        flash("Beneficiary and Case Type are required.", "error")
        return redirect("/cases/new")
      
      conn.execute(
        "INSERT INTO cases (beneficiary_id, case_type, category, description) VALUES (?, ?, ?, ?)",
        (beneficiary_id, case_type, category, description)
      )
      conn.commit()
      
      flash("Case created successfully.", "success")
      return redirect("/")
    
    selected_id = request.args.get("beneficiary_id")
    beneficiaries_list = conn.execute("SELECT id, name, phone, location FROM beneficiaries ORDER BY name ASC;").fetchall()
  
  return render_template("new_case.html", beneficiaries=beneficiaries_list, selected_beneficiary_id=selected_id)

@app.route("/cases/<int:case_id>")
@login_required
def case_detail(case_id):
  with get_db() as conn:
    case = conn.execute("""
      SELECT 
        c.id, c.case_type, c.category, c.description, 
        b.id AS beneficiary_id, b.name AS beneficiary_name, b.phone AS beneficiary_phone,
        b.location AS beneficiary_location, b.household_size
      FROM cases c JOIN beneficiaries b ON c.beneficiary_id = b.id WHERE c.id = ?;
      """,(case_id,)).fetchone()
    
    if case is None:
      flash("Case not found.", "error")
      return redirect("/")
    
  return render_template("case_detail.html", case=case)

app.run(debug=True)

@app.route("/cases/<int:case_id>/status", method=["POST"])
@login_required
def update_case_status(case_id):
  """
  Actualiza el estado de atención de un caso (Pendiente, En progreso, Completado).
  """
  new_status = request.form.get("status")
  if new_status in ["pending", "in_progress", "complete"]:
    with get_db() as conn:
      conn.execute("UPDATE cases SET status = ? WHERE id = ?", (new_status, case_id))
      flash("Estado del caso actualizado correctamente.", "success")
  else:
    flash("Estado inválido.", "error")
    
  return redirect(f"/cases/{case_id}")

if __name__ == "__main__":
  with app.app_context():
    init_db()
    