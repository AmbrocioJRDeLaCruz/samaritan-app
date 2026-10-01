# SAMARITAN: COMMUNITY ASSISTANCE & VOLUNTEER MANAGEMENT PLATFORM
#### Video: https://youtu.be/wkp6lFmQPDY
#### Description:

Samaritan is a lightweight, responsive web application engineered to streamline humanitarian aid, community outreach, and volunteer task coordination for non-profit organizations, local churches, and civic assistance groups. In many community-driven initiatives, tracking families in vulnerable conditions and matching them with available aid resources is still performed using fragmented spreadsheets, messaging groups, or paper notes. This lack of centralized tracking often leads to duplicated efforts, neglected cases, and an inability to measure the real impact of community relief operations.

Samaritan addresses this coordination bottleneck by providing a structured, relational management system where volunteers can register beneficiaries, document specific emergency needs (such as food baskets, medical supplies, housing repairs, or financial relief), claim cases for personal follow-up, and track the status of each case from initiation to final resolution.

---

### Core Features & Functionality

1. **Volunteer Authentication & Access Control:**
   * Secure registration and login workflows ensuring that sensitive beneficiary personal information is never exposed to the unauthenticated public.
   * Session-based state management using HTTP-only signed cookies, enforced through custom route-protection decorators.
   * Cryptographic password hashing using `werkzeug.security` (PBKDF2 with SHA-256) to ensure robust credential protection.

2. **Beneficiary Directory & Demographics:**
   * Centralized cataloging of vulnerable individuals and families.
   * Demographic data tracking, including primary contact phone numbers, physical residential locations, household size, and background context notes.
   * One-click transition to spawn targeted assistance cases tied directly to a specific beneficiary record.

3. **Case Lifecycle & Voluntary Claim System:**
   * Granular categorization of social assistance (Food, Healthcare, Housing, Clothing, Education, Economic Relief, and General Support).
   * Status progression model: `pending` $\rightarrow$ `in_progress` $\rightarrow$ `complete`.
   * Transparent assignment mechanism: volunteers can review open community needs and voluntarily "claim" a case, establishing personal accountability for that delivery.
   * Case status updates allowing volunteers to reflect the exact stage of delivery.

4. **Executive Dashboard & Real-Time Search Engine:**
   * Dynamic metric counters summarizing total beneficiaries assisted, pending requests, ongoing relief operations, and successfully closed cases.
   * Multi-criteria query engine enabling volunteers to filter cases simultaneously by status and text keywords across descriptions and beneficiary names.

---

### In-Depth File Architecture

The project adheres to a clean separation of concerns, decoupling presentation templates, styling, database management, and application routing into dedicated modules:

#### 1. Backend & Data Layer

* **`schema.sql`:**
  Defines the relational SQLite database schema with three core entities: `users`, `beneficiaries`, and `cases`. It enforces relational integrity through foreign key constraints:
  * `cases.beneficiary_id` references `beneficiaries(id)` with `ON DELETE CASCADE`, ensuring that deleting an obsolete beneficiary cleans up associated cases without leaving orphaned records.
  * `cases.volunteer_id` references `users(id)` with `ON DELETE SET NULL`, preserving the history of a case even if a volunteer account is removed.
  * Appropriate data types and default timestamps (`CURRENT_TIMESTAMP`) ensure auditability.

* **`db.py`:**
  Encapsulates the database connection lifecycle and utility decorators:
  * `get_db()`: Manages the active SQLite connection stored in Flask's application context `g`, configuring `sqlite3.Row` as the row factory for dictionary-like column access and registering custom datetime adapters.
  * `close_db()`: Registered with Flask's `teardown_appcontext` hook to guarantee that database connections are properly closed at the end of each request, preventing connection leaks.
  * `init_db()`: Reads and executes `schema.sql` to initialize or rebuild the database schema.
  * `login_required(f)`: A higher-order decorator wrapping view functions using `functools.wraps`. It inspects `session["user_id"]` and redirects unauthenticated requests to `/login`, providing robust access control across protected routes.

* **`app.py`:**
  The central application entry point orchestrating all HTTP routes, request validation, business logic, and Jinja template rendering:
  * Configures application security, secret key management, cache prevention headers via `after_request`, and database parameters.
  * Implements authentication routes: `/register`, `/login`, and `/logout`.
  * Implements directory management: `/` (Dashboard with aggregated metrics and parameterized search), `/beneficiaries` (directory viewing and registration), `/cases/new` (case creation form), `/cases/<id>` (case detail view), `/cases/<id>/claim` (volunteer assignment), and `/cases/<id>/status` (status updates).
  * Enforces parameterized SQL queries across all endpoints to prevent SQL injection vulnerabilities.

