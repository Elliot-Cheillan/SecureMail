import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import sqlite3
import pickle
import os
from config import DATABASE_FINAL_PATH, MODEL_PATH, SCALER_PATH, SAVED_DIR
from securemail_net import SecureMailNet
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def train():
    with sqlite3.connect(DATABASE_FINAL_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM Features_Normalized", conn)

    features_np = df.drop(["Label", "ID"], axis=1).values
    target = torch.tensor(df["Label"].values, dtype=torch.float)

    X_train_np, X_test_np, y_train, y_test = train_test_split(
        features_np, target, test_size=0.2, shuffle=True, random_state=0
    )

    scaler = (
        StandardScaler()
    )  # VERY IMPORTANT, I forgot to standardize the features, so I did it here, and save the scaler for using it again
    # the scaler is stocked in the saved directory.
    X_train = torch.tensor(scaler.fit_transform(X_train_np), dtype=torch.float)
    X_test = torch.tensor(scaler.transform(X_test_np), dtype=torch.float)

    os.makedirs(SAVED_DIR, exist_ok=True)
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)

    n_features = X_train.shape[1]
    model = SecureMailNet(n_features)
    loss_fn = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(
        model.parameters(), lr=0.01
    )  # tested with multiple values of lr, but more it grows, more the model is bad, the balance point is near from this value
    # (surely there is a better value but with 0.01 it workds well)

    for epoch in range(
        150
    ):  # I tested with multiples epoch, with a batch size at 256, and the training dataset with 36k mails, I think 150 is good
        # after 150, it stagnates, before 50, he's not train enough
        model.train()

        pred = model(X_train)
        loss = loss_fn(pred, y_train)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            train_preds = (torch.sigmoid(model(X_train)) > 0.5).float()
            train_acc = (train_preds == y_train).float().mean()
            test_preds = (torch.sigmoid(model(X_test)) > 0.5).float()
            test_acc = (test_preds == y_test).float().mean()

        print(
            f"Epoch {epoch} | Loss: {loss.item():.4f} | Train: {train_acc:.2%} | Test: {test_acc:.2%}"
        )

    torch.save(model.state_dict(), MODEL_PATH)
    print(f"\nModel saved — Final test accuracy: {test_acc:.2%}")

    # For info, the model trained on old mails, with a not perfect parsing, the features are impacted, not good variety for mails attacks
    # not enough mails, not recent dataset, so it's trained on nearly 18k old mails and 18k recent mails, the model learn on surely a bad
    # dataset but I made my best and I can't get a better dataset with labelling and .eml, so actually the current model and the best I made
    # have a 96% accuracy on the test dataset. I don't think I can go further with the bad datas, not perfect parsing, and featuring with
    # values arbitrary defined.


if __name__ == "__main__":
    train()
