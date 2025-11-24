import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
import numpy as np
import matplotlib.pyplot as plt



def random_forest_model_post_game_stats():
    df = pd.read_csv('stats/final_data.csv')
    df = df.select_dtypes(include=['number'])

    drop_cols = ["GAME_ID", "TEAM_ID","TEAM_NAME", "TEAM_ABBREVIATION", "SEASON", "MIN", "PIE", "PTS", "PLUS_MINUS"]
    # i dropped PIE, PTS, PLUS_MINUS because they show too much about the outcome of the game
    drop_cols = [c for c in drop_cols if c in df.columns]
    df = df.drop(columns=drop_cols)

    target = "RESULT"
    X = df.drop(columns=[target])
    print(f"Columns used: {X.columns}")
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    random_forest = RandomForestClassifier(
    n_estimators=100,
    criterion='gini',  # gini index
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=None,
    oob_score=True,
    bootstrap=True
)
    random_forest.fit(X_train, y_train)
    preds = random_forest.predict(X_test)

    importance = random_forest.feature_importances_
    features = X.columns
    forest_importances = pd.Series(importance, index=features)
    std = np.std([tree.feature_importances_ for tree in random_forest.estimators_], axis=0)
    fig, ax = plt.subplots()
    forest_importances.plot.bar(yerr=std, ax=ax)
    ax.set_title("Feature importances using MDI")
    ax.set_ylabel("Mean decrease in impurity")
    fig.tight_layout()
    plt.show()

    accuracy = accuracy_score(y_test, preds)
    conf_mat = confusion_matrix(y_test, preds)
    display_conf_mat = ConfusionMatrixDisplay(confusion_matrix=conf_mat, display_labels=random_forest.classes_)

    print(f"Random Forest Classifier Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, preds))
    print("Confusion Matrix:")
    print(conf_mat)
    display_conf_mat.plot()
    plt.show()

def random_forest_model_pre_game_stats():
    df = pd.read_csv("stats/final_data.csv")

    df = df.sort_values(["TEAM_ID", "SEASON"])

    # DO NOT drop TEAM_ID yet
    drop_cols = ["GAME_ID", "TEAM_NAME", "TEAM_ABBREVIATION", "SEASON", "MIN","COVID_FLAG"]
    drop_cols = [c for c in drop_cols if c in df.columns]
    df = df.drop(columns=drop_cols)

    target = "RESULT"

    X = (
        df.drop(columns=[target])
        .select_dtypes(include=["number"])
        .drop(columns=["TEAM_ID"])
    )
    # computes rolling means for game before stats
    rolling = (
        df.groupby("TEAM_ID")[X.columns]
        .rolling(window=10, min_periods=1)
        .mean()
        .shift(1)  # critical: pre-game
        .reset_index(level=0, drop=True)
    )

    # now include rolling pre-game stats as new columns
    for col in X.columns:
        df[f"{col}_pre"] = rolling[col]


    # NOW DROP the original post-game stats
    df = df.drop(columns=["PIE","PTS","PLUS_MINUS",'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
       'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PF',
       'EFG_PCT', 'WIN_PCT'])

    df = df.drop(columns=["TEAM_ID"])
    df = df.dropna()

    # final training setup
    X = df.drop(columns=[target]).select_dtypes(include=["number"])
    y = df[target]

    print(f"Columns used: {X.columns}")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    random_forest = RandomForestClassifier(
        n_estimators=100,
        criterion='gini',  # gini index
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=None,
        oob_score=True,
        bootstrap=True
    )
    random_forest.fit(X_train, y_train)
    preds = random_forest.predict(X_test)

    importance = random_forest.feature_importances_
    features = X.columns
    forest_importances = pd.Series(importance, index=features)
    std = np.std([tree.feature_importances_ for tree in random_forest.estimators_], axis=0)
    fig, ax = plt.subplots()
    forest_importances.plot.bar(yerr=std, ax=ax)
    ax.set_title("Feature importances using MDI")
    ax.set_ylabel("Mean decrease in impurity")
    fig.tight_layout()
    plt.show()

    accuracy = accuracy_score(y_test, preds)
    conf_mat = confusion_matrix(y_test, preds)
    display_conf_mat = ConfusionMatrixDisplay(confusion_matrix=conf_mat, display_labels=random_forest.classes_)

    print(f"Random Forest Classifier Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, preds))
    print("Confusion Matrix:")
    print(conf_mat)
    display_conf_mat.plot()
    plt.show()


if __name__ == "__main__":
    random_forest_model_pre_game_stats()