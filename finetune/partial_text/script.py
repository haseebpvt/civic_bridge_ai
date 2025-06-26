from datasets import load_dataset
from huggingface_hub import snapshot_download
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)

# 1) Download the Granite base checkpoint
local_path = snapshot_download(
    repo_id="ibm-granite/granite-3.3-2b-base",
    cache_dir="./hf_cache"
)

# 2) Load tokenizer + sequence-classification model
tokenizer = AutoTokenizer.from_pretrained(local_path, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(
    local_path,
    local_files_only=True,
    num_labels=2  # Binary classification
)

# 3) Load your CSVs
raw_ds = load_dataset("csv",
                      data_files={"train": "train.csv", "validation": "validate.csv"}
                      )


# 4) Tokenize **and** carry over labels into a "labels" field
def preprocess_function(examples):
    tokens = tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",  # or True
        max_length=128  # adjust to your use case
    )
    tokens["labels"] = examples["label"]  # Must be named "labels"
    return tokens


tokenized_ds = raw_ds.map(preprocess_function, batched=True)

# 5) Rename & set format so Trainer knows to collate inputs + labels
tokenized_ds = tokenized_ds.rename_column("label", "labels")
tokenized_ds.set_format(
    type="torch",
    columns=["input_ids", "attention_mask", "labels"]
)

# 6) Training arguments (you can tweak these)
training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    evaluation_strategy="epoch",
)

# 7) Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_ds["train"],
    eval_dataset=tokenized_ds["validation"],
)

# 8) Train!
trainer.train()
