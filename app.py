import os
import csv
import io
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from database import init_db, get_db
from ai_engine import classify_notes_for_student, predict_risk, summarize_notes, recommend_activities

# Load .env file if present (local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

init_db()

# ─────────────────────────────────────────────
# One-time DB reset (admin only, via GET)
# Visit /admin/reset-db to wipe all data.
# Remove this route after use in production.
# ─────────────────────────────────────────────

@app.route("/admin/reset-db")
def reset_db():
    if not admin_required():
        return redirect(url_for("login"))
    db = get_db()
    tables = [
        "community_replies", "post_reactions", "community_posts",
        "learning_materials", "homework", "classroom_activities",
        "observational_logs", "behavioral_notes", "parent_student_link",
        "student_profiles", "users"
    ]
    for t in tables:
        db.execute(f"DELETE FROM {t}")
    db.commit()
    db.close()
    session.clear()   # log admin out too so they re-register fresh
    flash("✅ All data wiped. Please register a new admin account.", "success")
    return redirect(url_for("register"))

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(role=None):
    if "user_id" not in session:
        flash("Please log in to continue.", "warning")
        return False
    if role and session.get("role") != role:
        flash("You don't have permission to access that page.", "danger")
        return False
    return True

def admin_required():
    """Only the hard-coded admin account can access admin routes."""
    if "user_id" not in session:
        flash("Please log in to continue.", "warning")
        return False
    if not session.get("is_admin"):
        flash("Admin access only.", "danger")
        return False
    return True

# ─────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role     = request.form.get("role", "")

        if not name or not email or not password or not role:
            flash("Please fill in all required fields.", "danger")
            return render_template("register.html")

        if role not in ("teacher", "parent"):
            flash("Invalid role selected.", "danger")
            return render_template("register.html")

        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash("An account with that email already exists.", "danger")
            db.close()
            return render_template("register.html")

        # Create user account directly
        db.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, hash_password(password), role)
        )
        db.commit()
        db.close()

        flash("Account created successfully! Please log in. 🎉", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        db   = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, hash_password(password))
        ).fetchone()
        db.close()
        if user:
            session["user_id"] = user["id"]
            session["name"]    = user["name"]
            session["role"]    = user["role"]
            session["is_admin"] = (user["email"] == "admin@accessezy.com")
            flash(f"Welcome back, {user['name']}! 👋", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Incorrect email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You've been logged out.", "info")
    return redirect(url_for("home"))

# ─────────────────────────────────────────────
# Dashboard — role-based router
# ─────────────────────────────────────────────

@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))
    # Admin goes directly to admin portal — no teacher dashboard detour
    if session.get("is_admin"):
        return redirect(url_for("admin_portal"))
    if session.get("role") == "teacher":
        return redirect(url_for("teacher_dashboard"))
    elif session.get("role") == "parent":
        return redirect(url_for("parent_dashboard"))
    flash("Unknown role.", "danger")
    return redirect(url_for("logout"))

# ─────────────────────────────────────────────
# Teacher Dashboard
# ─────────────────────────────────────────────

@app.route("/teacher")
def teacher_dashboard():
    if not login_required(role="teacher"):
        return redirect(url_for("login"))

    db = get_db()
    teacher_id = session["user_id"]

    # All students this teacher manages
    students_raw = db.execute(
        "SELECT * FROM student_profiles WHERE teacher_id = ? ORDER BY name",
        (teacher_id,)
    ).fetchall()

    # All parents (for the link form)
    parents = db.execute(
        "SELECT id, name, email FROM users WHERE role = 'parent' ORDER BY name"
    ).fetchall()

    # Recent behavioral notes across all students
    recent_notes = db.execute("""
        SELECT bn.*, sp.name as student_name
        FROM behavioral_notes bn
        JOIN student_profiles sp ON bn.student_id = sp.id
        WHERE bn.teacher_id = ?
        ORDER BY bn.created_at DESC LIMIT 5
    """, (teacher_id,)).fetchall()

    # Compute risk + wellbeing + strengths for each student
    students = []
    for s in students_raw:
        sid = s["id"]
        s_notes = db.execute(
            "SELECT * FROM behavioral_notes WHERE student_id = ? ORDER BY created_at DESC",
            (sid,)
        ).fetchall()
        s_homework = db.execute(
            "SELECT * FROM homework WHERE student_id = ?", (sid,)
        ).fetchall()
        s_activities = db.execute(
            "SELECT * FROM classroom_activities WHERE student_id = ?", (sid,)
        ).fetchall()
        risk = predict_risk(
            [dict(n) for n in s_notes],
            [dict(h) for h in s_homework],
            [dict(a) for a in s_activities]
        )
        students.append({**dict(s), "risk": risk})

    db.close()
    return render_template("teacher_dashboard.html",
                           students=students,
                           parents=parents,
                           recent_notes=recent_notes)

