# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, session
from orchestrator import process_user_message
from db_queries import get_user_by_username, save_chat_message, get_chat_history, get_open_cases

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Use a secure key in production

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("select_case"))
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = get_user_by_username(username)
        if user and user["password_hash"] == password:
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            # Clear any existing conversation
            session["conversation"] = {}
            return redirect(url_for("select_case"))
        else:
            return "Invalid credentials", 401
    return render_template("login.html")

@app.route("/select_case", methods=["GET"])
def select_case():
    if "user_id" not in session:
        return redirect(url_for("login"))
    open_cases = get_open_cases()
    return render_template("select_case.html", open_cases=open_cases)

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    # Get case_id either from query parameter or session
    case_id = request.args.get("case_id") or session.get("current_case_id")
    if not case_id:
        return redirect(url_for("select_case"))
    case_id = int(case_id)
    # Store the active case id in session
    session["current_case_id"] = case_id

    # Always load conversation history from DB for this (user, case)
    conversation = get_chat_history(user_id, case_id)

    if request.method == "POST":
        user_message = request.form.get("message")
        # Save the user message in the DB
        save_chat_message(user_id, case_id, "user", user_message)
        # Process message via orchestrator with the new message as context.
        # (We send only the latest message along with system prompt that includes the case id)
        answer = process_user_message(user_id, case_id, [{"role": "user", "content": user_message}])
        # Save the assistant's reply to the DB
        save_chat_message(user_id, case_id, "assistant", answer)
        # Reload full conversation from DB
        conversation = get_chat_history(user_id, case_id)
        return render_template("chat.html", conversation=conversation, case_id=case_id)
    else:
        return render_template("chat.html", conversation=conversation, case_id=case_id)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
