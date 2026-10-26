# Food Donation Management System - Codebase Explanation

## 1. Project Purpose
This project is a Flask-based web application for managing food donations. It helps track:

- Donors
- Recipients
- Donations
- Donation status such as Available or Distributed
- Dashboard summary and recent activity

The app connects to a MySQL database and renders HTML pages using Flask templates.

---

## 2. Project Structure

```text
Food_Donation_Management_System/
├── app.py                     # Main Flask application logic and route definitions
├── schema.sql                 # MySQL database schema + sample data
├── README.md                  # Basic project notes
├── requirements.txt           # Python dependencies
├── static/
│   └── style.css              # Front-end styling
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── donations.html
│   ├── donors.html
│   ├── edit_donation.html
│   ├── edit_donor.html
│   ├── edit_recipient.html
│   ├── recipients.html
│   └── setup_error.html
└── .venv/                     # Virtual environment
```

---

## 3. Where the Database Is
The project uses MySQL, not SQLite.

### Database setup file
The database is created in:

- [schema.sql](schema.sql)

This file contains:

- `CREATE DATABASE IF NOT EXISTS food_donation_db;`
- `USE food_donation_db;`
- Table definitions for `donors`, `recipients`, and `donations`
- Sample inserted records for demo data

### Database connection in code
The database connection is configured in:

- [app.py](app.py)

The app uses:

```python
mysql.connector.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    user=os.environ.get("DB_USER", "root"),
    password=os.environ.get("DB_PASSWORD", "Kansh@001"),
    database=os.environ.get("DB_NAME", "food_donation_db")
)
```

So the default database name is:

- `food_donation_db`

and it connects to:

- MySQL host: `localhost`
- MySQL user: `root`

> In short: the database is a MySQL database created by the SQL script, and the app connects to it through the `get_db_connection()` function in [app.py](app.py).

---

## 4. Database Tables
The schema in [schema.sql](schema.sql) creates these tables:

### 4.1 donors
Stores donor information.

Columns:

- `donor_id` (PK)
- `name`
- `phone`
- `email`
- `address`
- `created_at`

### 4.2 recipients
Stores recipient information.

Columns:

- `recipient_id` (PK)
- `name`
- `phone`
- `organization`
- `address`
- `created_at`

### 4.3 donations
Stores donation records.

Columns:

- `donation_id` (PK)
- `donor_id` (FK to donors)
- `recipient_id` (FK to recipients, optional)
- `food_name`
- `quantity`
- `unit`
- `expiry_time`
- `status`
- `notes`
- `created_at`

Status values:

- `Available`
- `Distributed`
- `Expired`

---

## 5. How the App Works
The main logic is in [app.py](app.py).

### Core functions

#### `get_db_connection()`
Creates a MySQL database connection.

#### `query_db(sql, params=None, fetch=False)`
Runs SQL queries and optionally fetches rows.

This function is used across the app to:

- insert records
- update records
- delete records
- fetch lists for forms and dashboard pages

---

## 6. API Endpoints / Routes
This project is mainly a server-rendered web app, not a REST API in the traditional JSON-style sense. The routes accept form submissions and render HTML pages.

### Dashboard

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Displays summary stats and recent donations |

#### Example behavior
- Count total donations
- Count available donations
- Count distributed donations
- Count recipients
- Show latest donation entries

---

### Donors

| Route | Method | Purpose |
|---|---|---|
| `/donors` | GET | View all donors |
| `/donors` | POST | Add a new donor |
| `/donors/<donor_id>/edit` | GET | Load donor edit form |
| `/donors/<donor_id>/edit` | POST | Update donor |
| `/donors/<donor_id>/delete` | POST | Delete donor |

#### Logic summary
- Add donor with name, phone, email, address
- Edit donor details
- Delete donor if not linked to donation references

---

### Recipients

