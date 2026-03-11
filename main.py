from graph import app
from nodes import generate_report
from database import init_db, create_session, end_session


try:
    init_db()
    session_id = create_session()
    app.invoke({"current_app": "", "iteration": 0, "category": "neutre", "score": 0, "presence": "absent", "distraction_streak": 0,"session_id":session_id, "historique": []})
except KeyboardInterrupt:
    end_session(session_id, 0)
    generate_report()
