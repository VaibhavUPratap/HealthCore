from flask import Flask, render_template
from flask_cors import CORS
from database.db import init_db
from routes.health_routes import health_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Initialize DB
    init_db(app)
    
    # Register routes
    app.register_blueprint(health_bp, url_prefix="/api")
    
    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/report")
    def report_page():
        return render_template("report.html")

    @app.route("/alerts")
    def alerts_page():
        return render_template("alerts.html")

    @app.errorhandler(404)
    def not_found(_):
        return "Not Found", 404

    @app.errorhandler(500)
    def server_error(_):
        return "Server Error", 500

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