| Route | Method | Purpose |
|---|---|---|
| `/recipients` | GET | View all recipients |
| `/recipients` | POST | Add a new recipient |
| `/recipients/<recipient_id>/edit` | GET | Load recipient edit form |
| `/recipients/<recipient_id>/edit` | POST | Update recipient |
| `/recipients/<recipient_id>/delete` | POST | Delete recipient |

#### Logic summary
- Add recipient with name, phone, organization, address
- Edit recipient info
- Delete recipient if not linked to donation references

---

### Donations

| Route | Method | Purpose |
|---|---|---|
| `/donations` | GET | View all donation records |
| `/donations` | POST | Add a donation |
| `/donations/<donation_id>/edit` | GET | Load donation edit form |
| `/donations/<donation_id>/edit` | POST | Update donation |
| `/donations/<donation_id>/assign` | POST | Assign a donation to a recipient and mark as Distributed |
| `/donations/<donation_id>/delete` | POST | Delete a donation |

#### Logic summary
- Record food donation details
- Set donor and quantity
- Optionally assign to recipient
- Update status to `Distributed`
- Display donation details on the page

---

## 7. Main App Flow
### Request flow example
1. User visits `/donors`
2. Flask route in [app.py](app.py) handles the request
3. SQL query runs against MySQL
4. Results are sent to a template in the [templates](templates) folder
5. Browser renders HTML page

### Example
For a donor add operation:

- Form submits to `POST /donors`
- Name, phone, email, address are retrieved from `request.form`
- Query inserts a row into `donors`
- App redirects back to `/donors`

---

## 8. Templates Folder
The HTML pages are stored in [templates](templates):

- [templates/dashboard.html](templates/dashboard.html) - dashboard summary page
- [templates/donors.html](templates/donors.html) - donor list and add form
- [templates/recipients.html](templates/recipients.html) - recipient list and add form
- [templates/donations.html](templates/donations.html) - donation list and add form
- [templates/edit_donor.html](templates/edit_donor.html) - donor edit form
- [templates/edit_recipient.html](templates/edit_recipient.html) - recipient edit form
- [templates/edit_donation.html](templates/edit_donation.html) - donation edit form
- [templates/setup_error.html](templates/setup_error.html) - database connection error page

These pages render data from the database and allow CRUD operations.

---

## 9. How Data is Related
This is a small relational database system.

### Relationships
- Each donation belongs to one donor
- Each donation may be assigned to one recipient
- Donors and recipients are independent entities

### Foreign keys
The `donations` table links to:

- `donors.donor_id`
- `recipients.recipient_id`

This keeps the donation records tied to actual donor and recipient entries.

---

## 10. Example Data Flow
A normal donation workflow is:

1. Add donor to `donors`
2. Add recipient to `recipients`
3. Add donation to `donations`
4. Select recipient in the donor assignment section
5. Donation status becomes `Distributed`
6. Dashboard updates totals from database queries

---

## 11. Running the App
The application is started with Flask:

```bash
python app.py
```

When run, Flask starts the local web server in debug mode:

```python
if __name__ == "__main__":
    app.run(debug=True)
```

---

## 12. Important Notes
- This is not a separate REST API using JSON endpoints.
- It is a form-based web app using HTML templates.
- The database is expected to be running on MySQL locally.
- If MySQL is not configured correctly, the app shows the error page from [templates/setup_error.html](templates/setup_error.html).

---

## 13. Summary
This codebase is a small but complete food donation system built with:

- Flask for the application layer
- MySQL for data storage
- HTML templates for the interface
- SQL relationships to manage donors, recipients, and donations

The central files are:

- [app.py](app.py) — application logic and routes
- [schema.sql](schema.sql) — database structure and sample records
- [templates](templates) — UI pages
- [static/style.css](static/style.css) — styling

If you need a beginner-friendly explanation of each function and route, this project is easy to understand by reading [app.py](app.py) first, then [schema.sql](schema.sql).
