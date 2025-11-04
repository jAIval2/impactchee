#!/usr/bin/env python3
"""
Impact Chee Training Script

This script trains a BERT-based model to classify company annual reports
based on their GHG emissions disclosure level (Scope 1, 2, and 3).
"""

import os
import json
import argparse
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import get_linear_schedule_with_warmup
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')


class EmissionsDataset(Dataset):
    """Custom Dataset for emissions classification"""
    
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }


def train_epoch(model, dataloader, optimizer, scheduler, device, class_weights=None):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    
    for batch in tqdm(dataloader, desc="Training"):
        optimizer.zero_grad()
        
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )
        
        loss = outputs.loss
        
        # Apply class weights if provided
        if class_weights is not None:
            # Recompute loss with class weights
            logits = outputs.logits
            loss_fn = torch.nn.CrossEntropyLoss(weight=class_weights)
            loss = loss_fn(logits, labels)
        
        total_loss += loss.item()
        
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
    
    return total_loss / len(dataloader)


def evaluate(model, dataloader, device):
    """Evaluate model on validation set"""
    model.eval()
    predictions = []
    true_labels = []
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )
            
            logits = outputs.logits
            preds = torch.argmax(logits, dim=1)
            
            predictions.extend(preds.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())
    
    accuracy = accuracy_score(true_labels, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(
        true_labels, predictions, average='binary'
    )
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'predictions': predictions,
        'true_labels': true_labels
    }


def main():
    parser = argparse.ArgumentParser(
        description='Train emissions classification model'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        default='dataset.csv',
        help='Path to training dataset'
    )
    parser.add_argument(
        '--validation',
        type=str,
        required=True,
        help='Path to validation dataset'
    )
    parser.add_argument(
        '--model_dir',
        type=str,
        default='./model',
        help='Directory to save model'
    )
    parser.add_argument(
        '--batch_size',
        type=int,
        default=16,
        help='Batch size for training'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=3,
        help='Number of training epochs'
    )
    parser.add_argument(
        '--learning_rate',
        type=float,
        default=2e-5,
        help='Learning rate'
    )
    parser.add_argument(
        '--max_length',
        type=int,
        default=512,
        help='Maximum token length'
    )
    
    args = parser.parse_args()
    
    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load datasets
    print("\nLoading datasets...")
    if not os.path.exists(args.dataset):
        print(f"Error: Training dataset not found: {args.dataset}")
        return
    
    if not os.path.exists(args.validation):
        print(f"Error: Validation dataset not found: {args.validation}")
        return
    
    train_df = pd.read_csv(args.dataset)
    val_df = pd.read_csv(args.validation)
    
    print(f"Training samples: {len(train_df)}")
    print(f"Validation samples: {len(val_df)}")
    print(f"Training label distribution:\n{train_df['label'].value_counts()}")
    print(f"Validation label distribution:\n{val_df['label'].value_counts()}")
    
    # Initialize tokenizer and model
    print("\nInitializing model...")
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertForSequenceClassification.from_pretrained(
        'bert-base-uncased',
        num_labels=2
    )
    model.to(device)
    
    # Create datasets
    train_dataset = EmissionsDataset(
        train_df['text_excerpt'].values,
        train_df['label'].values,
        tokenizer,
        max_length=args.max_length
    )
    
    val_dataset = EmissionsDataset(
        val_df['text_excerpt'].values,
        val_df['label'].values,
        tokenizer,
        max_length=args.max_length
    )
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False
    )
    
    # Calculate class weights to handle imbalance
    label_counts = train_df['label'].value_counts().sort_index()
    total_samples = len(train_df)
    class_weights = torch.tensor([
        total_samples / (2 * label_counts[0]),  # Weight for label 0
        total_samples / (2 * label_counts[1])   # Weight for label 1
    ], dtype=torch.float).to(device)
    print(f"\nClass weights: {class_weights.cpu().numpy()}")
    
    # Setup optimizer and scheduler
    optimizer = AdamW(model.parameters(), lr=args.learning_rate)
    total_steps = len(train_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=0,
        num_training_steps=total_steps
    )
    
    # Training loop
    print("\nStarting training...")
    best_f1 = 0
    
    for epoch in range(args.epochs):
        print(f"\nEpoch {epoch + 1}/{args.epochs}")
        
        # Train
        train_loss = train_epoch(model, train_loader, optimizer, scheduler, device, class_weights)
        print(f"Training loss: {train_loss:.4f}")
        
        # Evaluate
        val_metrics = evaluate(model, val_loader, device)
        print(f"Validation accuracy: {val_metrics['accuracy']:.4f}")
        print(f"Validation precision: {val_metrics['precision']:.4f}")
        print(f"Validation recall: {val_metrics['recall']:.4f}")
        print(f"Validation F1: {val_metrics['f1']:.4f}")
        
        # Save best model
        if val_metrics['f1'] > best_f1:
            best_f1 = val_metrics['f1']
            os.makedirs(args.model_dir, exist_ok=True)
            model.save_pretrained(args.model_dir)
            tokenizer.save_pretrained(args.model_dir)
            print(f"✓ Model saved (F1: {best_f1:.4f})")
    
    # Final evaluation
    print("\n" + "="*70)
    print("FINAL EVALUATION")
    print("="*70)
    
    final_metrics = evaluate(model, val_loader, device)
    print(f"Final Accuracy: {final_metrics['accuracy']:.4f}")
    print(f"Final Precision: {final_metrics['precision']:.4f}")
    print(f"Final Recall: {final_metrics['recall']:.4f}")
    print(f"Final F1: {final_metrics['f1']:.4f}")
    
    # Prepare output with evaluation metrics
    output = {
        'files_used_for_training': int(train_df['company_name'].nunique()),
        'exchanges_in_dataset': sorted(train_df['exchange'].unique().tolist()),
        'accuracy': round(final_metrics['accuracy'], 2),
        'precision': round(final_metrics['precision'], 2),
        'recall': round(final_metrics['recall'], 2),
        'f1': round(final_metrics['f1'], 2)
    }
    
    # Print JSON output to stdout
    print("\n" + "="*70)
    print("OUTPUT")
    print("="*70)
    print(json.dumps(output))


if __name__ == "__main__":
    main()
