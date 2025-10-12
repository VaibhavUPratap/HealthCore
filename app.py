from flask import Flask, render_template
from flask_cors import CORS
from database.db import init_db
from routes.health_routes import health_bp
import os

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
    
    @app.route("/solutions")
    def solutions_page():
        return render_template("solutions.html")
    
    @app.route("/text-comparison")
    def text_comparison():
        return render_template("text-comparison.html")


    @app.errorhandler(404)
    def not_found(_):
        return "Not Found", 404

    @app.errorhandler(500)
    def server_error(_):
        return "Server Error", 500

    return app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app = create_app()
    app.run(host="0.0.0.0", port=port)

