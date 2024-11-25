from app import app
from app import db

if __name__ == "__main__":
    # from waitress import serve
    # serve(app)
    app.run(debug=True)
