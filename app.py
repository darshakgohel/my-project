from flask import Flask, render_template, request, session, jsonify
from flask import send_from_directory
from datetime import timedelta
import chatlogic

app = Flask(__name__)
app.secret_key = "replace_with_a_random_secret_key"
app.permanent_session_lifetime = timedelta(hours=6)  # session lasts while browser open

# initialize session memory
def init_session():
    session.permanent = True
    if "memory" not in session:
        session["memory"] = {
            "name": None,
            "goal": None,
            "habit": None,
            "node": "start",   # current node id
            "steps": 0
        }

@app.route("/")
def index():
    init_session()
    return render_template("index.html")

# single POST /chat route. Expects JSON: { message: "..." }
@app.route("/chat", methods=["POST"])
def chat():
    init_session()
    data = request.get_json() or {}
    user_message = (data.get("message") or "").strip()
    if user_message == "":
        return jsonify({"ok": False, "error": "Empty message."}), 400

    # route into chatlogic
    mem = session["memory"]
    response = chatlogic.handle_message(user_message, mem)

    # update session memory & current node
    session["memory"] = response.get("memory", mem)
    # respond with message, options, and node id
    return jsonify({
        "ok": True,
        "reply": response["reply"],
        "options": response["options"],
        "node": response.get("node", session["memory"].get("node", "start"))
    })

# route to reset the session (optional)
@app.route("/reset", methods=["POST"])
def reset():
    session.pop("memory", None)
    init_session()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)
