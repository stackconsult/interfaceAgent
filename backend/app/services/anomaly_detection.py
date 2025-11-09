"""
ML-based Anomaly Detection service.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import Anomaly, Event

settings = get_settings()


class AnomalyDetectionService:
    """Service for detecting anomalies using ML."""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.is_trained = False

        if settings.enable_ml_anomaly:
            self._initialize_model()

    def _initialize_model(self):
        """Initialize the anomaly detection model."""
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100,
        )
        self.scaler = StandardScaler()

    async def train_model(self, db: AsyncSession, lookback_days: int = 30):
        """Train the anomaly detection model on historical data."""
        if not settings.enable_ml_anomaly:
            return

        # Fetch historical events
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)
        result = await db.execute(select(Event).where(Event.created_at >= cutoff_date))
        events = result.scalars().all()

        if len(events) < 100:
            return  # Not enough data to train

        # Extract features from events
        features = self._extract_features(events)

        if features:
            # Scale and train
            scaled_features = self.scaler.fit_transform(features)
            self.model.fit(scaled_features)
            self.is_trained = True

    def _extract_features(self, events: List[Event]) -> np.ndarray:
        """Extract numerical features from events."""
        features = []

        for event in events:
            # Example features - customize based on your needs
            feature_vector = [
                len(str(event.payload)) if event.payload else 0,
                event.retry_count,
                hash(event.event_type) % 1000,  # Simple hash for categorical
                hash(event.source) % 1000,
            ]
            features.append(feature_vector)

        return np.array(features)

    async def detect_anomaly(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        detection_type: str = "pattern",
    ) -> Optional[Dict[str, Any]]:
        """Detect if the given data is anomalous."""
        if not settings.enable_ml_anomaly or not self.is_trained:
            return None

        # Extract features from data
        features = self._extract_features_from_dict(data)

        if not features:
            return None

        # Scale features
        scaled_features = self.scaler.transform([features])

        # Predict
        prediction = self.model.predict(scaled_features)
        score = self.model.score_samples(scaled_features)[0]

        # -1 means anomaly, 1 means normal
        if prediction[0] == -1 and abs(score) > settings.anomaly_threshold:
            # Determine severity based on score
            severity = self._calculate_severity(score)

            # Create anomaly record
            anomaly = Anomaly(
                detection_type=detection_type,
                severity=severity,
                description=f"Anomaly detected in {detection_type}",
                data=data,
                score=float(score),
                is_resolved=False,
            )

            db.add(anomaly)
            await db.commit()
            await db.refresh(anomaly)

            return {
                "id": anomaly.id,
                "severity": severity,
                "score": float(score),
                "detected_at": anomaly.created_at.isoformat(),
            }

        return None

    def _extract_features_from_dict(self, data: Dict[str, Any]) -> List[float]:
        """Extract features from a dictionary."""
        # Example feature extraction - customize based on your needs
        features = [
            len(str(data)),
            len(data.keys()) if isinstance(data, dict) else 0,
            hash(str(data.get("type", ""))) % 1000 if "type" in data else 0,
            hash(str(data.get("source", ""))) % 1000 if "source" in data else 0,
        ]
        return features

    def _calculate_severity(self, score: float) -> str:
        """Calculate severity based on anomaly score."""
        abs_score = abs(score)

        if abs_score > 1.5:
            return "critical"
        elif abs_score > 1.2:
            return "high"
        elif abs_score > 0.9:
            return "medium"
        else:
            return "low"


# Global anomaly detection service instance
anomaly_service = AnomalyDetectionService()
