import secrets

from flask import Blueprint, jsonify, request
from flask_mail import Message

from app import db, mail
from app.models import User
from flask import render_template

main = Blueprint("main", __name__)

@main.route('/admin-dashboard')
def admin_dashboard():
    return render_template("admin_dashboard.html")

@main.route('/user-dashboard')
def user_dashboard():
    return render_template("user_dashboard.html")
    
@main.route('/login-page')
def login_page():
    return render_template("login.html")

@main.route('/')
def home():
    return render_template("index.html")


def generate_otp() -> str:
    """Return a random 6-digit OTP (000000–999999) as a string."""
    return f"{secrets.randbelow(1_000_000):06d}"

def send_otp_email(email: str, otp: str) -> None:
    """Send the OTP to *email* via Flask-Mail. Requires an application context."""
    msg = Message(
        subject="Your OTP Code",
        recipients=[email],
        body=f"Your OTP is: {otp}",
    )
    mail.send(msg)

@main.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    if not email or not isinstance(email, str):
        return jsonify({"error": "email is required"}), 400

    email = email.strip()
    if not email:
        return jsonify({"error": "email is required"}), 400

    otp = generate_otp()
    user = User.query.filter_by(email=email).first()

    if user is None:
        user = User(email=email, status="PENDING")
        db.session.add(user)

    user.otp = otp
    db.session.commit()

    send_otp_email(email, otp)

    return jsonify({"message": "OTP sent successfully"}), 200


@main.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    otp = data.get("otp")

    if not email or not isinstance(email, str):
        return jsonify({"error": "email is required"}), 400
    if otp is None or not isinstance(otp, str):
        return jsonify({"error": "otp is required"}), 400

    email = email.strip()
    otp = otp.strip()
    if not email or not otp:
        return jsonify({"error": "email and otp are required"}), 400

    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "Invalid email or OTP"}), 401

    stored = user.otp or ""
    if not secrets.compare_digest(stored, otp):
        return jsonify({"error": "Invalid email or OTP"}), 401

    # Verified; leave status unchanged (remains PENDING for new users).
    return jsonify({"message": "OTP verified successfully"}), 200


@main.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    if not email or not isinstance(email, str):
        return jsonify({"error": "email is required"}), 400

    email = email.strip()
    if not email:
        return jsonify({"error": "email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "user not found"}), 404

    if user.status == "ACTIVE":
        return jsonify({"message": "Login successful","role": user.role}), 200
    if user.status == "PENDING":
        return jsonify({"message": "Your account is pending admin approval"}), 200
    if user.status == "BLOCKED":
        return jsonify({"error": "Access denied"}), 403

    return jsonify({"error": "Unknown account status"}), 400

@main.route('/dashboard', methods=['POST'])
def dashboard():
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email).first()

    if not user or user.status != "ACTIVE":
        return jsonify({"error": "Unauthorized"}), 403

    approved = User.query.filter_by(status="ACTIVE").all()
    pending = User.query.filter_by(status="PENDING").all()
    blocked = User.query.filter_by(status="BLOCKED").all()

    return jsonify({
        "approved": [u.email for u in approved],
        "pending": [u.email for u in pending],
        "blocked": [u.email for u in blocked],
        "counts": {
            "approved": len(approved),
            "pending": len(pending),
            "blocked": len(blocked)
        }
    })


@main.route("/admin/users", methods=["GET"])
def admin_users():
    users = User.query.order_by(User.id).all()
    return jsonify(
        [
            {"email": u.email, "status": u.status, "role": u.role}
            for u in users
        ]
    )


@main.route("/admin/approve", methods=["POST"])
def admin_approve():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    if not email or not isinstance(email, str):
        return jsonify({"error": "email is required"}), 400

    email = email.strip()
    if not email:
        return jsonify({"error": "email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "user not found"}), 404

    user.status = "ACTIVE"
    db.session.commit()

    return jsonify({"message": "User approved successfully"}), 200


@main.route("/admin/reject", methods=["POST"])
def admin_reject():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    if not email or not isinstance(email, str):
        return jsonify({"error": "email is required"}), 400

    email = email.strip()
    if not email:
        return jsonify({"error": "email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "user not found"}), 404

    user.status = "BLOCKED"
    db.session.commit()

    return jsonify({"message": "User rejected successfully"}), 200