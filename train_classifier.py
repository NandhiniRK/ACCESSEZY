"""
train_classifier.py
────────────────────────────────────────────────────────────────
Accessezy — Phase 4b: Fine-tuned Wellbeing Classifier

Downloads GoEmotions, remaps 27 labels → 3 wellbeing categories,
fine-tunes distilbert-base-uncased, saves model to:
    models/wellbeing_classifier/

3 categories trained:
    0 — Academic Overload
    1 — Social Stress
    2 — Emotional Regulation

Attendance Concern is handled by keyword rules in ai_engine.py
(no GoEmotions label maps to it cleanly).

Usage:
    python train_classifier.py          # full dataset (~2-4 hrs on CPU)
    python train_classifier.py --fast   # 5k sample subset (~15-20 mins)
────────────────────────────────────────────────────────────────
"""

import os
import sys
import csv
import json
import random
import argparse
import numpy as np
from pathlib import Path

# ── Parse args ───────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--fast", action="store_true",
                    help="Use 5k sample subset for quick training")
parser.add_argument("--epochs", type=int, default=3,
                    help="Number of training epochs (default: 3)")
args = parser.parse_args()

FAST_MODE   = args.fast
NUM_EPOCHS  = args.epochs
MODEL_DIR   = Path("models/wellbeing_classifier")
DATA_DIR    = Path("data")
DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Accessezy — Wellbeing Classifier Training")
print(f"Mode   : {'FAST (5k samples)' if FAST_MODE else 'FULL dataset'}")
print(f"Epochs : {NUM_EPOCHS}")
print("=" * 60)

# ────────────────────────────────────────────────────────────
# STEP 1 — Install dependencies if needed
# ────────────────────────────────────────────────────────────
print("\n[1/5] Checking dependencies...")
try:
    import torch
    import transformers
    import datasets
    import sklearn
    print("✅ All dependencies present.")
except ImportError as e:
    print(f"Missing: {e}")
    print("Run: pip install torch transformers datasets scikit-learn")
    sys.exit(1)

from datasets import load_dataset, Dataset
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    TrainingArguments,
    Trainer,
)
from sklearn.metrics import classification_report, f1_score
import torch

# ────────────────────────────────────────────────────────────
# STEP 2 — GoEmotions label remapping
# ────────────────────────────────────────────────────────────
print("\n[2/5] Defining label remapping...")

# GoEmotions 27 labels (index → name)
GOEMOTIONS_LABELS = [
    "admiration", "amusement", "anger", "annoyance", "approval",
    "caring", "confusion", "curiosity", "desire", "disappointment",
    "disapproval", "disgust", "embarrassment", "excitement", "fear",
    "gratitude", "grief", "joy", "love", "nervousness",
    "optimism", "pride", "realization", "relief", "remorse",
    "sadness", "surprise"
]

# Map GoEmotions label → our wellbeing category (None = discard)
# 0 = Academic Overload
# 1 = Social Stress
# 2 = Emotional Regulation
LABEL_MAP = {
    "anger":         2,   # Emotional Regulation
    "annoyance":     0,   # Academic Overload
    "confusion":     0,   # Academic Overload
    "disappointment":0,   # Academic Overload
    "disapproval":   0,   # Academic Overload
    "disgust":       1,   # Social Stress
    "embarrassment": 1,   # Social Stress
    "fear":          1,   # Social Stress
    "grief":         2,   # Emotional Regulation
    "nervousness":   0,   # Academic Overload
    "remorse":       2,   # Emotional Regulation
    "sadness":       2,   # Emotional Regulation
    # Discard positive/neutral emotions — not relevant to wellbeing concerns
    "admiration":    None,
    "amusement":     None,
    "approval":      None,
    "caring":        None,
    "curiosity":     None,
    "desire":        None,
    "excitement":    None,
    "gratitude":     None,
    "joy":           None,
    "love":          None,
    "optimism":      None,
    "pride":         None,
    "realization":   None,
    "relief":        None,
    "surprise":      None,
}

CATEGORY_NAMES = [
    "Academic Overload",
    "Social Stress",
    "Emotional Regulation"
]

print(f"✅ Remapping {len([v for v in LABEL_MAP.values() if v is not None])} GoEmotions labels → 3 categories.")

# ────────────────────────────────────────────────────────────
# STEP 3 — Load and remap GoEmotions dataset
# ────────────────────────────────────────────────────────────
print("\n[3/5] Loading GoEmotions dataset from HuggingFace...")
print("(This downloads ~80MB on first run — will be cached after)")

try:
    raw_dataset = load_dataset("go_emotions", "simplified")
except Exception as e:
    print(f"\n❌ Failed to load GoEmotions: {e}")
    print("Make sure you have internet access and 'datasets' installed.")
    sys.exit(1)

print(f"✅ Loaded. Splits: {list(raw_dataset.keys())}")


def remap_example(example):
    """
    GoEmotions simplified uses multi-label — take the first label only
    for single-label classification. Returns None if label should be discarded.
    """
    labels = example["labels"]
    if not labels:
        return None
    # Take first label (most prominent)
    raw_label_idx = labels[0]
    raw_label_name = GOEMOTIONS_LABELS[raw_label_idx] if raw_label_idx < len(GOEMOTIONS_LABELS) else None
    if raw_label_name is None:
        return None
    mapped = LABEL_MAP.get(raw_label_name)
    if mapped is None:
        return None
    return {"text": example["text"], "label": mapped}


