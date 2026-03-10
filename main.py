from graph import app
from nodes import generate_report

try:
    app.invoke({"current_app": "", "iteration": 0, "category": "neutre", "score": 0, "presence": "absent", "distraction_streak": 0, "historique": []})
except KeyboardInterrupt:
    generate_report()
