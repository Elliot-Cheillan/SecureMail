import torch
import pandas as pd
import sqlite3
import pickle
import logging
from model.config import DATABASE_FINAL_PATH, MODEL_PATH, SCALER_PATH, X_TRAIN_PATH
from model.securemail_net import SecureMailNet
from model.shap_wrapper import ShapWrapper
import shap
import streamlit as st


logger = logging.getLogger(__name__)


def load_model(model_path=MODEL_PATH, scaler_path=SCALER_PATH):
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)

    n_features = scaler.n_features_in_
    model = SecureMailNet(n_features)
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()
    return model, scaler


def _predict(model, scaler, df):
    features_np = df.drop(["Label", "ID"], axis=1).values
    features_scaled = scaler.transform(features_np)
    features_tensor = torch.tensor(features_scaled, dtype=torch.float)

    with torch.no_grad():
        probs = torch.sigmoid(model(features_tensor))
        preds = (probs > 0.5).float()

    return preds.numpy(), probs.numpy()


def run_inference():
    model, scaler = load_model()

    with sqlite3.connect(DATABASE_FINAL_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM Features_Normalized", conn)

    predictions, probabilities = _predict(model, scaler, df)

    df["Prediction"] = predictions
    df["Spam_Probability"] = probabilities
    df["Result"] = df["Prediction"].map({1.0: "SPAM", 0.0: "HAM"})

    logger.info(f"=== Scan Results : ({len(df)} mails analyzed) ===")

    for _, row in df.iterrows():
        logger.debug(
            f"Mail #{int(row['ID'])} — {row['Result']} (spam probability: {row['Spam_Probability']:.2%})"
        )  # Here I use logger.debug then if we have a lot of mail that are sent to the model, we don't have thousands of
        # prints in the console, it only write on the scan_results.log

    logger.info(f"Spams detected : {int(predictions.sum())} / {len(predictions)}")
    logger.info(f"Spam ratio : {predictions.mean():.2%}")
    logger.info("Check 'scan_results.log' at the root for per-mail details.")
    logger.info("Warning: log file is overwritten on next run, save it if needed !!!")
    return predictions, probabilities


def run_explanation(model, scaler, df):

    # Mail_Tensor
    features_np = df.drop(["Label", "ID"], axis=1).values
    features_scaled = scaler.transform(features_np)
    features_tensor = torch.tensor(features_scaled, dtype=torch.float)

    # Train tensor
    X_train = torch.load(X_TRAIN_PATH)

    wrapped_model = ShapWrapper(model)
    wrapped_model.eval()

    explainer = shap.DeepExplainer(wrapped_model, X_train)
    shap_values = explainer.shap_values(features_tensor)

    values = [v[0] if isinstance(v, list) else v for v in shap_values[0].tolist()]
    feature_names = list(df.drop(columns=["ID", "Label"]).columns)
    shap_dict = dict(zip(feature_names, values))

    return shap_dict
