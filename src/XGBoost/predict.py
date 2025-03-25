import numpy as np
import xgboost as xgb
import pandas as pd
import os


def xgb_predict(
    features_file_name: str,
    src_folder: str,
    model_path: str,
    dst_folder: str,
) -> None:
    feature_path = os.path.join(src_folder, features_file_name)
    save_path = os.path.join(dst_folder, features_file_name)

    xgb_model = xgb.Booster()
    xgb_model.load_model(model_path)

    df = pd.read_csv(feature_path)
    dmat = xgb.DMatrix(df)

    pred_probs = xgb_model.predict(dmat)
    pred_classes = (pred_probs > 0.5).astype(int)
    df["prediction_prob"] = pred_probs
    df["prediction"] = pred_classes

    os.makedirs(dst_folder, exist_ok=True)
    df.to_csv(save_path, index=False)
