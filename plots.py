import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os
from constants import COLS, CLASSES, SUPERIOR


def payoff_histogram(df: pd.DataFrame):
    # Create results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)
    
    payoff_col = df[COLS['payoff']]
    human_deal_mask = df[COLS['human_deal']]
    payoff_col_with_deal = payoff_col[human_deal_mask]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # All payoffs
    ax1.hist(payoff_col, bins=7, edgecolor='black', alpha=0.7)
    ax1.axvline(payoff_col.mean(), color='red', linestyle='--', 
                label=f'Mean: {payoff_col.mean():.1f}')
    ax1.axvline(payoff_col.median(), color='green', linestyle='--', 
                label=f'Median: {payoff_col.median():.1f}')
    ax1.set_title('All Payoffs')
    ax1.legend()

    # Payoffs when players reach a deal
    ax2.hist(payoff_col_with_deal, bins=7, edgecolor='black', alpha=0.7)
    ax2.axvline(payoff_col_with_deal.mean(), color='red', linestyle='--', 
                label=f'Mean: {payoff_col_with_deal.mean():.1f}')
    ax2.axvline(payoff_col_with_deal.median(), color='green', linestyle='--', 
                label=f'Median: {payoff_col_with_deal.median():.1f}')
    ax2.set_title('Payoffs when Players reach a Deal')
    ax2.legend()

    plt.tight_layout()
    
    # Save as JPG
    output_path = 'results/payoff_histogram.jpg'
    plt.savefig(output_path, format='jpg', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Payoff histograms saved: {output_path}")


def comprehension_stacked_barchart(df: pd.DataFrame):
    # Create results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)

    mistakes_col = df[COLS['comprehension_mistakes']]
    role_col = df[COLS['is_manager']]

    # Stacked bar chart by role
    ct = pd.crosstab(role_col, mistakes_col, normalize='index') * 100
    ct.plot(kind='bar', stacked=True, figsize=(10, 6))
    plt.ylabel('Percentage (%)')
    plt.xlabel('Role (is_manager)')
    plt.title('Comprehension Mistakes Distribution by Role')
    plt.legend(title='Mistakes', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=0)
    plt.tight_layout()
    
    # Save as JPG
    output_path = 'results/comprehension_stacked_barchart.jpg'
    plt.savefig(output_path, format='jpg', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Comprehension barchart saved: {output_path}")


# Filter by class_a first, then by baseline

def num_of_decisions_by_class(df: pd.DataFrame):

    df_managers = df[df[COLS['is_manager']]]

    for c in CLASSES:
        data = df_managers[df_managers[COLS['product_class']] == c]
        
        baseline_1 = data[data['session.config.baseline'] == 1][COLS['second_mover_choice']]
        baseline_0 = data[data['session.config.baseline'] == 0][COLS['second_mover_choice']]

        # Get value counts and align indices
        baseline_1_counts = baseline_1.value_counts().sort_index()
        baseline_0_counts = baseline_0.value_counts().sort_index()

        # Get all unique choices across both conditions
        all_choices = sorted(set(baseline_1_counts.index) | set(baseline_0_counts.index))

        # Reindex both series to have the same index (fill missing with 0)
        baseline_1_counts = baseline_1_counts.reindex(all_choices, fill_value=0)
        baseline_0_counts = baseline_0_counts.reindex(all_choices, fill_value=0)

        # Create figure
        plt.figure(figsize=(10, 6))

        # Use tab10 colormap for normal colors
        colors = plt.cm.tab10(np.arange(len(all_choices)))

        # Set up positions - two groups closer together
        x_baseline_0 = 0
        x_baseline_1 = 0.8
        width = 0.08

        # Plot bars for each choice
        for i, choice in enumerate(all_choices):
            plt.bar(x_baseline_0 + i * width, baseline_0_counts[choice], width, 
                    color=colors[i], alpha=0.8)
            plt.bar(x_baseline_1 + i * width, baseline_1_counts[choice], width, 
                    color=colors[i], alpha=0.8)

        # Create custom legend with relabeled choices
        choice_labels = {
            'AJ': 'Option B (AI if treated)',
            'HS': 'Option A'
        }
        handles = [plt.Rectangle((0,0),1,1, color=colors[i], alpha=0.8) for i in range(len(all_choices))]
        labels = [choice_labels.get(choice, f'Choice {choice}') for choice in all_choices]
        plt.legend(handles, labels, title='Participant Choice')

        # Add labels and title
        plt.xlabel('Treatment')
        plt.ylabel('Frequency')
        plt.title(f'Number of decisions (Class {c}) (SUPERIOR: Option {SUPERIOR[c]})')
        plt.xticks([x_baseline_0 + (len(all_choices)-1)*width/2, x_baseline_1 + (len(all_choices)-1)*width/2], 
                ['AI Treatment', 'Control'])
        plt.grid(axis='y', alpha=0.5)

        plt.tight_layout()

        # Save as JPG
        output_path = f'results/num_of_decisions_class_{c}.jpg'
        plt.savefig(output_path, format='jpg', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Number of decisions by class barchart saved: {output_path}")