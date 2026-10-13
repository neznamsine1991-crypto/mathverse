# MATHVERSE

MATHVERSE is a Flask mathematics-learning platform for grades 5–8. It supports guest-mode practice, custom assessments, precise answer grading (including fractions), detailed worked solutions, attempt history, dashboard statistics, and a mistake journal.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Deploy to Render

Push this folder to a GitHub repository, then create a **Blueprint** in Render and select that repository. Render will read `render.yaml`. Set a strong `SECRET_KEY` (Render can generate it automatically). The default database is a guest-mode SQLite database in `/tmp`, which is reset when Render redeploys; attach a persistent database before launching for real students.
