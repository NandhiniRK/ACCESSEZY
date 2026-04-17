"""
evaluate_classifier.py
────────────────────────────────────────────────────────────────
Accessezy — Phase 4b: Wellbeing Classifier Evaluation

Loads the fine-tuned DistilBERT model from models/wellbeing_classifier/
and evaluates it against:
  1. The held-out GoEmotions test set
  2. The keyword baseline (original detect_wellbeing_tags logic)

Outputs:
  - Per-class F1 / precision / recall table
  - Macro and weighted averages
  - Side-by-side comparison: fine-tuned vs keyword baseline
  - Saves results to data/evaluation_results.json

Run AFTER train_classifier.py:
    python evaluate_classifier.py
────────────────────────────────────────────────────────────────
"""

import os
import sys
import json
import time
import numpy as np
from pathlib import Path

MODEL_DIR     = Path("models/wellbeing_classifier")
DATA_DIR      = Path("data")
RESULTS_PATH  = DATA_DIR / "evaluation_results.json"

print("=" * 60)
print("Accessezy — Wellbeing Classifier Evaluation")
print("=" * 60)

# ── Check model exists ───────────────────────────────────────
if not MODEL_DIR.exists():
    print("\n❌ Model not found at models/wellbeing_classifier/")
    print("Run train_classifier.py first.")
    sys.exit(1)

test_data_path = DATA_DIR / "goemotions_remapped_test.json"
if not test_data_path.exists():
    print(f"\n❌ Test data not found at {test_data_path}")
    print("Run train_classifier.py first.")
    sys.exit(1)

# ── Load dependencies ────────────────────────────────────────
try:
    import torch
    from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
    from sklearn.metrics import classification_report, confusion_matrix
    print("✅ Dependencies loaded.")
except ImportError as e:
    print(f"Missing: {e}")
    print("Run: pip install torch transformers scikit-learn")
    sys.exit(1)

# ── Load test data ───────────────────────────────────────────
print("\n[1/4] Loading test data...")
with open(test_data_path) as f:
    test_data = json.load(f)

test_texts  = test_data["texts"]
test_labels = test_data["labels"]
CATEGORY_NAMES = test_data["category_names"]

print(f"✅ {len(test_texts)} test samples loaded.")
from collections import Counter
dist = Counter(test_labels)
print("Test label distribution:")
for label_id, count in sorted(dist.items()):
    print(f"  {CATEGORY_NAMES[label_id]}: {count} samples")

# ── Load fine-tuned model ────────────────────────────────────
print("\n[2/4] Loading fine-tuned model...")
tokenizer = DistilBertTokenizerFast.from_pretrained(str(MODEL_DIR))
model     = DistilBertForSequenceClassification.from_pretrained(str(MODEL_DIR))
model.eval()
print("✅ Model loaded.")

# ── Run fine-tuned model inference ──────────────────────────
print("\n[3/4] Running fine-tuned model inference...")
BATCH_SIZE = 32
all_preds  = []

