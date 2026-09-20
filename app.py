import os
from flask import Flask, render_template, request, redirect, flash

from db import get_db, init_db, close_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "samaritan-cs50-secret-dev-key")

app.config["DATABASE"] = "samaritan.db"

app.teardown_appcontext(close_db)

@app.route("/")
def index():
  return render_template("layout.html")

@app.route("/beneficiaries", methods=["GET", "POST"])
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
    