import logging

# Configure logging to output to both console and file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler("app_debug.log", mode="w")  # Log to a file, overwrite each time
    ]
)
logger = logging.getLogger(__name__)

logger.info("Starting Library Assistant Chatbot application...")

from chatbot.chatbot import Chatbot
from chatbot.database import get_db_connection
from chatbot.config import Config
from flask import Flask, render_template, request, session, redirect, url_for

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Initialize chatbot
chatbot = Chatbot()

# Update Flask app configuration
app.config.from_object(Config)

@app.before_request
def ensure_username():
    if "username" not in session and request.endpoint not in ["set_username", "static", "logout", "index"]:
        return redirect(url_for("index"))

@app.route("/set_username", methods=["POST"])
def set_username():
    username = request.form.get("username")
    if not username:
        return "Username is required", 400
    session["username"] = username
    return redirect(url_for("index"))

@app.route("/logout", methods=["GET"])
def logout():
    logger.info("Logout route accessed. Clearing session.")
    session.clear()
    logger.info("Session cleared. Redirecting to index.")
    return redirect(url_for("index"))

@app.route("/", methods=["GET"])
def index():
    logger.info("Index route accessed.")
    if "username" not in session:
        logger.info("No username in session. Rendering set_username.html.")
        return render_template("set_username.html")
    logger.info("Username found in session. Rendering index.html.")
    return render_template("index.html", history=session.get("history", []))

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form.get("message")

    if not user_message:
        return "Invalid input", 400

    # Get chatbot response
    bot_response = chatbot.get_response(user_message, session.get("username"))

    # Store chat history in session
    if "history" not in session:
        session["history"] = []

    session["history"].append({
        "user": session["username"],
        "message": user_message,
        "response": bot_response
    })

    return bot_response

@app.route("/test", methods=["GET"])
def test():
    return "Server is running and accessible!", 200

@app.before_request
def log_request_info():
    logger.debug(f"Request Endpoint: {request.endpoint}")
    logger.debug(f"Request Method: {request.method}")
    logger.debug(f"Request Args: {request.args}")
    logger.debug(f"Request Form: {request.form}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)  # Disable auto-reload for stability
