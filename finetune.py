import argparse
import sys
import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch import optim
from torch.utils.tensorboard import SummaryWriter
import yaml
from tqdm import tqdm

from data_utils import Dataset_ASVspoof2019_train, Dataset_ASVspoof2019_devNeval
from model import Model
from tensorboardX import SummaryWriter
from core_scripts.startup_config import set_random_seed


def train_epoch(model, device, train_loader, optimizer, criterion, epoch):
    """Train for one epoch"""
    model.train()
    train_loss = 0.0
    correct = 0
    total = 0
    
    pbar = tqdm(train_loader, desc=f'Epoch {epoch}')
    for batch_idx, (batch_x, batch_y) in enumerate(pbar):
        batch_x = batch_x.to(device)
        batch_y = batch_y.to(device)
        
        optimizer.zero_grad()
        
        # Forward pass
        batch_out = model(batch_x)
        
        # Compute loss
        batch_loss = criterion(batch_out, batch_y)
        
        # Backward pass
        batch_loss.backward()
        optimizer.step()
        
        # Statistics
        train_loss += batch_loss.item()
        _, predicted = torch.max(batch_out.data, 1)
        total += batch_y.size(0)
        correct += (predicted == batch_y).sum().item()
        
        # Update progress bar
        pbar.set_postfix({
            'loss': f'{train_loss/(batch_idx+1):.4f}',
            'acc': f'{100.*correct/total:.2f}%'
        })
    
    train_loss /= len(train_loader)
    train_acc = 100. * correct / total
    
    return train_loss, train_acc


