"""Train/test preparation and classification reporting."""

import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split


def xg_prepare_train_test(data, feature_cols, categorical_cols, test_size, random_state):
    """Split labeled rows and align test indicators to training columns."""
    labeled = data[data["priority_tier"].notna()].copy()

    X = labeled[feature_cols].apply(pd.to_numeric, errors="coerce")  # a few cols (e.g. Total_Carbon) carry stray "None" strings
    X[categorical_cols] = labeled[categorical_cols].apply(
        lambda col: col.astype("string").str.strip().replace("", pd.NA).fillna("Missing")
    )
    y = labeled["priority_tier"].cat.codes  # low=0, high=1 (order set by qcut's `labels=`)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Encode categories after splitting; test-only categories use all-zero indicators.
    X_train = pd.get_dummies(X_train, columns=categorical_cols, dtype=int)
    X_test = pd.get_dummies(X_test, columns=categorical_cols, dtype=int).reindex(
        columns=X_train.columns, fill_value=0
    )
    return X_train, X_test, y_train, y_test


def nn_prepare_train_evaluate(data, feature_cols, categorical_cols, test_size, random_state,
                                hidden_layer_sizes=(64, 32)):
    """Same split, same rows, same encoding as xg_prepare_train_test -- calls it directly
    rather than re-deriving the split, so the XGBoost and NN comparison is on an identical
    train/test partition. Adds the imputation + scaling a neural net needs but XGBoost didn't."""
    X_train, X_test, y_train, y_test = xg_prepare_train_test(
        data, feature_cols, categorical_cols, test_size, random_state
    )

    imputer = SimpleImputer(strategy="median")
    X_train_imp = imputer.fit_transform(X_train)
    X_test_imp = imputer.transform(X_test)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_imp)
    X_test_scaled = scaler.transform(X_test_imp)

    model = MLPClassifier(
        hidden_layer_sizes=hidden_layer_sizes,
        activation="relu",
        solver="adam",
        alpha=1e-4,
        early_stopping=True,
        n_iter_no_change=10,
        max_iter=300,
        random_state=random_state,
    )
    model.fit(X_train_scaled, y_train)

    preds = model.predict(X_test_scaled)
    print(f"Accuracy: {accuracy_score(y_test, preds):.3f}")
    print(classification_report(y_test, preds, target_names=["low", "high"]))
    print(confusion_matrix(y_test, preds))
    return model, scaler, imputer


def evaluate_classifier(model, X_test, y_test, class_names):
    """Print test metrics and return predictions for further inspection."""
    preds = model.predict(X_test)
    labels = list(range(len(class_names)))
    print(f"Accuracy: {accuracy_score(y_test, preds):.3f}")
    print(classification_report(
        y_test, preds, labels=labels, target_names=class_names, zero_division=0
    ))
    print(confusion_matrix(y_test, preds, labels=labels))
    return preds
