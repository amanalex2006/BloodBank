from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from sqlalchemy import text, inspect
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {"sslmode": "require"}
}

db = SQLAlchemy(app)




@app.route("/")
def home():
    return "Blood Bank App Running"


@app.route("/test-db")
def test_db():
    try:
        result = db.session.execute(text("SELECT 1"))
        return "Database Connected Successfully ✅"
    except Exception as e:
        return f"Connection Failed ❌<br>{str(e)}"





@app.route("/tables")
def show_tables():
    try:
        conn = db.session.connection()
        inspector = inspect(conn)
        tables = inspector.get_table_names()
        return "<br>".join(tables)
    except Exception as e:
        return f"<pre>{str(e)}</pre>"

if __name__ == "__main__":
    app.run(debug=True)