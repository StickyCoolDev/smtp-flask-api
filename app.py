import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# --- Configurations --- #
app = Flask(__name__)
load_dotenv()

# NOTE : use a good API key in .env

API_KEY: str = os.getenv("API_KEY", "default_unsafe")

# setup limiter
limiter = Limiter(
    get_remote_address, app=app, default_limits=["200 per day", "50 per hour"]
)

# --- Email Configuration --- #
SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD: str = os.getenv("SENDER_PASSWORD", "")
SMTP_SERVER: str = "smtp.gmail.com"
SMTP_PORT: int = 465


# --- Flask routes --- #
@app.route("/send_email", methods=["POST"])
def send_email():
    data = request.get_json()
    if API_KEY != data.get("key"):
        return jsonify({"error": "Invalid acsses"}), 401
    try:
        recipient_email = data.get("recipient")
        subject = data.get("subject")
        body = data.get("body")

        if not all([recipient_email, subject, body]):
            return jsonify({"error": "Missing recipient, subject, or body"}), 400

        # Create a multipart message and set headers
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email
        msg["Subject"] = subject

        # Attach the body with MIMEText
        msg.attach(MIMEText(body, "plain"))

        # Create a secure SSL context
        context = ssl.create_default_context()

        # Connect to the SMTP server and send the email
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())

        print("[INFO] : Emall sent successfully")
        return jsonify({"message": "Email sent successfully!"}), 200

    except Exception as e:
        print("[ERROR]: ", e)
        return jsonify({"error": str(e)}), 500


# --- Main Function ---
def main():
    if SENDER_EMAIL == "" or SENDER_PASSWORD == "":
        if (
            input(
                "\033[48;5;214m Warn \033[0m]: ENV's not found, continue running app?(n/ENTER)"
            )
            == "n"
        ):
            quit()
        else:
            pass
    app.run(debug=True)


if __name__ == "__main__":
    main()