# ─────────────────────────────────────────────
# Teacher — Add Student Profile
# ─────────────────────────────────────────────

@app.route("/teacher/add-student", methods=["POST"])
def add_student():
    if not login_required(role="teacher"):
        return redirect(url_for("login"))
    name = request.form.get("name", "").strip()
    age  = request.form.get("age") or None
    if not name:
        flash("Student name is required.", "danger")
        return redirect(url_for("teacher_dashboard"))
    db = get_db()
    db.execute(
        "INSERT INTO student_profiles (name, age, teacher_id) VALUES (?, ?, ?)",
        (name, age, session["user_id"])
    )
    db.commit()
    db.close()
    flash(f"Student '{name}' added successfully! ✅", "success")
    return redirect(url_for("teacher_dashboard"))

# ─────────────────────────────────────────────
# Teacher — Link Parent to Student
# ─────────────────────────────────────────────

@app.route("/teacher/link-parent", methods=["POST"])
def link_parent():
    if not login_required(role="teacher"):
        return redirect(url_for("login"))
    parent_id  = request.form.get("parent_id")
    student_id = request.form.get("student_id")
    if not parent_id or not student_id:
        flash("Please select both a parent and a student.", "danger")
        return redirect(url_for("teacher_dashboard"))
    db = get_db()
    existing = db.execute(
        "SELECT id FROM parent_student_link WHERE parent_id = ? AND student_id = ?",
        (parent_id, student_id)
    ).fetchone()
    if not existing:
        db.execute(
            "INSERT INTO parent_student_link (parent_id, student_id) VALUES (?, ?)",
            (parent_id, student_id)
        )
        db.commit()
        flash("Parent linked to student successfully! ✅", "success")
    else:
        flash("This parent is already linked to that student.", "warning")
    db.close()
    return redirect(url_for("teacher_dashboard"))

# ─────────────────────────────────────────────
# Student Profile (teacher & parent can view)
# ─────────────────────────────────────────────

@app.route("/student/<int:student_id>")
def student_profile(student_id):
    if not login_required():
        return redirect(url_for("login"))
    db = get_db()

    # Teachers see only their own students; parents see only linked students
    if session["role"] == "teacher":
        student = db.execute(
            "SELECT * FROM student_profiles WHERE id = ? AND teacher_id = ?",
            (student_id, session["user_id"])
        ).fetchone()
    else:
        student = db.execute("""
            SELECT sp.* FROM student_profiles sp
            JOIN parent_student_link psl ON sp.id = psl.student_id
            WHERE sp.id = ? AND psl.parent_id = ?
        """, (student_id, session["user_id"])).fetchone()

    if not student:
        flash("Student not found or access denied.", "danger")
        db.close()
        return redirect(url_for("dashboard"))

    notes = db.execute(
        "SELECT * FROM behavioral_notes WHERE student_id = ? ORDER BY created_at DESC",
        (student_id,)
    ).fetchall()

    logs = db.execute(
        "SELECT * FROM observational_logs WHERE student_id = ? ORDER BY log_date DESC",
        (student_id,)
    ).fetchall()

    activities = db.execute(
        "SELECT * FROM classroom_activities WHERE student_id = ? ORDER BY completed_on DESC",
        (student_id,)
    ).fetchall()

    homework = db.execute(
        "SELECT * FROM homework WHERE student_id = ? ORDER BY due_date ASC",
        (student_id,)
    ).fetchall()

    materials = db.execute(
        "SELECT * FROM learning_materials WHERE student_id = ? ORDER BY created_at DESC",
        (student_id,)
    ).fetchall()

    db.close()

    # ── Run emotion classification on all notes ───────────────
    notes_as_dicts = [dict(n) for n in notes]
    emotion_analytics = classify_notes_for_student(notes_as_dicts)

    # ── Run risk prediction ───────────────────────────────────
    risk = predict_risk(
        notes_as_dicts,
        [dict(h) for h in homework],
        [dict(a) for a in activities]
    )

    # ── Run note summarization (Module C) ─────────────────────
    note_summary = summarize_notes(notes_as_dicts)

    # ── Run activity recommendations (Module D) ──────────────
    recommendations = recommend_activities(
        notes_as_dicts,
        [dict(a) for a in activities],
        emotion_analytics.get("latest_emotion"),
        risk
    )

    return render_template("student_profile.html",
                           student=student,
                           notes=notes,
                           logs=logs,
                           activities=activities,
                           homework=homework,
                           materials=materials,
                           emotion_analytics=emotion_analytics,
                           risk=risk,
                           note_summary=note_summary,
                           recommendations=recommendations)

