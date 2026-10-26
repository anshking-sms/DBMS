from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-development-key")

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "Kansh@001"),
        database=os.environ.get("DB_NAME", "food_donation_db")
    )
def query_db(sql, params=None, fetch=False):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        result = cursor.fetchall() if fetch else None
        if not fetch:
            conn.commit()
        return result
    finally:
        cursor.close()
        conn.close()

@app.route("/")
def dashboard():
    try:
        stats = {
            "donations": query_db("SELECT COUNT(*) AS n FROM donations", fetch=True)[0]["n"],
            "available": query_db("SELECT COUNT(*) AS n FROM donations WHERE status='Available'", fetch=True)[0]["n"],
            "distributed": query_db("SELECT COUNT(*) AS n FROM donations WHERE status='Distributed'", fetch=True)[0]["n"],
            "recipients": query_db("SELECT COUNT(*) AS n FROM recipients", fetch=True)[0]["n"],
        }
        recent = query_db("""
            SELECT d.donation_id, d.food_name, d.quantity, d.unit, d.expiry_time,
                   d.status, dn.name AS donor_name, r.name AS recipient_name
            FROM donations d
            JOIN donors dn ON d.donor_id = dn.donor_id
            LEFT JOIN recipients r ON d.recipient_id = r.recipient_id
            ORDER BY d.created_at DESC LIMIT 8
        """, fetch=True)
        return render_template("dashboard.html", stats=stats, recent=recent)
    except Error as e:
        return render_template("setup_error.html", error=str(e))

@app.route("/donors", methods=["GET", "POST"])
def donors():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        if not name:
            flash("Donor name is required.", "error")
        else:
            try:
                query_db("INSERT INTO donors (name, phone, email, address) VALUES (%s,%s,%s,%s)",
                         (name, phone or None, email or None, address or None))
                flash("Donor added successfully.", "success")
                return redirect(url_for("donors"))
            except Error as e:
                flash(f"Could not add donor: {e}", "error")
    rows = query_db("SELECT * FROM donors ORDER BY donor_id DESC", fetch=True)
    return render_template("donors.html", donors=rows)

@app.route("/donors/<int:donor_id>/edit", methods=["GET", "POST"])
def edit_donor(donor_id):
    donor = query_db("SELECT * FROM donors WHERE donor_id=%s", (donor_id,), True)
    if not donor:
        flash("Donor not found.", "error")
        return redirect(url_for("donors"))
    donor = donor[0]
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Donor name is required.", "error")
            return render_template("edit_donor.html", donor=donor)
        query_db("""UPDATE donors SET name=%s, phone=%s, email=%s, address=%s
                    WHERE donor_id=%s""",
                 (name, request.form.get("phone") or None, request.form.get("email") or None,
                  request.form.get("address") or None, donor_id))
        flash("Donor updated successfully.", "success")
        return redirect(url_for("donors"))
    return render_template("edit_donor.html", donor=donor)

@app.route("/donors/<int:donor_id>/delete", methods=["POST"])
def delete_donor(donor_id):
    try:
        query_db("DELETE FROM donors WHERE donor_id=%s", (donor_id,))
        flash("Donor deleted. Donors with existing donations cannot be deleted.", "success")
    except Error:
        flash("Cannot delete this donor because donation records reference them.", "error")
    return redirect(url_for("donors"))

@app.route("/recipients", methods=["GET", "POST"])
def recipients():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        organization = request.form.get("organization", "").strip()
        address = request.form.get("address", "").strip()
        if not name:
            flash("Recipient name is required.", "error")
        else:
            query_db("INSERT INTO recipients (name, phone, organization, address) VALUES (%s,%s,%s,%s)",
                     (name, phone or None, organization or None, address or None))
            flash("Recipient added successfully.", "success")
            return redirect(url_for("recipients"))
    rows = query_db("SELECT * FROM recipients ORDER BY recipient_id DESC", fetch=True)
    return render_template("recipients.html", recipients=rows)

@app.route("/recipients/<int:recipient_id>/edit", methods=["GET", "POST"])
def edit_recipient(recipient_id):
    recipient = query_db("SELECT * FROM recipients WHERE recipient_id=%s", (recipient_id,), True)
    if not recipient:
        flash("Recipient not found.", "error")
        return redirect(url_for("recipients"))
    recipient = recipient[0]
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Recipient name is required.", "error")
            return render_template("edit_recipient.html", recipient=recipient)
        query_db("""UPDATE recipients SET name=%s, phone=%s, organization=%s, address=%s
                    WHERE recipient_id=%s""",
                 (name, request.form.get("phone") or None, request.form.get("organization") or None,
                  request.form.get("address") or None, recipient_id))
        flash("Recipient updated successfully.", "success")
        return redirect(url_for("recipients"))
    return render_template("edit_recipient.html", recipient=recipient)

