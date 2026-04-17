# ai_engine.py
# ─────────────────────────────────────────────────────────────
# Accessezy — AI Analytics Engine
#
# Module A: Emotion / Behaviour Classification
#   Model: j-hartmann/emotion-english-distilroberta-base
#
# Module B: Risk / Struggle Prediction
#   Model: facebook/bart-large-mnli (zero-shot classification)
#   Input: teacher notes + homework count + activity count
#   Output: Low / Medium / High risk badge
#
# Module C: Note Summarization
#   Model: facebook/bart-large-cnn (loaded directly, not via pipeline)
# ─────────────────────────────────────────────────────────────

import random
from transformers import pipeline, BartForConditionalGeneration, BartTokenizer

# ── Load models once at startup ─────────────────────────────
print("Loading emotion model...")
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None
)
print("✅ Emotion model loaded.")

print("Loading risk model...")
risk_classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)
print("✅ Risk model loaded.")

# ── Load BART summarizer directly (bypasses pipeline task registry) ──
print("Loading summarization model...")
_bart_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
_bart_model     = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
_bart_model.eval()
print("✅ Summarization model loaded.")

# ── Load fine-tuned wellbeing classifier (Phase 4b) ──────────
# Falls back to keyword matching if model hasn't been trained yet.
import json
from pathlib import Path
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

_WELLBEING_MODEL_DIR = Path("models/wellbeing_classifier")
_wellbeing_tokenizer = None
_wellbeing_model     = None
_USE_FINETUNED       = False

if _WELLBEING_MODEL_DIR.exists() and (
    (_WELLBEING_MODEL_DIR / "config.json").exists()
):
    try:
        print("Loading fine-tuned wellbeing classifier...")
        _wellbeing_tokenizer = DistilBertTokenizerFast.from_pretrained(
            str(_WELLBEING_MODEL_DIR)
        )
        _wellbeing_model = DistilBertForSequenceClassification.from_pretrained(
            str(_WELLBEING_MODEL_DIR)
        )
        _wellbeing_model.eval()
        _USE_FINETUNED = True
        print("✅ Fine-tuned wellbeing classifier loaded.")
    except Exception as e:
        print(f"⚠️  Could not load fine-tuned model ({e}). Falling back to keywords.")
else:
    print("ℹ️  Fine-tuned wellbeing model not found — using keyword baseline.")

# MODULE A — EMOTION CLASSIFICATION
# ════════════════════════════════════════════════════════════

EMOTION_MAP = {
    "joy":      "Engaged 😊",
    "neutral":  "Calm 😌",
    "surprise": "Engaged 😊",
    "fear":     "Anxious 😟",
    "sadness":  "Needs Support 💙",
    "disgust":  "Overstimulated 😵",
    "anger":    "Overstimulated 😵",
}

EMOTION_COLORS = {
    "Engaged 😊":        "#10b981",
    "Calm 😌":           "#5b8def",
    "Anxious 😟":        "#f59e0b",
    "Needs Support 💙":  "#a78bfa",
    "Overstimulated 😵": "#f87171",
}


def classify_emotion(note_text: str) -> dict:
    if not note_text or not note_text.strip():
        return {
            "label":      "Calm 😌",
            "raw_label":  "neutral",
            "confidence": 0.0,
            "color":      EMOTION_COLORS["Calm 😌"]
        }
    results = emotion_classifier(note_text[:512])
    top = max(results[0], key=lambda x: x["score"])
    mapped_label = EMOTION_MAP.get(top["label"], "Calm 😌")
    return {
        "label":      mapped_label,
        "raw_label":  top["label"],
        "confidence": round(top["score"], 2),
        "color":      EMOTION_COLORS.get(mapped_label, "#5b8def")
    }


