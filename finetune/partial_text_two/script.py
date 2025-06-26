#!/usr/bin/env python
# finetune_granite_mps.py  –  works on older transformers + low-VRAM Macs

import torch.nn as nn
from datasets import load_dataset
from huggingface_hub import snapshot_download
from transformers import (
    AutoConfig,
    AutoTokenizer,
    AutoModel,
    PreTrainedModel,
    TrainingArguments,
    Trainer,
)
from transformers.modeling_outputs import SequenceClassifierOutput

# ─── CONSTANTS ──────────────────────────────────────────────────────────
REPO_ID = "ibm-granite/granite-3.3-2b-base"
CACHE_DIR = "./granite-3.3-2b-base"
TRAIN_CSV = "train.csv"  # columns: text,label
VAL_CSV = "validate.csv"
NUM_LABELS = 2
MAX_LEN = 64  # shorter seq to fit VRAM
BATCH_SIZE = 1  # per-device batch (MPS ≤18 GB)
ACC_STEPS = 8  # so “effective” batch ≈ 8
EPOCHS = 3
OUTPUT_DIR = "granite_cls_mps"

# ─── 1) DOWNLOAD MODEL ─────────────────────────────────────────────────
print("⏬  downloading Granite checkpoint …")
ckpt_path = snapshot_download(
    repo_id=REPO_ID,
    cache_dir=CACHE_DIR,
    local_dir=CACHE_DIR,
    local_dir_use_symlinks=False,
)
print("✅ checkpoint ready:", ckpt_path)

# ─── 2) CONFIG + TOKENIZER ─────────────────────────────────────────────
config = AutoConfig.from_pretrained(ckpt_path, local_files_only=True)
config.num_labels = NUM_LABELS
tokenizer = AutoTokenizer.from_pretrained(ckpt_path, local_files_only=True)


# ─── 3) WRAP WITH CLASSIFICATION HEAD (mean-pool) ──────────────────────
class GraniteSeqClassifier(PreTrainedModel):
    config_class = type(config)

    def __init__(self, config):
        super().__init__(config)
        self.backbone = AutoModel.from_pretrained(ckpt_path, config=config, local_files_only=True)
        dp = (
                getattr(config, "hidden_dropout_prob", None)
                or getattr(config, "hidden_dropout", None)
                or getattr(config, "dropout_p", None)
                or 0.1
        )
        self.dropout = nn.Dropout(dp)
        self.classifier = nn.Linear(config.hidden_size, config.num_labels)
        self.init_weights()

    def forward(self, input_ids, attention_mask=None, labels=None):
        out = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        hidden = out.last_hidden_state  # [b,s,h]
        if attention_mask is not None:  # mean-pool with mask
            mask = attention_mask.unsqueeze(-1)
            hidden = hidden * mask
            pooled = hidden.sum(1) / mask.sum(1).clamp(min=1e-9)
        else:
            pooled = hidden.mean(1)
        logits = self.classifier(self.dropout(pooled))
        loss = None
        if labels is not None:
            loss = nn.CrossEntropyLoss()(logits, labels)
        return SequenceClassifierOutput(loss=loss, logits=logits)


model = GraniteSeqClassifier(config)

# ─── 4) DATA LOAD + TOKENISE ───────────────────────────────────────────
raw = load_dataset("csv", data_files={"train": TRAIN_CSV, "validation": VAL_CSV})


def tok_fn(batch):
    tok = tokenizer(batch["text"], padding="max_length", truncation=True, max_length=MAX_LEN)
    tok["labels"] = batch["label"]
    return tok


tok_ds = raw.map(tok_fn, batched=True)
tok_ds.set_format("torch", columns=["input_ids", "attention_mask", "labels"])

# ─── 5) TRAINING ARGS (old API, step-based) ────────────────────────────
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=ACC_STEPS,  # accum to keep global batch ≈8
    num_train_epochs=EPOCHS,
    learning_rate=5e-5,
    fp16=False,  # MPS backend can’t fp16
    bf16=False,
    logging_steps=50,
    save_steps=200,
    eval_steps=200,
    do_train=True,
    do_eval=True,
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tok_ds["train"],
    eval_dataset=tok_ds["validation"],
)

# ─── 6) TRAIN & SAVE ───────────────────────────────────────────────────
if __name__ == "__main__":
    trainer.train()
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("🎉 fine-tuning complete. Model saved to", OUTPUT_DIR)
