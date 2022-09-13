# evaluate multioutput regression model with k-fold cross-validation
from numpy import absolute
from numpy import mean
from numpy import std
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold

# create datasets
X, y = make_regression(n_samples=1000, n_features=10, n_informative=5, n_targets=2, random_state=1, noise=0.5)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=0)
print(X_train.shape, y_train.shape)
# define model
model = LinearRegression()
# define the evaluation procedure
cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
# evaluate the model and collect the scores
n_scores = cross_val_score(
    model, X_train, y_train, cv=cv, n_jobs=-1, 
    #scoring='neg_mean_absolute_error'
    )

# force the scores to be positive
#n_scores = absolute(n_scores)
# summarize performance
print(n_scores.mean())
print('MAE: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))


# Re-train the model
model.fit(X_train, y_train)
# Evaluate the model on test dataset
print(model.score(X_test, y_test))


# make a prediction
row = [0.21947749, 0.32948997, 0.81560036, 0.440956, -0.0606303, -0.29257894, -0.2820059, -0.00290545, 0.96402263, 0.04992249]
yhat = model.predict([row])
# summarize prediction
print(yhat[0])