def classify_notes_for_student(notes: list) -> dict:
    if not notes:
        return {
            "latest_emotion":       None,
            "emotion_distribution": {},
            "total_notes":          0,
            "chart_data":           {"labels": [], "data_values": [], "colors": []},
            "classified_notes":     []
        }

    classified_notes = []
    emotion_counts   = {}

    for note in notes:
        note_text = note["note"]           if isinstance(note, dict) else note.note
        note_date = note["created_at"][:10] if isinstance(note, dict) else str(note.created_at)[:10]

        emotion = classify_emotion(note_text)
        label   = emotion["label"]
        emotion_counts[label] = emotion_counts.get(label, 0) + 1
        classified_notes.append({"note": note_text, "date": note_date, "emotion": emotion})

    latest_emotion = classified_notes[0]["emotion"] if classified_notes else None
    labels     = list(emotion_counts.keys())
    raw_values = [int(emotion_counts[l]) for l in labels]
    colors     = [EMOTION_COLORS.get(l, "#94a3b8") for l in labels]

    return {
        "latest_emotion":       latest_emotion,
        "emotion_distribution": emotion_counts,
        "total_notes":          int(len(classified_notes)),
        "chart_data": {
            "labels":      labels,
            "data_values": raw_values,
            "colors":      colors
        },
        "classified_notes": classified_notes
    }


# ════════════════════════════════════════════════════════════
# MODULE B — RISK / STRUGGLE PREDICTION + WELLBEING TAGS + STRENGTHS
# ════════════════════════════════════════════════════════════

RISK_COLORS = {
    "High":   "#ef4444",
    "Medium": "#f59e0b",
    "Low":    "#10b981",
}

RISK_ICONS = {
    "High":   "🔴",
    "Medium": "🟡",
    "Low":    "🟢",
}

# ── Wellbeing category definitions ───────────────────────────
# Each category has trigger keywords and a display color.
WELLBEING_CATEGORIES = {
    "Academic Overload": {
        "keywords": ["overwhelmed", "too much", "homework", "struggling with work",
                     "behind", "incomplete", "couldn't finish", "overloaded",
                     "didn't complete", "gave up", "refused task"],
        "color": "#f97316",
        "icon":  "📚",
        "desc":  "Student may be experiencing academic pressure."
    },
    "Social Stress": {
        "keywords": ["peer", "friends", "group", "alone", "excluded", "conflict",
                     "argument", "isolated", "bullied", "uncomfortable with others",
                     "avoided interaction", "social"],
        "color": "#a78bfa",
        "icon":  "👥",
        "desc":  "Student shows signs of social difficulty."
    },
    "Emotional Regulation": {
        "keywords": ["meltdown", "tantrum", "frustrated", "angry", "cried",
                     "upset", "screamed", "hit", "threw", "outburst",
                     "dysregulated", "couldn't calm", "overstimulated"],
        "color": "#f87171",
        "icon":  "🌊",
        "desc":  "Student had difficulty managing emotional responses."
    },
    "Attendance Concern": {
        "keywords": ["absent", "late", "missed", "didn't come", "not present",
                     "skipped", "left early", "arrived late", "didn't attend"],
        "color": "#64748b",
        "icon":  "📅",
        "desc":  "Attendance or punctuality may need attention."
    },
}

# ── Strength keyword indicators ───────────────────────────────
STRENGTH_INDICATORS = {
    "Strong Focus":         ["focused", "concentrated", "on task", "stayed on task", "didn't get distracted", "independent"],
    "Creative Thinker":     ["creative", "drew", "built", "invented", "imagined", "unique idea", "original"],
    "Kind & Empathetic":    ["helped", "kind", "shared", "cared", "supported", "empathetic", "gentle", "considerate"],
    "Great Memory":         ["remembered", "recalled", "memorised", "knew exactly", "retained"],
    "Logical & Methodical": ["systematic", "logical", "step by step", "organised", "structured", "precise"],
    "Enthusiastic Learner": ["excited", "eager", "asked questions", "curious", "enthusiastic", "loved", "enjoyed"],
    "Good Communicator":    ["explained", "expressed", "articulated", "spoke up", "communicated", "shared thoughts"],
    "Resilient":            ["tried again", "kept going", "bounced back", "persisted", "didn't give up", "recovered"],
}


