import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PREDICTION_PATH = (
    PROJECT_ROOT
    / "data/processed/predictions/islam_vs_volk_1.json"
)

app = FastAPI(title="UFC Fight Predictor API")


class ModelPrediction(BaseModel):
    name: str
    islamWinProbability: float = Field(
        ge=0,
        le=100,
        allow_inf_nan=False,
    )
    description: str


class MatchupPrediction(BaseModel):
    fightId: str
    fighterA: str
    fighterB: str
    fightDate: str
    trainingCutoff: str
    trainingFights: int = Field(gt=0)
    featureCount: int = Field(gt=0)
    predictions: list[ModelPrediction]


@app.get(
    "/api/predictions/islam-vs-volk-1",
    response_model=MatchupPrediction,
)
def get_matchup_prediction():
    if not PREDICTION_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="Predictions unavailable. Run export_matchup.py first.",
        )

    data = json.loads(
        PREDICTION_PATH.read_text(encoding="utf-8")
    )

    return MatchupPrediction.model_validate(data)