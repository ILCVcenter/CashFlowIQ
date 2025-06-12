"""
ui/chart_helpers.py - Helper functions for improved chart display
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from datetime import datetime

def format_currency(value, pos=None):
    """Format currency with comma thousands separator"""
    return f'${value:,.0f}'

def format_date_labels(ax, dates, max_labels=10):
    """Format and limit date labels for better readability"""
    if len(dates) > max_labels:
        # Show only every nth label
        step = len(dates) // max_labels
        for i, label in enumerate(ax.get_xticklabels()):
            if i % step != 0:
                label.set_visible(False)
    
    # Rotate labels for better fit
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

def apply_chart_styling(ax, title, xlabel, ylabel):
    """Apply consistent styling to charts"""
    ax.set_facecolor('#181943')
    ax.set_title(title, fontsize=10, color='white', pad=15, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=8, color='white')
    ax.set_ylabel(ylabel, fontsize=8, color='white')
    
    # Format y-axis with currency
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
    
    # Style ticks
    ax.tick_params(axis='x', labelsize=7, colors='white')
    ax.tick_params(axis='y', labelsize=7, colors='white')
    
    # Style spines
    for spine in ax.spines.values():
        spine.set_color('white')
        spine.set_linewidth(0.5)
    
    # Add grid
    ax.grid(axis='y', linestyle='--', alpha=0.3, color='white')
    ax.set_axisbelow(True)

def create_figure(width=4, height=3):
    """Create a figure with consistent styling"""
    fig, ax = plt.subplots(figsize=(width, height), facecolor='#181943')
    return fig, ax

def format_month_labels(dates):
    """Format month labels consistently"""
    if isinstance(dates[0], str):
        return [datetime.strptime(d, '%Y-%m').strftime('%b %Y') for d in dates]
    else:
        return [d.strftime('%b %Y') for d in dates] 