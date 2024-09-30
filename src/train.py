import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from lightgbm import LGBMClassifier
from omegaconf import OmegaConf
import mlflow


# Path to train.py
file_path = os.path.dirname(__file__)

# Read configuration file
conf = OmegaConf.load(os.path.join(file_path, "config.yml"))


mlflow.set_experiment("credit-card-exp")


def train(df, params):
    with mlflow.start_run():
         # Get features and target name
        features = df.columns.to_list()[1:-1]
        target = df.columns.to_list()[-1]

        # Train test split
        df_train, df_test = train_test_split(df, test_size=0.3, random_state=23)

        # Train model
        mlflow.log_params(params)
        clf = LGBMClassifier(**params)
        clf.fit(df_train[features], df_train[target])
        
        #meta dado do modelo
        signature = mlflow.models.infer_signature(df_train[features], clf.predict(df_train[features]))
        mlflow.sklearn.log_model(clf, "model", signature=signature, input_example=df_train[features].iloc[:2])

        # Evaluate
        gini_train = (2 * roc_auc_score(df_train[target], clf.predict_proba(df_train[features])[:, 1]) - 1  )
        gini_test = ( 2 * roc_auc_score(df_test[target], clf.predict_proba(df_test[features])[:, 1]) - 1)

        mlflow.log_metric("gini_train", gini_train)
        mlflow.log_metric("gini_test", gini_test)
        # Show results
        print(f"Gini train: {gini_train:.3f}")
        print(f"Gini test:  {gini_test:.3f}")


def main():
    # Load data
    data_path = os.path.join(file_path, "..", "data", "UCI_Credit_Card.csv")
    df = pd.read_csv(data_path)

    # Train model
    train(df, conf["parameters"])


if __name__ == "__main__":
    main()
