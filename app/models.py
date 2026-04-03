from __future__ import annotations

from . import db 


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    otp = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(32), nullable=False, default="PENDING")
    role = db.Column(db.String(32), nullable=False, default="USER")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} status={self.status!r} role={self.role!r}>"
