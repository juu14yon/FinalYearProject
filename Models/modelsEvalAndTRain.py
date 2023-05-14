from numpy import mean, absolute
import pandas as pd
from sklearn.model_selection import cross_val_score, RepeatedKFold, train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import LinearSVR
from xgboost import XGBRegressor
import pickle, sys, os

# Suppress warnings for readable output
from warnings import simplefilter
if not sys.warnoptions:
    simplefilter("ignore")
    os.environ["PYTHONWARNINGS"] = "ignore" # Also affect subprocesses

# Evaluate model with k-fold validation
# Train and save the model and its predictions
def evalAndTrain(name, model):
    cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
    scoring = "neg_mean_absolute_error"

    score = absolute(cross_val_score(model, X.values, y.values, scoring=scoring, cv=cv, n_jobs=-1))
    print(f"MAE score of {name}: {round(mean(score), 3)}")

    model.fit(X_train.values, y_train.values)
    y_pred = model.predict(X_test.values)

    data = pd.DataFrame()
    data["x1"] = y_test["x"]
    data["y1"] = y_test["y"]
    data["x2"] = [i[0] for i in y_pred]
    data["y2"] = [i[1] for i in y_pred]

    data.to_csv(f"csv/predicted-{name}.csv")
    pickle.dump(model, open(f"pickled/predictor-{name}.sav", 'wb'))

# Read input data
data = pd.read_csv("data/data.csv")
X = data.drop(["x", "y"], axis=1)
y = data[["x", "y"]]

# Split into training and testing data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model_lin = MultiOutputRegressor(LinearRegression())
evalAndTrain("Linear", model_lin)
model_svr = MultiOutputRegressor(LinearSVR())
evalAndTrain("SVR", model_svr)
model_rfr = MultiOutputRegressor(RandomForestRegressor())
evalAndTrain("RF", model_rfr)


# Same thing as above but specifically for XGBoost
model = XGBRegressor()
wrapper = MultiOutputRegressor(model)
cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
score = absolute(cross_val_score(wrapper, X.values, y.values, scoring='neg_mean_absolute_error', cv=cv, n_jobs=-1))

print(f"MAE score of XGBoost: {round(mean(score), 3)}")

wrapper.fit(X_train.values, y_train.values)
y_pred = wrapper.predict(X_test.values)

data = pd.DataFrame()
data["x1"] = y_test["x"]
data["y1"] = y_test["y"]
data["x2"] = [i[0] for i in y_pred]
data["y2"] = [i[1] for i in y_pred]

data.to_csv("csv/predicted-XGBoost.csv")
pickle.dump(model, open("pickled/predictor-XGBoost.sav", 'wb'))