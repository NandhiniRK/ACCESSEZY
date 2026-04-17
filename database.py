import sqlite3

DB_PATH = "database.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # ── Users: teacher and parent only ──────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            email      TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            role       TEXT NOT NULL CHECK(role IN ('teacher', 'parent')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Pending users awaiting OTP email verification ────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            email      TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            role       TEXT NOT NULL,
            otp        TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Student profiles (managed by teacher, not a login account) ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_profiles (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            age        INTEGER,
            notes      TEXT,
            teacher_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(id)
        )
    """)

    # ── Link parent account to a student profile ─────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parent_student_link (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id  INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            UNIQUE(parent_id, student_id),
            FOREIGN KEY (parent_id)  REFERENCES users(id),
            FOREIGN KEY (student_id) REFERENCES student_profiles(id)
        )
    """)

    # ── Behavioral notes written by teacher ──────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS behavioral_notes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            note       TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(id),
            FOREIGN KEY (student_id) REFERENCES student_profiles(id)
        )
    """)

    # ── Observational logs (structured, weekly entries) ───────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS observational_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            log_text   TEXT NOT NULL,
            log_date   DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(id),
            FOREIGN KEY (student_id) REFERENCES student_profiles(id)
        )
    """)

    # ── Classroom activities completed by a student ───────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classroom_activities (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id   INTEGER NOT NULL,
            student_id   INTEGER NOT NULL,
            activity_name TEXT NOT NULL,
            description  TEXT,
            completed_on DATE NOT NULL,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(id),
            FOREIGN KEY (student_id) REFERENCES student_profiles(id)
        )
    """)

    # ── Homework assigned by teacher ──────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS homework (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id  INTEGER NOT NULL,
            student_id  INTEGER NOT NULL,
            title       TEXT NOT NULL,
            description TEXT,
            due_date    DATE,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(id),
            FOREIGN KEY (student_id) REFERENCES student_profiles(id)
        )
    """)

    # ── Learning materials uploaded by teacher ────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_materials (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id  INTEGER NOT NULL,
            student_id  INTEGER NOT NULL,
            title       TEXT NOT NULL,
            description TEXT,
            file_url    TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(id),
            FOREIGN KEY (student_id) REFERENCES student_profiles(id)
        )
    """)

    # ── Community posts (teacher + parent) ───────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS community_posts (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            title        TEXT NOT NULL,
            content      TEXT NOT NULL,
            category     TEXT DEFAULT 'general',
            is_anonymous INTEGER DEFAULT 0,
            is_pinned    INTEGER DEFAULT 0,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS community_replies (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id      INTEGER NOT NULL,
            user_id      INTEGER NOT NULL,
            content      TEXT NOT NULL,
            is_anonymous INTEGER DEFAULT 0,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES community_posts(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_reactions (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            UNIQUE(post_id, user_id),
            FOREIGN KEY (post_id) REFERENCES community_posts(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized.")