def build_remapped_dataset(split_data):
    texts, labels = [], []
    for example in split_data:
        remapped = remap_example(example)
        if remapped:
            texts.append(remapped["text"])
            labels.append(remapped["label"])
    return texts, labels


print("Remapping train split...")
train_texts, train_labels = build_remapped_dataset(raw_dataset["train"])
print(f"  Train samples after remap: {len(train_texts)}")

print("Remapping validation split...")
val_texts, val_labels = build_remapped_dataset(raw_dataset["validation"])
print(f"  Val samples after remap  : {len(val_texts)}")

print("Remapping test split...")
test_texts, test_labels = build_remapped_dataset(raw_dataset["test"])
print(f"  Test samples after remap : {len(test_texts)}")

# ── Fast mode: subsample ─────────────────────────────────────
if FAST_MODE:
    random.seed(42)
    n_train = min(4000, len(train_texts))
    n_val   = min(500,  len(val_texts))
    n_test  = min(500,  len(test_texts))

    indices = random.sample(range(len(train_texts)), n_train)
    train_texts  = [train_texts[i]  for i in indices]
    train_labels = [train_labels[i] for i in indices]

    indices = random.sample(range(len(val_texts)), n_val)
    val_texts  = [val_texts[i]  for i in indices]
    val_labels = [val_labels[i] for i in indices]

    indices = random.sample(range(len(test_texts)), n_test)
    test_texts  = [test_texts[i]  for i in indices]
    test_labels = [test_labels[i] for i in indices]

    print(f"\n⚡ FAST MODE: using {n_train} train / {n_val} val / {n_test} test samples")

# ── Save remapped test set for evaluate_classifier.py ────────
test_data_path = DATA_DIR / "goemotions_remapped_test.json"
with open(test_data_path, "w") as f:
    json.dump({"texts": test_texts, "labels": test_labels,
               "category_names": CATEGORY_NAMES}, f)
print(f"✅ Test set saved to {test_data_path}")

# ── Class distribution ────────────────────────────────────────
from collections import Counter
dist = Counter(train_labels)
print("\nTrain label distribution:")
for label_id, count in sorted(dist.items()):
    print(f"  {CATEGORY_NAMES[label_id]}: {count} samples")

# ────────────────────────────────────────────────────────────
# STEP 4 — Tokenize and fine-tune
# ────────────────────────────────────────────────────────────
print("\n[4/5] Tokenizing and fine-tuning DistilBERT...")
print("Model: distilbert-base-uncased")

tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")


def tokenize(texts, labels):
    encodings = tokenizer(texts, truncation=True, padding=True, max_length=128)
    dataset = Dataset.from_dict({
        "input_ids":      encodings["input_ids"],
        "attention_mask": encodings["attention_mask"],
        "labels":         labels
    })
    return dataset


print("Tokenizing...")
train_dataset = tokenize(train_texts, train_labels)
val_dataset   = tokenize(val_texts,   val_labels)
print("✅ Tokenization done.")

# ── Load model ───────────────────────────────────────────────
model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=3,
    id2label={0: "Academic Overload", 1: "Social Stress", 2: "Emotional Regulation"},
    label2id={"Academic Overload": 0, "Social Stress": 1, "Emotional Regulation": 2}
)

# ── Training arguments (CPU-optimised) ───────────────────────
training_args = TrainingArguments(
    output_dir=str(MODEL_DIR / "checkpoints"),
    num_train_epochs=NUM_EPOCHS,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    warmup_steps=100,
    weight_decay=0.01,
    logging_dir=str(MODEL_DIR / "logs"),
    logging_steps=50,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    use_cpu=not torch.cuda.is_available(),
    report_to="none",
)


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    f1 = f1_score(labels, predictions, average="weighted")
    return {"f1": f1}


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)

print(f"\nStarting training ({NUM_EPOCHS} epochs)...")
print("This will take a while on CPU. Go make a cup of tea ☕")
print("-" * 60)
trainer.train()

# ────────────────────────────────────────────────────────────
# STEP 5 — Save model + tokenizer
# ────────────────────────────────────────────────────────────
print(f"\n[5/5] Saving model to {MODEL_DIR}...")
trainer.save_model(str(MODEL_DIR))
tokenizer.save_pretrained(str(MODEL_DIR))

# Save label mapping for ai_engine.py to load
label_config = {
    "id2label": {0: "Academic Overload", 1: "Social Stress", 2: "Emotional Regulation"},
    "label2id": {"Academic Overload": 0, "Social Stress": 1, "Emotional Regulation": 2},
    "category_names": CATEGORY_NAMES
}
with open(MODEL_DIR / "label_config.json", "w") as f:
    json.dump(label_config, f, indent=2)

print("✅ Model saved!")
print("\n" + "=" * 60)
print("Training complete! Next steps:")
print("  1. Run: python evaluate_classifier.py")
print("     → Generates F1/precision/recall + baseline comparison table")
print("  2. The updated ai_engine.py will auto-load the fine-tuned model")
print("     from models/wellbeing_classifier/ on next Flask startup")
print("=" * 60)