@app.route("/recipients/<int:recipient_id>/delete", methods=["POST"])
def delete_recipient(recipient_id):
    try:
        query_db("DELETE FROM recipients WHERE recipient_id=%s", (recipient_id,))
        flash("Recipient deleted.", "success")
    except Error:
        flash("Cannot delete this recipient because donation records reference them.", "error")
    return redirect(url_for("recipients"))

@app.route("/donations", methods=["GET", "POST"])
def donations():
    if request.method == "POST":
        try:
            donor_id = int(request.form["donor_id"])
            food_name = request.form["food_name"].strip()
            quantity = float(request.form["quantity"])
            unit = request.form["unit"]
            expiry_time = request.form.get("expiry_time") or None
            notes = request.form.get("notes", "").strip() or None
            if not food_name or quantity <= 0:
                raise ValueError("Enter a food name and a quantity greater than zero.")
            query_db("""INSERT INTO donations
                (donor_id, food_name, quantity, unit, expiry_time, notes, status)
                VALUES (%s,%s,%s,%s,%s,%s,'Available')""",
                (donor_id, food_name, quantity, unit, expiry_time, notes))
            flash("Donation recorded successfully.", "success")
            return redirect(url_for("donations"))
        except (ValueError, KeyError) as e:
            flash(str(e) or "Please check the donation details.", "error")
        except Error as e:
            flash(f"Could not save donation: {e}", "error")
    donors_list = query_db("SELECT donor_id, name FROM donors ORDER BY name", fetch=True)
    recipients_list = query_db("SELECT recipient_id, name FROM recipients ORDER BY name", fetch=True)
    rows = query_db("""
        SELECT d.*, dn.name AS donor_name, r.name AS recipient_name
        FROM donations d JOIN donors dn ON d.donor_id=dn.donor_id
        LEFT JOIN recipients r ON d.recipient_id=r.recipient_id
        ORDER BY d.donation_id DESC
    """, fetch=True)
    return render_template("donations.html", donations=rows, donors=donors_list, recipients=recipients_list)

@app.route("/donations/<int:donation_id>/edit", methods=["GET", "POST"])
def edit_donation(donation_id):
    result = query_db("SELECT * FROM donations WHERE donation_id=%s", (donation_id,), True)
    if not result:
        flash("Donation not found.", "error")
        return redirect(url_for("donations"))
    donation = result[0]
    donors_list = query_db("SELECT donor_id, name FROM donors ORDER BY name", fetch=True)
    if request.method == "POST":
        try:
            donor_id = int(request.form["donor_id"])
            food_name = request.form["food_name"].strip()
            quantity = float(request.form["quantity"])
            unit = request.form["unit"]
            expiry_time = request.form.get("expiry_time") or None
            notes = request.form.get("notes", "").strip() or None
            status = request.form["status"]
            if not food_name or quantity <= 0:
                raise ValueError("Enter a food name and quantity greater than zero.")
            query_db("""UPDATE donations SET donor_id=%s, food_name=%s, quantity=%s,
                unit=%s, expiry_time=%s, notes=%s, status=%s WHERE donation_id=%s""",
                (donor_id, food_name, quantity, unit, expiry_time, notes, status, donation_id))
            flash("Donation updated successfully.", "success")
            return redirect(url_for("donations"))
        except (ValueError, KeyError) as e:
            flash(str(e) or "Please check the details.", "error")
        except Error as e:
            flash(f"Could not update donation: {e}", "error")
    return render_template("edit_donation.html", donation=donation, donors=donors_list)

@app.route("/donations/<int:donation_id>/assign", methods=["POST"])
def assign_donation(donation_id):
    recipient_id = request.form.get("recipient_id")
    if not recipient_id:
        flash("Choose a recipient first.", "error")
    else:
        try:
            query_db("""UPDATE donations SET recipient_id=%s, status='Distributed'
                        WHERE donation_id=%s AND status='Available'""",
                     (int(recipient_id), donation_id))
            flash("Donation marked as distributed.", "success")
        except Error as e:
            flash(f"Could not assign donation: {e}", "error")
    return redirect(url_for("donations"))

@app.route("/donations/<int:donation_id>/delete", methods=["POST"])
def delete_donation(donation_id):
    query_db("DELETE FROM donations WHERE donation_id=%s", (donation_id,))
    flash("Donation record deleted.", "success")
    return redirect(url_for("donations"))

if __name__ == "__main__":
    app.run(debug=True)
