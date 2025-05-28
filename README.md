# Clinic SaaS MVP

This is a Minimal Viable Product (MVP) for a SaaS platform built with Flask, designed for small clinics to manage patient visits, view schedules, and streamline administrative tasks. It is mobile-responsive, lightweight, and easy to deploy.

## ✨ Features

* Patient self-booking
* Visit scheduling with time slots
* Dashboard for doctors and patients
* Role-based data visibility
* Password change and secure login (JWT)
* Admin: manage organizations, niches, and functionality

## 📅 Use Cases

* Solo doctors managing patient appointments
* Small clinics needing a simple scheduling tool
* MVP for testing with healthcare clients

## 👀 Demo Screenshots

| Dashboard                               | Schedule Visit                                    | Patient View                          |
| --------------------------------------- | ------------------------------------------------- | ------------------------------------- |
| ![Dashboard](screenshots/dashboard.png) | ![Schedule Visit](screenshots/schedule_visit.png) | ![Patients](screenshots/patients.png) |

## ⚡ Tech Stack

* Python 3.12
* Flask
* Jinja2 templates
* SQLite database
* TailwindCSS for styling

## ⛓ Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## ⚙️ Running Locally

1. Clone the repo:

   ```bash
   git clone https://github.com/VladimirGoldenberg/clinic-saas-mvp.git
   cd clinic-saas-mvp
   ```
2. Initialize the DB:

   ```bash
   flask db upgrade
   ```
3. Run the app:

   ```bash
   python -m app.app
   ```

Then go to `http://127.0.0.1:5000/health/login` in your browser.

## 🔑 Default Test Accounts

| Role    | Email                                                                     | Password |
| ------- | ------------------------------------------------------------------------- | -------- |
| Doctor  | [vladimir.goldenberg@hotmail.com](mailto:vladimir.goldenberg@hotmail.com) | test1234 |
| Patient | [anna@hotmail.com](mailto:anna@hotmail.com)                               | test1234 |

## 🏥 Roadmap

* [ ] Email reminders
* [ ] Patient visit history
* [ ] Chatbot integration for Q\&A
* [ ] Clinic-specific branding

## ✉️ Contact

For questions or suggestions, please contact [Vladimir Goldenberg](mailto:vladimir.goldenberg@hotmail.com)

---

© 2025 Health MVP. Built with love and Flask.