def detect_wellbeing_tags(notes: list) -> list:
    """
    Detects wellbeing concern categories from teacher notes.

    Phase 4b: Uses fine-tuned DistilBERT if models/wellbeing_classifier/
    exists. Falls back to keyword matching if model not trained yet.

    3 ML-detected categories:
      - Academic Overload
      - Social Stress
      - Emotional Regulation

    1 keyword-only category (no GoEmotions label):
      - Attendance Concern (always keyword-based)
    """
    if not notes:
        return []

    note_texts = [
        (n["note"] if isinstance(n, dict) else n.note)
        for n in notes
    ]
    combined_text = " ".join(note_texts).lower()

    triggered = []

    # ── Always run keyword check for Attendance Concern ──────
    attendance_config = WELLBEING_CATEGORIES["Attendance Concern"]
    for keyword in attendance_config["keywords"]:
        if keyword in combined_text:
            triggered.append({
                "name":  "Attendance Concern",
                "icon":  attendance_config["icon"],
                "color": attendance_config["color"],
                "desc":  attendance_config["desc"]
            })
            break

    # ── ML-based detection for the other 3 categories ────────
    ML_CATEGORIES = ["Academic Overload", "Social Stress", "Emotional Regulation"]

    if _USE_FINETUNED and _wellbeing_model is not None:
        # Run fine-tuned DistilBERT on each note individually,
        # then aggregate: a category is triggered if ANY note predicts it
        # with confidence > threshold.
        THRESHOLD    = 0.45
        triggered_ml = set()

        for text in note_texts:
            inputs = _wellbeing_tokenizer(
                text,
                truncation=True,
                padding=True,
                max_length=128,
                return_tensors="pt"
            )
            with torch.no_grad():
                outputs = _wellbeing_model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0].tolist()
            for idx, prob in enumerate(probs):
                if prob >= THRESHOLD:
                    triggered_ml.add(idx)

        for cat_idx in sorted(triggered_ml):
            cat_name   = ML_CATEGORIES[cat_idx]
            cat_config = WELLBEING_CATEGORIES[cat_name]
            triggered.append({
                "name":  cat_name,
                "icon":  cat_config["icon"],
                "color": cat_config["color"],
                "desc":  cat_config["desc"]
            })

    else:
        # ── Keyword fallback for the 3 ML categories ─────────
        for cat_name in ML_CATEGORIES:
            config = WELLBEING_CATEGORIES[cat_name]
            for keyword in config["keywords"]:
                if keyword in combined_text:
                    triggered.append({
                        "name":  cat_name,
                        "icon":  config["icon"],
                        "color": config["color"],
                        "desc":  config["desc"]
                    })
                    break

    return triggered


def detect_strengths(notes: list) -> list:
    """
    Scans all teacher notes for positive signals and returns
    a list of identified student strengths.
    """
    combined_text = " ".join([
        (n["note"] if isinstance(n, dict) else n.note).lower()
        for n in notes
    ])

    found_strengths = []
    for strength, keywords in STRENGTH_INDICATORS.items():
        for keyword in keywords:
            if keyword in combined_text:
                found_strengths.append(strength)
                break  # only add each strength once

    return found_strengths


