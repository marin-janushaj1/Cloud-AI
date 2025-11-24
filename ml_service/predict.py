"""
ML Prediction Service - Core Logic
Handles predictions for both Housing and Electricity models
"""
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelPredictor:
    """Handles model loading and predictions"""

    def __init__(self, base_path: str = None):
        # Use environment variable if available, otherwise use default
        import os
        if base_path is None:
            base_path = os.getenv('MODEL_BASE_PATH', '../data/clean')

        self.base_path = Path(base_path)
        self.housing_model = None
        self.housing_encoder = None
        self.housing_features = None
        self.electricity_model = None
        self._load_models()

    def _load_models(self):
        """Load all trained models"""
        try:
            # Load housing model
            housing_path = self.base_path / "best_model.pkl"
            if housing_path.exists():
                bundle = joblib.load(housing_path)
                self.housing_model = bundle['model']
                self.housing_encoder = bundle.get('target_encoder')
                self.housing_features = bundle.get('feature_names')
                logger.info(f"✓ Loaded housing model: {bundle.get('model_name')}")
            else:
                logger.warning(f"Housing model not found at {housing_path}")

            # Load electricity model if it exists
            elec_path = self.base_path / "electricity_model.pkl"
            if elec_path.exists():
                self.electricity_model = joblib.load(elec_path)
                logger.info("✓ Loaded electricity model")
            else:
                logger.warning(f"Electricity model not found at {elec_path}")

        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise

    def predict_housing(self, property_type: str, is_new: str, duration: str,
                       county: str, year: int, month: int) -> Dict[str, Any]:
        """
        Predict UK housing price

        Args:
            property_type: D, S, T, F, O (Detached, Semi, Terraced, Flat, Other)
            is_new: Y or N (New build or established)
            duration: F, L, U (Freehold, Leasehold, Unknown)
            county: UK county name (uppercase)
            year: Year of transfer (1995-2025)
            month: Month (1-12)

        Returns:
            Dictionary with prediction and confidence interval
        """
        if self.housing_model is None:
            raise ValueError("Housing model not loaded")

        try:
            # Calculate quarter from month
            quarter = (month - 1) // 3 + 1

            # Create feature dataframe
            row = pd.DataFrame([{
                "type": property_type,
                "is_new": is_new,
                "duration": duration,
                "county": county.upper(),
                "year": year,
                "month": month,
                "quarter": quarter
            }])

            # Target encode county
            if self.housing_encoder is not None:
                try:
                    enc_df = self.housing_encoder.transform(row[["county"]])
                    row["county_encoded"] = enc_df["county"]
                except:
                    row["county_encoded"] = 0.0
            else:
                row["county_encoded"] = 0.0

            row = row.drop(columns=["county"])

            # One-hot encode categorical features
            row = pd.get_dummies(row, columns=["type", "is_new", "duration"], drop_first=False)

            # Drop reference categories to match training
            cols_to_drop = ['type_D', 'is_new_N', 'duration_F']
            row = row.drop(columns=[col for col in cols_to_drop if col in row.columns])

            # Align to training features
            if self.housing_features is not None:
                for col in self.housing_features:
                    if col not in row.columns:
                        row[col] = 0
                row = row[self.housing_features]

            # Predict (model returns log-transformed values)
            y_log = self.housing_model.predict(row)[0]

            # Convert back from log scale
            predicted_price = float(np.expm1(y_log))

            # Calculate confidence interval (using MAE from training)
            mae = 122353  # From model metrics
            confidence_lower = max(1000, predicted_price - 2 * mae)
            confidence_upper = predicted_price + 2 * mae

            return {
                "price": round(predicted_price, 2),
                "price_log": round(y_log, 4),
                "confidence_lower": round(confidence_lower, 2),
                "confidence_upper": round(confidence_upper, 2),
                "model": "LightGBM",
                "features_used": len(self.housing_features) if self.housing_features else 0
            }

        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise

    def predict_electricity(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict UK electricity demand

        Args:
            features: Dictionary with required features for electricity model

        Returns:
            Dictionary with prediction
        """
        if self.electricity_model is None:
            raise ValueError("Electricity model not loaded")

        try:
            # TODO: Implement electricity prediction logic
            # This depends on your specific electricity model
            raise NotImplementedError("Electricity prediction not yet implemented")

        except Exception as e:
            logger.error(f"Electricity prediction error: {e}")
            raise

    def health_check(self) -> Dict[str, Any]:
        """Check if models are loaded and ready"""
        return {
            "housing_model_loaded": self.housing_model is not None,
            "electricity_model_loaded": self.electricity_model is not None,
            "housing_model_type": type(self.housing_model).__name__ if self.housing_model else None,
            "status": "healthy" if self.housing_model is not None else "degraded"
        }


# Global predictor instance
predictor: Optional[ModelPredictor] = None


def get_predictor() -> ModelPredictor:
    """Get or create global predictor instance"""
    global predictor
    if predictor is None:
        predictor = ModelPredictor()
    return predictor
