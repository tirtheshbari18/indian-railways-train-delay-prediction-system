import numpy as np
from typing import Dict, Any
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calculate primary regression evaluation metrics on unseen test data.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    
    mae = float(mean_absolute_error(y_true, y_pred))
    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true, y_pred))
    
    # Residual analysis
    residuals = y_true - y_pred
    mean_residual = float(np.mean(residuals))
    std_residual = float(np.std(residuals))
    
    return {
        "mae": round(mae, 2),
        "mse": round(mse, 2),
        "rmse": round(rmse, 2),
        "r2_score": round(r2, 4),
        "mean_residual": round(mean_residual, 2),
        "std_residual": round(std_residual, 2)
    }

def get_feature_importances(model, feature_names: list) -> Dict[str, float]:
    """
    Extract feature importance weights from tree-based or linear models.
    """
    importances = {}
    try:
        if hasattr(model, "feature_importances_"):
            raw_scores = model.feature_importances_
            total = sum(raw_scores) if sum(raw_scores) > 0 else 1.0
            for name, score in zip(feature_names, raw_scores):
                importances[name] = round(float(score / total) * 100, 2)
        elif hasattr(model, "coef_"):
            raw_scores = np.abs(model.coef_)
            total = sum(raw_scores) if sum(raw_scores) > 0 else 1.0
            for name, score in zip(feature_names, raw_scores):
                importances[name] = round(float(score / total) * 100, 2)
        else:
            for name in feature_names:
                importances[name] = round(100.0 / len(feature_names), 2)
    except Exception:
        for name in feature_names:
            importances[name] = round(100.0 / len(feature_names), 2)
            
    # Sort descending
    sorted_importances = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))
    return sorted_importances