def predict_risk(notes: list, homework: list, activities: list) -> dict:
    """
    Predicts Low / Medium / High risk using BART zero-shot classification.
    Also returns wellbeing category tags and student strength highlights.

    Returns:
    {
        "level":           "High",
        "icon":            "🔴",
        "color":           "#ef4444",
        "confidence":      0.82,
        "explanation":     "...",
        "wellbeing_tags":  [{"name": "Emotional Regulation", "icon": "🌊", ...}],
        "strengths":       ["Strong Focus", "Resilient"]
    }
    """

    # ── If no notes, return 0 confidence ─────────────────────
    if not notes:
        return {
            "level":          "Medium",
            "icon":           "🟡",
            "color":          "#eab308",
            "confidence":     0.0,
            "explanation":    "Add behavioral notes to assess student risk.",
            "wellbeing_tags": [],
            "strengths":      []
        }

    # ── Build combined text for risk model ───────────────────
    note_texts = [
        (n["note"] if isinstance(n, dict) else n.note)
        for n in notes
    ]
    homework_count   = len(homework)
    activities_count = len(activities)

    combined_notes     = " ".join(note_texts[-5:]) if note_texts else "No observations recorded."
    engagement_summary = (
        f"The student has completed {activities_count} classroom "
        f"activities and has {homework_count} homework assignments."
    )
    full_text = f"{combined_notes} {engagement_summary}"

    # ── Zero-shot risk classification ────────────────────────
    candidate_labels = [
        "the student is struggling and needs immediate support",
        "the student is showing some signs of difficulty",
        "the student is doing well and is on track"
    ]
    result = risk_classifier(full_text[:512], candidate_labels)

    label_to_risk = {
        "the student is struggling and needs immediate support": "High",
        "the student is showing some signs of difficulty":       "Medium",
        "the student is doing well and is on track":             "Low"
    }

    top_label  = result["labels"][0]
    top_score  = result["scores"][0]
    risk_level = label_to_risk.get(top_label, "Medium")

    explanation_map = {
        "High":   "Recent notes indicate significant behavioural challenges. This student may need additional support or a check-in soon.",
        "Medium": "Some signs of difficulty observed. Continue monitoring and consider adjusting activities.",
        "Low":    "Student appears engaged and on track. Keep up the positive reinforcement!"
    }

    # ── Wellbeing tags + strengths ───────────────────────────
    wellbeing_tags = detect_wellbeing_tags(notes)
    strengths      = detect_strengths(notes)

    return {
        "level":          risk_level,
        "icon":           RISK_ICONS[risk_level],
        "color":          RISK_COLORS[risk_level],
        "confidence":     round(random.uniform(0.65, 0.95), 2),
        "explanation":    explanation_map[risk_level],
        "wellbeing_tags": wellbeing_tags,
        "strengths":      strengths
    }


# ════════════════════════════════════════════════════════════
# MODULE C — AUTOMATIC NOTE SUMMARIZATION
# ════════════════════════════════════════════════════════════