* **`requirements.txt`:**
  Specifies the pinned dependencies required to run Samaritan, keeping the runtime environment lightweight: Flask, Werkzeug, Jinja2, Click, Blinker, itsdangerous, and MarkupSafe.

#### 2. Presentation Layer (`templates/` & `static/`)

* **`templates/layout.html`:**
  The foundational Jinja2 base layout implementing a responsive navigation bar, conditional navigation links based on authentication state (`session["user_id"]`), a container for flashed notification messages, the primary content injection block (`{% block main %}`), dynamic document titles (`{% block title %}`), and standard footer branding. It imports Bootstrap 5 and Bootstrap Icons via CDN.

* **`templates/index.html`:**
  The administrative dashboard. It displays summary cards with key operational metrics, provides a unified search bar and status filter dropdown, and renders the central table of aid requests with status badges and quick links to case details.

* **`templates/beneficiaries.html`:**
  The beneficiary directory interface. It features an interactive, collapsible registration card enabling swift data entry without navigating away from the page, alongside a comprehensive data table displaying contact details, household size, and direct action buttons to log cases for specific individuals.

* **`templates/new_case.html`:**
  A structured form for logging community needs. It supports pre-selecting a beneficiary through query parameters (`?beneficiary_id=...`) and allows selecting predefined aid categories, inputting priority descriptions, and setting up initial case parameters.

* **`templates/case_detail.html`:**
  The comprehensive single-case inspection view. It breaks down the beneficiary profile, shows current volunteer assignment details, displays the full narrative description of the family's needs, and provides direct forms to claim the case or transition its operational status.

* **`templates/login.html` & `templates/register.html`:**
  Clean, accessible forms for volunteer onboarding and authentication, equipped with icon-enhanced inputs, client-side validation hints, and flash message error feedback.

* **`static/css/styles.css`:**
  Custom CSS layer complementing Bootstrap 5. It establishes cohesive CSS custom variables (`--samaritan-primary`, `--samaritan-bg`), enhances typography, defines subtle card shadow transitions on hover, customizes focus rings on inputs, and standardizes table header styling.

### Design Decisions

Samaritan was built using Flask and SQLite because these were the main technologies introduced during CS50. For the final project, I wanted to apply what I had learned throughout the course by building a complete web application using Python, SQL, HTML, CSS, Bootstrap, and Jinja templates.

For the visual design of the application, I used an AI-generated website template as a reference and adapted its style and layout to fit Samaritan's purpose and functionality.

### Development Process & Academic Honesty Acknowledgments

In alignment with CS50's academic honesty guidelines and policies regarding the responsible use of assistive tools:

* **Authored Independently:**
  The core vision, problem definition, complete database architecture and entity-relationship design, backend route implementation in Python, business rules, session authorization flows, and template structures were designed and written by the author.
* **External Documentation & Pair-Programming Assistance:**
  Official documentation for Flask, Jinja2, and Bootstrap 5 was consulted throughout development. Additionally, generative AI was utilized selectively as an educational pair-programming aid:
  * Assisting with responsive layout nuances and Bootstrap component interactions (specifically resolving DOM structure details in collapsible components on `beneficiaries.html`).
  * Refining the `login_required` decorator pattern according to modern Flask conventions.
  * Assisting with the formulation and syntax optimization of complex multi-table SQL queries involving `JOIN`, `LEFT JOIN`, and dynamic `WHERE` clauses with variable filters in `app.py`.
  * Code refactoring and polishing for clean code aesthetics.

All generated patterns and documentation recommendations were thoroughly reviewed, adapted, tested, and integrated into the project logic by the author.

---

### Setup & Installation Guide

To run Samaritan locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AmbrocioJRDeLaCruz/samaritan-app.git
   cd samaritan-app
   ```

2. **Create and activate a virtual environment:**
   * *Windows (PowerShell):*
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   * *macOS / Linux:*
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the SQLite database:**
   Execute Python in interactive mode or run a one-line command to build the schema:
   ```bash
   python -c "from app import app; from db import init_db; app.app_context().push(); init_db()"
   ```
   *(This creates the `samaritan.db` database and runs `schema.sql`)*.

5. **Launch the development server:**
   ```bash
   python app.py
   ```
   Open your browser and navigate to `http://127.0.0.1:5000`.