# ─────────────────────────────────────────────
# Teacher — Add Behavioral Note
# ─────────────────────────────────────────────

@app.route("/teacher/add-note", methods=["POST"])
def add_note():
    if not login_required(role="teacher"):
        return redirect(url_for("login"))
    student_id = request.form.get("student_id")
    note       = request.form.get("note", "").strip()
    if not student_id or not note:
        flash("Note cannot be empty.", "danger")
        return redirect(url_for("teacher_dashboard"))
    db = get_db()
    db.execute(
        "INSERT INTO behavioral_notes (teacher_id, student_id, note) VALUES (?, ?, ?)",
        (session["user_id"], student_id, note)
    )
    db.commit()
    db.close()
    flash("Behavioral note saved! 📝", "success")
    return redirect(url_for("student_profile", student_id=student_id))

# ─────────────────────────────────────────────
# Teacher — Add Observational Log
# ─────────────────────────────────────────────

@app.route("/teacher/add-log", methods=["POST"])
def add_log():
    if not login_required(role="teacher"):
        return redirect(url_for("login"))
    student_id = request.form.get("student_id")
    log_text   = request.form.get("log_text", "").strip()
    log_date   = request.form.get("log_date")
    if not student_id or not log_text or not log_date:
        flash("All fields are required for a log entry.", "danger")
        return redirect(url_for("student_profile", student_id=student_id))
    db = get_db()
    db.execute(
        "INSERT INTO observational_logs (teacher_id, student_id, log_text, log_date) VALUES (?, ?, ?, ?)",
        (session["user_id"], student_id, log_text, log_date)
    )
    db.commit()
    db.close()
    flash("Observational log saved! 🔍", "success")
    return redirect(url_for("student_profile", student_id=student_id))

# ─────────────────────────────────────────────
# Teacher — Add Classroom Activity
# ─────────────────────────────────────────────

@app.route("/teacher/add-activity", methods=["POST"])
def add_activity():
    if not login_required(role="teacher"):
        return redirect(url_for("login"))
    student_id    = request.form.get("student_id")
    activity_name = request.form.get("activity_name", "").strip()
    description   = request.form.get("description", "").strip()
    completed_on  = request.form.get("completed_on")
    if not student_id or not activity_name or not completed_on:
        flash("Activity name and date are required.", "danger")
        return redirect(url_for("student_profile", student_id=student_id))
    db = get_db()
    db.execute(
        """INSERT INTO classroom_activities
           (teacher_id, student_id, activity_name, description, completed_on)
           VALUES (?, ?, ?, ?, ?)""",
        (session["user_id"], student_id, activity_name, description, completed_on)
    )
    db.commit()
    db.close()
    flash("Activity recorded! ✅", "success")
    return redirect(url_for("student_profile", student_id=student_id))

# ─────────────────────────────────────────────
# Teacher — Assign Homework
# ─────────────────────────────────────────────

@app.route("/teacher/assign-homework", methods=["POST"])
def assign_homework():
    if not login_required(role="teacher"):
        return redirect(url_for("login"))
    student_id  = request.form.get("student_id")
    title       = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    due_date    = request.form.get("due_date") or None
    if not student_id or not title:
        flash("Homework title is required.", "danger")
        return redirect(url_for("student_profile", student_id=student_id))
    db = get_db()
    db.execute(
        "INSERT INTO homework (teacher_id, student_id, title, description, due_date) VALUES (?, ?, ?, ?, ?)",
        (session["user_id"], student_id, title, description, due_date)
    )
    db.commit()
    db.close()
    flash("Homework assigned! 📋", "success")
    return redirect(url_for("student_profile", student_id=student_id))

# ─────────────────────────────────────────────
# Teacher — Add Learning Material
# ─────────────────────────────────────────────