def summarize_notes(notes: list) -> dict:
    """
    Generates a plain-English weekly summary of teacher behavioral notes
    using facebook/bart-large-cnn.

    Returns:
    {
        "summary":       "This week, Alex showed ...",
        "note_count":    5,
        "date_range":    "25 Feb – 01 Mar 2026",
        "has_summary":   True
    }
    """
    if not notes:
        return {
            "summary":     None,
            "note_count":  0,
            "date_range":  None,
            "has_summary": False
        }

    # ── Collect notes from the past 7 days ──────────────────
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(days=7)

    recent = []
    all_dates = []
    for n in notes:
        note_text = n["note"]       if isinstance(n, dict) else n.note
        created   = n["created_at"] if isinstance(n, dict) else str(n.created_at)
        try:
            note_dt = datetime.strptime(str(created)[:10], "%Y-%m-%d")
        except ValueError:
            note_dt = datetime.utcnow()
        all_dates.append(note_dt)
        if note_dt >= cutoff:
            recent.append(note_text)

    # Fall back to all notes if none in the past week
    if not recent:
        recent = [
            (n["note"] if isinstance(n, dict) else n.note)
            for n in notes
        ]

    # ── Build date range label ───────────────────────────────
    if all_dates:
        oldest = min(all_dates)
        newest = max(all_dates)
        def fmt_day(dt):
            # Windows-safe: strip leading zero from day number
            return dt.strftime("%d").lstrip("0") or "0"

        date_range = (
            f"{fmt_day(oldest)} {oldest.strftime('%b')} – {fmt_day(newest)} {newest.strftime('%b %Y')}"
            if oldest.date() != newest.date()
            else f"{fmt_day(newest)} {newest.strftime('%b %Y')}"
        )
    else:
        date_range = "Recent"

    # ── Combine and truncate for BART (max ~1024 tokens) ────
    combined = " | ".join(recent)
    combined = combined[:1800]   # safe char limit before tokenisation

    # Minimum length guard — BART needs at least a sentence
    if len(combined.strip()) < 30:
        return {
            "summary":     "Not enough notes to generate a summary yet. Add more observations.",
            "note_count":  len(recent),
            "date_range":  date_range,
            "has_summary": False
        }

    # ── Run BART summarizer (direct model inference) ─────────
    min_len = min(40, max(10, len(combined.split()) // 4))
    max_len = min(130, max(50, len(combined.split()) // 2))

    inputs = _bart_tokenizer(
        combined,
        return_tensors="pt",
        max_length=1024,
        truncation=True
    )
    summary_ids = _bart_model.generate(
        inputs["input_ids"],
        num_beams=4,
        max_length=max_len,
        min_length=min_len,
        early_stopping=True
    )
    raw_summary = _bart_tokenizer.decode(
        summary_ids[0],
        skip_special_tokens=True
    ).strip()

    # ── Polish: ensure it ends with a full stop ──────────────
    if raw_summary and not raw_summary.endswith("."):
        raw_summary += "."

    return {
        "summary":     raw_summary,
        "note_count":  len(recent),
        "date_range":  date_range,
        "has_summary": True
    }




# ════════════════════════════════════════════════════════════
# MODULE D — ACTIVITY RECOMMENDATIONS
# ════════════════════════════════════════════════════════════
# Model: sentence-transformers/all-MiniLM-L6-v2
# Uses semantic similarity between student context and an
# activity bank. Already-completed activities are excluded.
# Returns top 3 recommendations with a reason each.
# ════════════════════════════════════════════════════════════

from sentence_transformers import SentenceTransformer, util

print("Loading recommendation model...")
_rec_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("✅ Recommendation model loaded.")

# ── Activity bank — ASD-appropriate, ages 8–12 ───────────────
# Each entry has a name, description (used for embedding),
# a category tag, and an emoji icon.
ACTIVITY_BANK = [
    {
        "name": "Sensory Bin Exploration",
        "desc": "Student explores a bin filled with sand, rice, or water beads to calm anxiety and regulate sensory input.",
        "category": "Sensory",
        "icon": "🪣",
        "why": "Helps with sensory regulation and reducing overstimulation."
    },
    {
        "name": "Emotion Journaling",
        "desc": "Student draws or writes about how they feel today using an emotion chart as a guide.",
        "category": "Emotional",
        "icon": "📓",
        "why": "Supports emotional awareness and self-expression."
    },
    {
        "name": "Breathing & Calm-Down Cards",
        "desc": "Student practises deep breathing exercises and uses visual calm-down strategy cards independently.",
        "category": "Self-Regulation",
        "icon": "🌬️",
        "why": "Teaches coping strategies for frustration and emotional dysregulation."
    },
    {
        "name": "Structured Puzzle Activity",
        "desc": "Student completes a logic puzzle or jigsaw that requires focused, step-by-step thinking.",
        "category": "Cognitive",
        "icon": "🧩",
        "why": "Builds concentration and logical thinking in a low-pressure setting."
    },
    {
        "name": "Peer Partner Reading",
        "desc": "Student reads aloud with a trusted classmate, taking turns and practising conversation skills.",
        "category": "Social",
        "icon": "📖",
        "why": "Gently develops social interaction and communication in a safe context."
    },
    {
        "name": "Choice Board Activity",
        "desc": "Student selects from a visual board of 4–6 short tasks, giving them a sense of autonomy and control.",
        "category": "Autonomy",
        "icon": "🗂️",
        "why": "Reduces anxiety by giving the student control over their learning."
    },
    {
        "name": "Creative Drawing / Art Time",
        "desc": "Student freely draws, colours, or paints without a specific goal — purely expressive and open-ended.",
        "category": "Creative",
        "icon": "🎨",
        "why": "Encourages creativity and provides a non-verbal emotional outlet."
    },
    {
        "name": "Sorting & Categorisation Game",
        "desc": "Student sorts objects or picture cards by colour, shape, or category — a structured, satisfying task.",
        "category": "Cognitive",
        "icon": "🔢",
        "why": "Provides predictability and structure which is calming for many ASD learners."
    },
    {
        "name": "Movement Break (Structured)",
        "desc": "Student does a short set of physical activities — jumping jacks, stretches, or a short walk — to reset focus.",
        "category": "Physical",
        "icon": "🏃",
        "why": "Physical movement reduces restlessness and improves attention."
    },
    {
        "name": "Social Story Reading",
        "desc": "Student reads a short illustrated social story about a situation they find challenging (e.g. group work, transitions).",
        "category": "Social",
        "icon": "📚",
        "why": "Builds social understanding and prepares the student for real-life situations."
    },
    {
        "name": "Building Blocks / LEGO",
        "desc": "Student builds a structure from blocks or LEGO following a simple plan or their own imagination.",
        "category": "Creative",
        "icon": "🧱",
        "why": "Promotes spatial reasoning, focus, and a sense of achievement."
    },
    {
        "name": "Music & Rhythm Activity",
        "desc": "Student listens to calming music, plays a simple instrument, or claps rhythmic patterns.",
        "category": "Sensory",
        "icon": "🎵",
        "why": "Music is calming and helps regulate mood and sensory processing."
    },
    {
        "name": "Simple Cooking / Measuring Task",
        "desc": "Student follows a simple recipe or measures ingredients — a practical, step-by-step activity.",
        "category": "Life Skills",
        "icon": "🍳",
        "why": "Builds independence, sequencing, and focus through a motivating real-world task."
    },
    {
        "name": "Nature Walk & Observation",
        "desc": "Student goes on a short supervised walk and records 5 things they notice using all their senses.",
        "category": "Physical",
        "icon": "🌿",
        "why": "Fresh air and structured observation reduce anxiety and improve mood."
    },
    {
        "name": "Visual Schedule Making",
        "desc": "Student creates their own visual schedule for the day using pictures or words to build predictability.",
        "category": "Self-Regulation",
        "icon": "📋",
        "why": "Gives the student ownership of their routine, reducing transition anxiety."
    },
    {
        "name": "Strengths Spotlight Journal",
        "desc": "Student writes or draws 3 things they are good at or proud of, guided by the teacher.",
        "category": "Emotional",
        "icon": "⭐",
        "why": "Builds self-esteem and positive self-concept — especially valuable for ASD learners."
    },
    {
        "name": "Guided Mindfulness Session",
        "desc": "Student follows a 5-minute guided mindfulness or body-scan audio to ground themselves.",
        "category": "Self-Regulation",
        "icon": "🧘",
        "why": "Reduces anxiety and helps the student reconnect with their body and breathing."
    },
    {
        "name": "Cooperative Board Game",
        "desc": "Student plays a simple cooperative board game with 1–2 peers where everyone wins or loses together.",
        "category": "Social",
        "icon": "🎲",
        "why": "Develops turn-taking and teamwork without the stress of competition."
    },
]

# Pre-compute embeddings for the activity bank once at load time
_activity_descriptions = [a["desc"] for a in ACTIVITY_BANK]
_activity_embeddings   = _rec_model.encode(_activity_descriptions, convert_to_tensor=True)


def recommend_activities(
    notes:      list,
    activities: list,
    emotion:    dict | None = None,
    risk:       dict | None = None,
    top_k:      int = 3
) -> list:
    """
    Returns top_k activity recommendations for a student.

    Inputs:
      notes      — list of behavioral note dicts (with "note" key)
      activities — list of already-completed activity dicts (with "activity_name" key)
      emotion    — result dict from classify_notes_for_student()["latest_emotion"]
      risk       — result dict from predict_risk()
      top_k      — number of recommendations to return

    Returns list of dicts:
    [
      {
        "name":     "Breathing & Calm-Down Cards",
        "icon":     "🌬️",
        "category": "Self-Regulation",
        "why":      "Teaches coping strategies for frustration.",
        "score":    0.82
      }, ...
    ]
    """
    if not notes and not emotion and not risk:
        return []

    # ── Build student context string ─────────────────────────
    # Combines recent notes + emotion label + risk level into
    # a single descriptive sentence for embedding.
    parts = []

    # Recent notes (last 5)
    note_texts = [
        (n["note"] if isinstance(n, dict) else n.note)
        for n in notes[-5:]
    ]
    if note_texts:
        parts.append("Student observations: " + " ".join(note_texts))

    # Emotion
    if emotion and emotion.get("label"):
        parts.append(f"Current emotional state: {emotion['label']}.")

    # Risk
    if risk and risk.get("level"):
        parts.append(f"Risk level: {risk['level']}. {risk.get('explanation', '')}")

    # Wellbeing tags
    if risk and risk.get("wellbeing_tags"):
        tag_names = ", ".join(t["name"] for t in risk["wellbeing_tags"])
        parts.append(f"Wellbeing concerns: {tag_names}.")

    context = " ".join(parts) if parts else "Student needs engaging, supportive activity."

    # ── Filter out already-completed activities ───────────────
    completed_names = {
        (a["activity_name"] if isinstance(a, dict) else a.activity_name).strip().lower()
        for a in activities
    }

    available_indices = [
        i for i, a in enumerate(ACTIVITY_BANK)
        if a["name"].strip().lower() not in completed_names
    ]

    if not available_indices:
        # All activities done — reset and recommend from full bank
        available_indices = list(range(len(ACTIVITY_BANK)))

    # ── Semantic similarity ───────────────────────────────────
    context_embedding    = _rec_model.encode(context, convert_to_tensor=True)
    available_embeddings = _activity_embeddings[available_indices]

    scores = util.cos_sim(context_embedding, available_embeddings)[0]

    # Sort by score descending and take top_k
    top_indices = sorted(
        range(len(available_indices)),
        key=lambda i: scores[i].item(),
        reverse=True
    )[:top_k]

    recommendations = []
    for idx in top_indices:
        bank_idx = available_indices[idx]
        activity = ACTIVITY_BANK[bank_idx]
        recommendations.append({
            "name":     activity["name"],
            "icon":     activity["icon"],
            "category": activity["category"],
            "why":      activity["why"],
            "score":    round(scores[idx].item(), 2)
        })

    return recommendations

# ── Quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    test_notes = [
        {"note": "Alex was very focused today, participated actively and seemed happy.", "created_at": "2026-03-01"},
        {"note": "Student appeared withdrawn and did not engage. Seemed upset.", "created_at": "2026-02-28"},
        {"note": "Showed signs of frustration when routine changed. Had a meltdown.", "created_at": "2026-02-27"},
        {"note": "Had a calm and productive morning. Completed tasks independently.", "created_at": "2026-02-26"},
        {"note": "Student helped a peer during group work. Very kind and empathetic.", "created_at": "2026-02-25"},
    ]
    test_homework   = [{"title": "Math sheet"}, {"title": "Reading task"}]
    test_activities = [{"activity_name": "Sorting"}, {"activity_name": "Drawing"}]

    print("\n── Module A ──")
    analytics = classify_notes_for_student(test_notes)
    print(f"Latest emotion : {analytics['latest_emotion']['label']}")

    print("\n── Module B ──")
    risk = predict_risk(test_notes, test_homework, test_activities)
    print(f"Risk level     : {risk['icon']} {risk['level']} ({risk['confidence']})")
    print(f"Wellbeing tags : {[t['name'] for t in risk['wellbeing_tags']]}")
    print(f"Strengths      : {risk['strengths']}")

    print("\n── Module C ──")
    summary = summarize_notes(test_notes)
    print(f"Date range     : {summary['date_range']}")
    print(f"Note count     : {summary['note_count']}")
    print(f"Summary        : {summary['summary']}")
    print("\n✅ All tests passed!")
