"""
Data transformation operations for figure generation.

This module provides common statistical and data manipulation operations
used in scientific figure generation.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Callable


def filter_data(df: pd.DataFrame, expr: str) -> pd.DataFrame:
    """
    Filter DataFrame using a query expression.
    
    Args:
        df: Input DataFrame
        expr: Query expression (e.g., "pvalue < 0.05")
        
    Returns:
        Filtered DataFrame
    """
    return df.query(expr, engine="python")


def select_columns(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """
    Select specific columns from DataFrame.
    
    Args:
        df: Input DataFrame
        cols: List of column names to select
        
    Returns:
        DataFrame with selected columns
    """
    return df[cols]


def mutate(df: pd.DataFrame, **newcols) -> pd.DataFrame:
    """
    Add new columns to DataFrame using expressions.
    
    Args:
        df: Input DataFrame
        **newcols: Keyword arguments where key is new column name
                  and value is expression string
                  
    Returns:
        DataFrame with new columns added
    """
    out = df.copy()
    for k, expr in newcols.items():
        out[k] = pd.eval(expr, engine="python", target=out)
    return out


def p_adjust_bh(df: pd.DataFrame, pcol: str, out: str = "p_adj") -> pd.DataFrame:
    """
    Apply Benjamini-Hochberg multiple testing correction.
    
    Args:
        df: Input DataFrame
        pcol: Column name containing p-values
        out: Output column name for adjusted p-values
        
    Returns:
        DataFrame with adjusted p-values
    """
    p = df[pcol].to_numpy()
    
    # Handle NaN values
    mask = ~np.isnan(p)
    p_clean = p[mask]
    
    if len(p_clean) == 0:
        # All NaN values
        df = df.copy()
        df[out] = np.nan
        return df
    
    # BH correction
    order = np.argsort(p_clean)[::-1]  # Descending order
    ranks = np.empty_like(order)
    ranks[order] = np.arange(1, len(p_clean) + 1)
    
    # Calculate adjusted p-values
    adj_clean = np.minimum(1.0, p_clean * len(p_clean) / ranks)
    
    # Enforce monotonicity (adjusted p-values should be non-decreasing)
    for i in range(len(adj_clean) - 1, 0, -1):
        adj_clean[i - 1] = max(adj_clean[i - 1], adj_clean[i])
    
    # Put back in original array with NaN values
    adj = np.full_like(p, np.nan)
    adj[mask] = adj_clean
    
    df = df.copy()
    df[out] = adj
    return df


def log2fc(df: pd.DataFrame, num: str, den: str, out: str = "log2fc", eps: float = 1e-9) -> pd.DataFrame:
    """
    Calculate log2 fold change.
    
    Args:
        df: Input DataFrame
        num: Column name for numerator
        den: Column name for denominator  
        out: Output column name for log2 fold change
        eps: Small value to add to avoid log(0)
        
    Returns:
        DataFrame with log2 fold change column
    """
    df = df.copy()
    df[out] = np.log2((df[num] + eps) / (df[den] + eps))
    return df


def add_significance_labels(df: pd.DataFrame, pcol: str, out: str = "significance") -> pd.DataFrame:
    """
    Add significance level labels based on p-values.
    
    Args:
        df: Input DataFrame
        pcol: Column name containing p-values
        out: Output column name for significance labels
        
    Returns:
        DataFrame with significance labels
    """
    df = df.copy()
    
    conditions = [
        df[pcol] < 0.001,
        df[pcol] < 0.01,
        df[pcol] < 0.05,
        df[pcol] >= 0.05
    ]
    
    choices = ["***", "**", "*", "ns"]
    
    df[out] = np.select(conditions, choices, default="ns")
    return df


# Registry of available transforms
TRANSFORM_REGISTRY: Dict[str, Callable] = {
    "filter": filter_data,
    "select": select_columns,
    "mutate": mutate,
    "p_adjust_bh": p_adjust_bh,
    "log2fc": log2fc,
    "add_significance": add_significance_labels,
}


def apply_pipeline(df: pd.DataFrame, steps: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Apply a series of transformation steps to a DataFrame.
    
    Args:
        df: Input DataFrame
        steps: List of transformation dictionaries with 'op' and 'args' keys
        
    Returns:
        Transformed DataFrame
        
    Raises:
        ValueError: If transformation operation is not recognized
    """
    result = df.copy()
    
    for step in steps:
        op = step["op"]
        args = step.get("args", {})
        
        if op not in TRANSFORM_REGISTRY:
            raise ValueError(f"Unknown transformation: {op}. Available: {list(TRANSFORM_REGISTRY.keys())}")
        
        fn = TRANSFORM_REGISTRY[op]
        
        # Apply transformation
        if args:
            result = fn(result, **args)
        else:
            result = fn(result)
    
    return result


def get_available_transforms() -> List[str]:
    """Get list of available transformation operations."""
    return list(TRANSFORM_REGISTRY.keys())