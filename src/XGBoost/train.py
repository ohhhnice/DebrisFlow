import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
import os

# 设置参数
params = {
    "objective": "binary:logistic",
    "max_depth": 4,
    "eta": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "eval_metric": "logloss",
    "seed": 42,
}


def train_xgboost(
    csv_name: str,
    src_folder: str,
    dst_folder: str,
    label_colname: str,
    test_size: float = 0.2,
    num_rounds: int = 100,
    random_state: int = 42,
):
    train_data_csv = os.path.join(src_folder, csv_name)
    data = pd.read_csv(train_data_csv)
    X = data.drop(label_colname, axis=1)
    y = data[label_colname]

    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    # 转换为DMatrix格式
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)

    model = xgb.train(params, dtrain, num_rounds)

    # 预测并评估模型
    y_pred = model.predict(dtest)
    y_pred_binary = [1 if p > 0.5 else 0 for p in y_pred]
    accuracy = accuracy_score(y_test, y_pred_binary)
    print(f"Accuracy: {accuracy:.4f}")

    dst_path = os.path.join(dst_folder, f"xgboost_model_Accuracy_{accuracy:.4f}.model")
    model.save_model(dst_path)