@app.route("/teacher/add-material", methods=["POST"])
def add_material():
    if not login_required(role="teacher"):
        return redirect(url_for("login"))
    student_id  = request.form.get("student_id")
    title       = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    file_url    = request.form.get("file_url", "").strip()
    if not student_id or not title:
        flash("Material title is required.", "danger")
        return redirect(url_for("student_profile", student_id=student_id))
    db = get_db()
    db.execute(
        "INSERT INTO learning_materials (teacher_id, student_id, title, description, file_url) VALUES (?, ?, ?, ?, ?)",
        (session["user_id"], student_id, title, description, file_url)
    )
    db.commit()
    db.close()
    flash("Learning material added! 📎", "success")
    return redirect(url_for("student_profile", student_id=student_id))

# ─────────────────────────────────────────────
# Parent Dashboard
# ─────────────────────────────────────────────

@app.route("/parent")
def parent_dashboard():
    if not login_required(role="parent"):
        return redirect(url_for("login"))

    db = get_db()
    parent_id = session["user_id"]

    # Get all students linked to this parent
    students_raw = db.execute("""
        SELECT sp.*
        FROM student_profiles sp
        JOIN parent_student_link psl ON sp.id = psl.student_id
        WHERE psl.parent_id = ?
        ORDER BY sp.name
    """, (parent_id,)).fetchall()

    children = []
    for s in students_raw:
        sid = s["id"]

        recent_notes = db.execute(
            "SELECT * FROM behavioral_notes WHERE student_id = ? ORDER BY created_at DESC LIMIT 3",
            (sid,)
        ).fetchall()

        recent_activities = db.execute(
            "SELECT * FROM classroom_activities WHERE student_id = ? ORDER BY completed_on DESC LIMIT 3",
            (sid,)
        ).fetchall()

        pending_homework = db.execute(
            "SELECT * FROM homework WHERE student_id = ? ORDER BY due_date ASC LIMIT 3",
            (sid,)
        ).fetchall()

        recent_materials = db.execute(
            "SELECT * FROM learning_materials WHERE student_id = ? ORDER BY created_at DESC LIMIT 3",
            (sid,)
        ).fetchall()

        # ── AI Summary for parent (Module C) ─────────────────
        all_notes_for_summary = db.execute(
            "SELECT * FROM behavioral_notes WHERE student_id = ? ORDER BY created_at DESC",
            (sid,)
        ).fetchall()
        note_summary = summarize_notes([dict(n) for n in all_notes_for_summary])

        # ── Activity recommendations for parent view (Module D) ──
        all_activities_for_rec = db.execute(
            "SELECT * FROM classroom_activities WHERE student_id = ?", (sid,)
        ).fetchall()
        all_notes_for_rec = db.execute(
            "SELECT * FROM behavioral_notes WHERE student_id = ? ORDER BY created_at DESC",
            (sid,)
        ).fetchall()
        parent_recs = recommend_activities(
            [dict(n) for n in all_notes_for_rec],
            [dict(a) for a in all_activities_for_rec],
            top_k=3
        )

        children.append({
            "id": sid,
            "name": s["name"],
            "age": s["age"],
            "recent_notes": recent_notes,
            "recent_activities": recent_activities,
            "pending_homework": pending_homework,
            "recent_materials": recent_materials,
            "note_summary": note_summary,
            "recommendations": parent_recs,
        })

    db.close()
    return render_template("parent_dashboard.html", children=children)

# ─────────────────────────────────────────────
# Community — Feed
# ─────────────────────────────────────────────

@app.route("/community")
def community():
    if not login_required():
        return redirect(url_for("login"))

    category = request.args.get("category", "all")
    db = get_db()
    user_id = session["user_id"]

    # Build query based on category filter
    if category == "all":
        posts_raw = db.execute("""
            SELECT cp.*, u.name as author_name, u.role as author_role
            FROM community_posts cp
            JOIN users u ON cp.user_id = u.id
            ORDER BY cp.is_pinned DESC, cp.created_at DESC
        """).fetchall()
    else:
        posts_raw = db.execute("""
            SELECT cp.*, u.name as author_name, u.role as author_role
            FROM community_posts cp
            JOIN users u ON cp.user_id = u.id
            WHERE cp.category = ?
            ORDER BY cp.is_pinned DESC, cp.created_at DESC
        """, (category,)).fetchall()

    posts = []
    for p in posts_raw:
        p = dict(p)
        p["like_count"] = db.execute(
            "SELECT COUNT(*) FROM post_reactions WHERE post_id = ?", (p["id"],)
        ).fetchone()[0]
        p["reply_count"] = db.execute(
            "SELECT COUNT(*) FROM community_replies WHERE post_id = ?", (p["id"],)
        ).fetchone()[0]
        p["user_liked"] = db.execute(
            "SELECT id FROM post_reactions WHERE post_id = ? AND user_id = ?",
            (p["id"], user_id)
        ).fetchone() is not None
        posts.append(p)

    db.close()
    return render_template("community.html", posts=posts, active_category=category)