start = time.time()
for i in range(0, len(test_texts), BATCH_SIZE):
    batch_texts = test_texts[i:i + BATCH_SIZE]
    inputs = tokenizer(
        batch_texts,
        truncation=True,
        padding=True,
        max_length=128,
        return_tensors="pt"
    )
    with torch.no_grad():
        outputs = model(**inputs)
    preds = torch.argmax(outputs.logits, dim=-1).tolist()
    all_preds.extend(preds)

    if (i // BATCH_SIZE) % 5 == 0:
        done = min(i + BATCH_SIZE, len(test_texts))
        print(f"  Processed {done}/{len(test_texts)} samples...")

elapsed = time.time() - start
print(f"✅ Inference done in {elapsed:.1f}s")

# ── Fine-tuned model metrics ─────────────────────────────────
print("\n── Fine-tuned DistilBERT Results ─────────────────────")
ft_report = classification_report(
    test_labels, all_preds,
    target_names=CATEGORY_NAMES,
    output_dict=True,
    zero_division=0
)
print(classification_report(
    test_labels, all_preds,
    target_names=CATEGORY_NAMES,
    zero_division=0
))

# ── Keyword baseline ─────────────────────────────────────────
print("\n[4/4] Running keyword baseline...")

# Mirror the keyword logic from ai_engine.py
KEYWORD_RULES = {
    0: {  # Academic Overload
        "keywords": ["overwhelmed", "too much", "homework", "struggling with work",
                     "behind", "incomplete", "couldn't finish", "overloaded",
                     "didn't complete", "gave up", "refused task",
                     "confused", "annoy", "disappoint", "nervous"]
    },
    1: {  # Social Stress
        "keywords": ["peer", "friends", "group", "alone", "excluded", "conflict",
                     "argument", "isolated", "bullied", "uncomfortable with others",
                     "avoided interaction", "social", "embarrass", "fear", "disgust"]
    },
    2: {  # Emotional Regulation
        "keywords": ["meltdown", "tantrum", "frustrated", "angry", "cried",
                     "upset", "screamed", "hit", "threw", "outburst",
                     "dysregulated", "couldn't calm", "overstimulated",
                     "grief", "sad", "anger", "remorse"]
    }
}


def keyword_predict(text: str) -> int:
    """Predict category using keyword matching. Returns most-matched category."""
    text_lower = text.lower()
    scores = {cat_id: 0 for cat_id in KEYWORD_RULES}
    for cat_id, config in KEYWORD_RULES.items():
        for kw in config["keywords"]:
            if kw in text_lower:
                scores[cat_id] += 1
    best = max(scores, key=lambda k: scores[k])
    # If no keyword matched at all, default to Emotional Regulation (2)
    if scores[best] == 0:
        return 2
    return best


baseline_preds = [keyword_predict(t) for t in test_texts]

print("\n── Keyword Baseline Results ──────────────────────────")
bl_report = classification_report(
    test_labels, baseline_preds,
    target_names=CATEGORY_NAMES,
    output_dict=True,
    zero_division=0
)
print(classification_report(
    test_labels, baseline_preds,
    target_names=CATEGORY_NAMES,
    zero_division=0
))

# ── Comparison table ─────────────────────────────────────────
print("\n" + "=" * 60)
print("COMPARISON TABLE — Fine-tuned vs Keyword Baseline")
print("=" * 60)

header = f"{'Category':<25} {'Fine-tuned F1':>14} {'Baseline F1':>12} {'Δ':>8}"
print(header)
print("-" * 60)

for cat in CATEGORY_NAMES:
    ft_f1 = ft_report.get(cat, {}).get("f1-score", 0.0)
    bl_f1 = bl_report.get(cat, {}).get("f1-score", 0.0)
    delta = ft_f1 - bl_f1
    arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "=")
    print(f"{cat:<25} {ft_f1:>13.3f}  {bl_f1:>11.3f}  {arrow}{abs(delta):>6.3f}")

print("-" * 60)
ft_macro = ft_report["macro avg"]["f1-score"]
bl_macro = bl_report["macro avg"]["f1-score"]
delta    = ft_macro - bl_macro
arrow    = "▲" if delta > 0 else ("▼" if delta < 0 else "=")
print(f"{'Macro Average':<25} {ft_macro:>13.3f}  {bl_macro:>11.3f}  {arrow}{abs(delta):>6.3f}")

ft_weighted = ft_report["weighted avg"]["f1-score"]
bl_weighted = bl_report["weighted avg"]["f1-score"]
delta       = ft_weighted - bl_weighted
arrow       = "▲" if delta > 0 else ("▼" if delta < 0 else "=")
print(f"{'Weighted Average':<25} {ft_weighted:>13.3f}  {bl_weighted:>11.3f}  {arrow}{abs(delta):>6.3f}")
print("=" * 60)

# ── Save results ─────────────────────────────────────────────
results = {
    "fine_tuned": {
        "per_class":        {cat: ft_report[cat] for cat in CATEGORY_NAMES},
        "macro_avg":        ft_report["macro avg"],
        "weighted_avg":     ft_report["weighted avg"],
        "accuracy":         ft_report.get("accuracy", 0.0),
    },
    "keyword_baseline": {
        "per_class":        {cat: bl_report[cat] for cat in CATEGORY_NAMES},
        "macro_avg":        bl_report["macro avg"],
        "weighted_avg":     bl_report["weighted avg"],
        "accuracy":         bl_report.get("accuracy", 0.0),
    },
    "n_test_samples": len(test_texts),
    "category_names": CATEGORY_NAMES,
}

DATA_DIR.mkdir(exist_ok=True)
with open(RESULTS_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Results saved to {RESULTS_PATH}")
print("\nNext step: Flask will auto-load the fine-tuned model.")
print("Restart your app and detect_wellbeing_tags() now uses DistilBERT.")
