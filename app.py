from __future__ import annotations

from uuid import uuid4

from flask import Flask, jsonify, request

app = Flask(__name__)
members: dict[str, dict[str, str]] = {}


@app.get("/health")
def health():
    return jsonify(status="healthy", service="gym-management-api")


@app.get("/api/members")
def list_members():
    return jsonify(members=list(members.values()))


@app.post("/api/members")
def create_member():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="A JSON object is required."), 400

    name = payload.get("name")
    email = payload.get("email")
    if not isinstance(name, str) or not name.strip():
        return jsonify(error="A non-empty name is required."), 400
    if not isinstance(email, str) or "@" not in email:
        return jsonify(error="A valid email address is required."), 400

    normalized_email = email.strip().lower()
    if any(member["email"] == normalized_email for member in members.values()):
        return jsonify(error="A member with this email already exists."), 409

    member = {
        "id": str(uuid4()),
        "name": name.strip(),
        "email": normalized_email,
        "status": "active",
    }
    members[member["id"]] = member
    return jsonify(member=member), 201


@app.get("/api/members/<member_id>")
def get_member(member_id: str):
    member = members.get(member_id)
    if member is None:
        return jsonify(error="Member not found."), 404
    return jsonify(member=member)