# ─────────────────────────────────────────────
# Community — New Post
# ─────────────────────────────────────────────

@app.route("/community/new", methods=["POST"])
def community_new_post():
    if not login_required():
        return redirect(url_for("login"))

    title    = request.form.get("title", "").strip()
    content  = request.form.get("content", "").strip()
    category = request.form.get("category", "general")
    is_anon  = 1 if request.form.get("is_anonymous") else 0
    is_pinned = 1 if (request.form.get("is_pinned") and session.get("role") == "teacher") else 0

    if not title or not content:
        flash("Title and content are required.", "danger")
        return redirect(url_for("community"))

    if category not in ("general", "tips", "announcements"):
        category = "general"

    db = get_db()
    db.execute(
        """INSERT INTO community_posts (user_id, title, content, category, is_anonymous, is_pinned)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (session["user_id"], title, content, category, is_anon, is_pinned)
    )
    db.commit()
    db.close()
    flash("Post published! 🚀", "success")
    return redirect(url_for("community"))


# ─────────────────────────────────────────────
# Community — Post Detail + Replies
# ─────────────────────────────────────────────

@app.route("/community/post/<int:post_id>")
def post_detail(post_id):
    if not login_required():
        return redirect(url_for("login"))

    db = get_db()
    user_id = session["user_id"]

    post = db.execute("""
        SELECT cp.*, u.name as author_name, u.role as author_role
        FROM community_posts cp
        JOIN users u ON cp.user_id = u.id
        WHERE cp.id = ?
    """, (post_id,)).fetchone()

    if not post:
        flash("Post not found.", "danger")
        db.close()
        return redirect(url_for("community"))

    post = dict(post)
    post["like_count"] = db.execute(
        "SELECT COUNT(*) FROM post_reactions WHERE post_id = ?", (post_id,)
    ).fetchone()[0]
    post["user_liked"] = db.execute(
        "SELECT id FROM post_reactions WHERE post_id = ? AND user_id = ?",
        (post_id, user_id)
    ).fetchone() is not None

    replies_raw = db.execute("""
        SELECT cr.*, u.name as author_name, u.role as author_role
        FROM community_replies cr
        JOIN users u ON cr.user_id = u.id
        WHERE cr.post_id = ?
        ORDER BY cr.created_at ASC
    """, (post_id,)).fetchall()

    db.close()
    return render_template("post_detail.html",
                           post=post,
                           replies=[dict(r) for r in replies_raw])


# ─────────────────────────────────────────────
# Community — Add Reply
# ─────────────────────────────────────────────

@app.route("/community/post/<int:post_id>/reply", methods=["POST"])
def add_reply(post_id):
    if not login_required():
        return redirect(url_for("login"))

    content = request.form.get("content", "").strip()
    is_anon = 1 if request.form.get("is_anonymous") else 0

    if not content:
        flash("Reply cannot be empty.", "danger")
        return redirect(url_for("post_detail", post_id=post_id))

    db = get_db()
    db.execute(
        "INSERT INTO community_replies (post_id, user_id, content, is_anonymous) VALUES (?, ?, ?, ?)",
        (post_id, session["user_id"], content, is_anon)
    )
    db.commit()
    db.close()
    flash("Reply posted! 💬", "success")
    return redirect(url_for("post_detail", post_id=post_id))


# ─────────────────────────────────────────────
# Community — Toggle Like / Reaction
# ─────────────────────────────────────────────

@app.route("/community/post/<int:post_id>/react", methods=["POST"])
def toggle_reaction(post_id):
    if not login_required():
        return redirect(url_for("login"))

    db = get_db()
    user_id = session["user_id"]
    existing = db.execute(
        "SELECT id FROM post_reactions WHERE post_id = ? AND user_id = ?",
        (post_id, user_id)
    ).fetchone()

    if existing:
        db.execute("DELETE FROM post_reactions WHERE post_id = ? AND user_id = ?",
                   (post_id, user_id))
    else:
        db.execute("INSERT INTO post_reactions (post_id, user_id) VALUES (?, ?)",
                   (post_id, user_id))

    db.commit()
    db.close()

    # Redirect back to wherever the user came from
    referrer = request.referrer
    if referrer and f"/community/post/{post_id}" in referrer:
        return redirect(url_for("post_detail", post_id=post_id))
    return redirect(url_for("community"))


# ─────────────────────────────────────────────
# Community — Toggle Pin (teacher only)
# ─────────────────────────────────────────────

@app.route("/community/post/<int:post_id>/pin", methods=["POST"])
def toggle_pin(post_id):
    if not login_required(role="teacher"):
        return redirect(url_for("login"))

    db = get_db()
    post = db.execute("SELECT is_pinned FROM community_posts WHERE id = ?", (post_id,)).fetchone()
    if post:
        new_val = 0 if post["is_pinned"] else 1
        db.execute("UPDATE community_posts SET is_pinned = ? WHERE id = ?", (new_val, post_id))
        db.commit()
        flash("Post " + ("pinned 📌" if new_val else "unpinned"), "success")
    db.close()
    return redirect(url_for("post_detail", post_id=post_id))


# ─────────────────────────────────────────────
# Community — Delete Post (teacher only)
# ─────────────────────────────────────────────

@app.route("/community/post/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    if not login_required(role="teacher"):
        return redirect(url_for("login"))

    db = get_db()
    db.execute("DELETE FROM community_replies WHERE post_id = ?", (post_id,))
    db.execute("DELETE FROM post_reactions WHERE post_id = ?", (post_id,))
    db.execute("DELETE FROM community_posts WHERE id = ?", (post_id,))
    db.commit()
    db.close()
    flash("Post deleted. 🗑️", "info")
    return redirect(url_for("community"))


# ─────────────────────────────────────────────
# Community — Delete Reply (teacher only)
# ─────────────────────────────────────────────

@app.route("/community/reply/<int:reply_id>/delete/<int:post_id>", methods=["POST"])
def delete_reply(reply_id, post_id):
    if not login_required(role="teacher"):
        return redirect(url_for("login"))

    db = get_db()
    db.execute("DELETE FROM community_replies WHERE id = ?", (reply_id,))
    db.commit()
    db.close()
    flash("Reply removed. 🗑️", "info")
    return redirect(url_for("post_detail", post_id=post_id))


# ─────────────────────────────────────────────
# Admin Portal
# ─────────────────────────────────────────────

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@accessezy.com")

@app.route("/admin")
def admin_portal():
    if not admin_required():
        return redirect(url_for("login"))

    db = get_db()

    # ── All users ─────────────────────────────────────────────
    users = db.execute("""
        SELECT u.*,
               COUNT(DISTINCT sp.id)  AS student_count,
               COUNT(DISTINCT bn.id)  AS note_count,
               COUNT(DISTINCT cp.id)  AS post_count
        FROM users u
        LEFT JOIN student_profiles sp ON sp.teacher_id = u.id
        LEFT JOIN behavioral_notes bn ON bn.teacher_id = u.id
        LEFT JOIN community_posts   cp ON cp.user_id   = u.id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """).fetchall()

    # ── Platform stats ────────────────────────────────────────
    stats = {
        "total_users":     db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "total_teachers":  db.execute("SELECT COUNT(*) FROM users WHERE role='teacher'").fetchone()[0],
        "total_parents":   db.execute("SELECT COUNT(*) FROM users WHERE role='parent'").fetchone()[0],
        "total_students":  db.execute("SELECT COUNT(*) FROM student_profiles").fetchone()[0],
        "total_notes":     db.execute("SELECT COUNT(*) FROM behavioral_notes").fetchone()[0],
        "total_posts":     db.execute("SELECT COUNT(*) FROM community_posts").fetchone()[0],
        "total_replies":   db.execute("SELECT COUNT(*) FROM community_replies").fetchone()[0],
        "total_homework":  db.execute("SELECT COUNT(*) FROM homework").fetchone()[0],
        "total_materials": db.execute("SELECT COUNT(*) FROM learning_materials").fetchone()[0],
    }

    # ── Most active teachers (by note count) ─────────────────
    top_teachers = db.execute("""
        SELECT u.name, COUNT(bn.id) AS note_count
        FROM users u
        JOIN behavioral_notes bn ON bn.teacher_id = u.id
        WHERE u.role = 'teacher'
        GROUP BY u.id
        ORDER BY note_count DESC
        LIMIT 5
    """).fetchall()

    # ── Recent community posts (for moderation) ───────────────
    community_posts = db.execute("""
        SELECT cp.*, u.name AS author_name,
               COUNT(cr.id) AS reply_count
        FROM community_posts cp
        JOIN users u ON cp.user_id = u.id
        LEFT JOIN community_replies cr ON cr.post_id = cp.id
        GROUP BY cp.id
        ORDER BY cp.created_at DESC
        LIMIT 20
    """).fetchall()

    db.close()
    return render_template("admin_portal.html",
                           users=users,
                           stats=stats,
                           top_teachers=top_teachers,
                           community_posts=community_posts)


@app.route("/admin/delete-user/<int:user_id>", methods=["POST"])
def admin_delete_user(user_id):
    if not admin_required():
        return redirect(url_for("login"))

    db = get_db()
    user = db.execute("SELECT name FROM users WHERE id = ?", (user_id,)).fetchone()
    if user:
        # Cascade: remove posts, replies, reactions, notes, links
        db.execute("DELETE FROM community_replies  WHERE user_id = ?", (user_id,))
        db.execute("DELETE FROM post_reactions      WHERE user_id = ?", (user_id,))
        db.execute("DELETE FROM community_posts     WHERE user_id = ?", (user_id,))
        db.execute("DELETE FROM behavioral_notes    WHERE teacher_id = ?", (user_id,))
        db.execute("DELETE FROM observational_logs  WHERE teacher_id = ?", (user_id,))
        db.execute("DELETE FROM classroom_activities WHERE teacher_id = ?", (user_id,))
        db.execute("DELETE FROM homework            WHERE teacher_id = ?", (user_id,))
        db.execute("DELETE FROM learning_materials  WHERE teacher_id = ?", (user_id,))
        db.execute("DELETE FROM parent_student_link WHERE parent_id  = ?", (user_id,))
        db.execute("DELETE FROM student_profiles    WHERE teacher_id = ?", (user_id,))
        db.execute("DELETE FROM users               WHERE id = ?",         (user_id,))
        db.commit()
        flash(f"User '{user['name']}' deleted. 🗑️", "info")
    db.close()
    return redirect(url_for("admin_portal"))


@app.route("/admin/delete-post/<int:post_id>", methods=["POST"])
def admin_delete_post(post_id):
    if not admin_required():
        return redirect(url_for("login"))

    db = get_db()
    db.execute("DELETE FROM community_replies WHERE post_id = ?", (post_id,))
    db.execute("DELETE FROM post_reactions    WHERE post_id = ?", (post_id,))
    db.execute("DELETE FROM community_posts   WHERE id = ?",      (post_id,))
    db.commit()
    db.close()
    flash("Post removed. 🗑️", "info")
    return redirect(url_for("admin_portal"))


@app.route("/admin/delete-reply/<int:reply_id>", methods=["POST"])
def admin_delete_reply(reply_id):
    if not admin_required():
        return redirect(url_for("login"))

    db = get_db()
    db.execute("DELETE FROM community_replies WHERE id = ?", (reply_id,))
    db.commit()
    db.close()
    flash("Reply removed. 🗑️", "info")
    return redirect(url_for("admin_portal"))


# ─────────────────────────────────────────────
# Admin — Export table as CSV
# Visit /admin/export-csv/<table_name> to download
# ─────────────────────────────────────────────

@app.route("/admin/export-csv/<table_name>")
def export_csv(table_name):
    if not admin_required():
        return redirect(url_for("login"))

    ALLOWED_TABLES = [
        "users", "student_profiles", "behavioral_notes",
        "homework", "learning_materials", "community_posts",
        "community_replies", "classroom_activities", "observational_logs"
    ]
    if table_name not in ALLOWED_TABLES:
        flash("Invalid table name.", "danger")
        return redirect(url_for("admin_portal"))

    db = get_db()
    rows = db.execute(f"SELECT * FROM {table_name}").fetchall()
    db.close()

    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows([dict(r) for r in rows])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={table_name}.csv"}
    )


if __name__ == "__main__":
    app.run(debug=True)