def evaluate(model, device, dev_loader, criterion):
    """Evaluate on validation set"""
    model.eval()
    val_loss = 0.0
    correct = 0
    total = 0
    
    # For EER calculation
    scores = []
    labels = []
    
    with torch.no_grad():
        for batch_x, batch_y in tqdm(dev_loader, desc='Validating'):
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            
            batch_out = model(batch_x)
            batch_loss = criterion(batch_out, batch_y)
            
            val_loss += batch_loss.item()
            _, predicted = torch.max(batch_out.data, 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()
            
            # Store scores for EER
            batch_score = (batch_out[:, 1]).data.cpu().numpy()
            batch_label = batch_y.data.cpu().numpy()
            scores.extend(batch_score)
            labels.extend(batch_label)
    
    val_loss /= len(dev_loader)
    val_acc = 100. * correct / total
    
    # Calculate EER
    eer = calculate_eer(np.array(labels), np.array(scores))
    
    return val_loss, val_acc, eer


def calculate_eer(labels, scores):
    """Calculate Equal Error Rate"""
    from scipy.optimize import brentq
    from scipy.interpolate import interp1d
    from sklearn.metrics import roc_curve
    
    fpr, tpr, thresholds = roc_curve(labels, scores, pos_label=1)
    eer = brentq(lambda x: 1. - x - interp1d(fpr, tpr)(x), 0., 1.)
    return eer * 100


def main(args):
    # Load configuration
    with open(args.config, 'r') as f_yaml:
        config = yaml.safe_load(f_yaml)
    
    # Set random seed
    set_random_seed(config['seed'])
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')
    
    # Create output directory
    os.makedirs(config['out_fold'], exist_ok=True)
    
    # Initialize TensorBoard
    writer = SummaryWriter(os.path.join(config['out_fold'], 'tensorboard'))
    
    # Load datasets
    print('Loading training data...')
    train_set = Dataset_ASVspoof2019_train(
        list_IDs=None,
        labels=None,
        base_dir=os.path.join(config['database_path'], 'ASVspoof2019_LA_train/'),
        algo=5  # RawBoost augmentation
    )
    train_loader = DataLoader(
        train_set,
        batch_size=config['batch_size'],
        shuffle=True,
        num_workers=config['num_workers'],
        drop_last=True
    )
    
    print('Loading validation data...')
    dev_set = Dataset_ASVspoof2019_devNeval(
        list_IDs=None,
        labels=None,
        base_dir=os.path.join(config['database_path'], 'ASVspoof2019_LA_dev/'),
        track='LA'
    )
    dev_loader = DataLoader(
        dev_set,
        batch_size=config['batch_size'],
        shuffle=False,
        num_workers=config['num_workers']
    )
    
    # Initialize model
    print('Initializing model...')
    model = Model(config['model_config'], device)
    model = model.to(device)
    
    # Load pretrained weights if specified
    if args.pretrained_model:
        print(f'Loading pretrained model from {args.pretrained_model}')
        checkpoint = torch.load(args.pretrained_model, map_location=device)
        model.load_state_dict(checkpoint)
        print('Pretrained model loaded successfully')
    
    # Freeze encoder if specified
    if args.freeze_encoder:
        print('Freezing encoder layers...')
        for name, param in model.named_parameters():
            if 'first_bn' in name or 'selu' in name or 'block' in name:
                param.requires_grad = False
        print('Encoder frozen. Only graph layers and classifier will be trained.')
    
    # Print trainable parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f'Total parameters: {total_params:,}')
    print(f'Trainable parameters: {trainable_params:,}')
    
    # Loss function
    criterion = nn.CrossEntropyLoss()
    
    # Optimizer
    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=config['lr'],
        betas=(config['beta_1'], config['beta_2']),
        eps=config['eps'],
        weight_decay=config['weight_decay'],
        amsgrad=config['amsgrad']
    )
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode='min',
        factor=config['lr_decay'],
        patience=config['interval'],
        verbose=True
    )
    
    # Training loop
    best_eer = float('inf')
    patience_counter = 0
    patience = 20  # Early stopping patience
    
    print(f'\nStarting training for {config["num_epochs"]} epochs...\n')
    
    for epoch in range(1, config['num_epochs'] + 1):
        # Train
        train_loss, train_acc = train_epoch(
            model, device, train_loader, optimizer, criterion, epoch
        )
        
        # Validate
        val_loss, val_acc, eer = evaluate(model, device, dev_loader, criterion)
        
        # Learning rate scheduling
        scheduler.step(val_loss)
        current_lr = optimizer.param_groups[0]['lr']
        
        # Log to TensorBoard
        writer.add_scalar('Loss/train', train_loss, epoch)
        writer.add_scalar('Loss/val', val_loss, epoch)
        writer.add_scalar('Accuracy/train', train_acc, epoch)
        writer.add_scalar('Accuracy/val', val_acc, epoch)
        writer.add_scalar('Metrics/EER', eer, epoch)
        writer.add_scalar('Learning_rate', current_lr, epoch)
        
        # Print results
        print(f'\nEpoch {epoch}/{config["num_epochs"]}:')
        print(f'  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%')
        print(f'  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%')
        print(f'  Val EER: {eer:.2f}%')
        print(f'  Learning Rate: {current_lr:.6f}')
        
        # Save checkpoint
        checkpoint_path = os.path.join(
            config['out_fold'], f'epoch_{epoch}.pth'
        )
        torch.save(model.state_dict(), checkpoint_path)
        
        # Save best model
        if eer < best_eer:
            best_eer = eer
            best_path = os.path.join(config['out_fold'], 'best_model.pth')
            torch.save(model.state_dict(), best_path)
            print(f'  *** New best EER: {best_eer:.2f}% - Model saved! ***')
            patience_counter = 0
        else:
            patience_counter += 1
        
        # Early stopping
        if patience_counter >= patience:
            print(f'\nEarly stopping triggered after {epoch} epochs')
            print(f'Best EER: {best_eer:.2f}%')
            break
    
    print('\nTraining completed!')
    print(f'Best EER achieved: {best_eer:.2f}%')
    print(f'Best model saved to: {best_path}')
    
    writer.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AASIST Fine-tuning')
    parser.add_argument('--config', type=str, required=True,
                        help='Path to configuration file')
    parser.add_argument('--pretrained_model', type=str, default=None,
                        help='Path to pretrained model for fine-tuning')
    parser.add_argument('--freeze_encoder', action='store_true',
                        help='Freeze encoder layers and only train classifier')
    
    args = parser.parse_args()
    main(args)
