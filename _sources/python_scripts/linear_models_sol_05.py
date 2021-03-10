# %% [markdown]
# # 📃 Solution for Exercise 05
# In the previous notebook, we presented a non-penalized logistic regression
# classifier. This classifier accepts a parameter `penalty` to add a
# regularization. The regularization strength is set using the parameter `C`.
#
# In this exercise, we ask you to train a l2-penalized logistic regression
# classifier and to find by yourself the effect of the parameter `C`.
#
# We will start by loading the dataset and create the helper function to show
# the decision separation as in the previous code

# %%
import pandas as pd
from sklearn.model_selection import train_test_split

penguins = pd.read_csv("../datasets/penguins_classification.csv")
# only keep the Adelie and Chinstrap classes
penguins = penguins.set_index("Species").loc[
    ["Adelie", "Chinstrap"]].reset_index()

culmen_columns = ["Culmen Length (mm)", "Culmen Depth (mm)"]
target_column = "Species"
data, target = penguins[culmen_columns], penguins[target_column]

data_train, data_test, target_train, target_test = train_test_split(
    data, target, stratify=target, random_state=0,
)
range_features = {
    feature_name: (data[feature_name].min() - 1, data[feature_name].max() + 1)
    for feature_name in data
}

# %%
import numpy as np
import matplotlib.pyplot as plt


def plot_decision_function(fitted_classifier, range_features, ax=None):
    """Plot the boundary of the decision function of a classifier."""
    from sklearn.preprocessing import LabelEncoder

    feature_names = list(range_features.keys())
    # create a grid to evaluate all possible samples
    plot_step = 0.02
    xx, yy = np.meshgrid(
        np.arange(*range_features[feature_names[0]], plot_step),
        np.arange(*range_features[feature_names[1]], plot_step),
    )

    # compute the associated prediction
    Z = fitted_classifier.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = LabelEncoder().fit_transform(Z)
    Z = Z.reshape(xx.shape)

    # make the plot of the boundary and the data samples
    if ax is None:
        _, ax = plt.subplots()
    ax.contourf(xx, yy, Z, alpha=0.4, cmap="RdBu")
    ax.set_xlabel(feature_names[0])
    ax.set_ylabel(feature_names[1])

    return ax


# %% [markdown]
# Given the following candidate for the parameter `C`, find out what is the
# effect of the value of this parameter on the decision boundary and on the
# weights magnitude.

# %%
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

Cs = [0.01, 0.1, 1, 10]
logistic_regression = make_pipeline(
    StandardScaler(), LogisticRegression(penalty="l2"))

# %%
import seaborn as sns

_, axs = plt.subplots(ncols=4, sharey=True, sharex=True, figsize=(16, 4))

weights_ridge = []
for ax, C in zip(axs, Cs):
    logistic_regression.set_params(logisticregression__C=C)
    logistic_regression.fit(data_train, target_train)
    # plot the decision function
    plot_decision_function(logistic_regression, range_features, ax=ax)
    sns.scatterplot(
        x=data_test.iloc[:, 0], y=data_test.iloc[:, 1], hue=target_test,
        palette=["tab:red", "tab:blue"], ax=ax)
    ax.set_title(f"C: {C}")
    # store the weights
    weights_ridge.append(pd.Series(
        logistic_regression[-1].coef_.ravel(), index=data.columns))
plt.subplots_adjust(wspace=0.35)

# %%
weights_ridge = pd.concat(
    weights_ridge, axis=1, keys=[f"C: {C}" for C in Cs])
_ = weights_ridge.plot(kind="barh")

# %% [markdown]
# We see that a small `C` will shrink the weights values toward zero. It means
# that a small `C` provides a more regularized model. Thus, `C` is the inverse
# of the `alpha` coefficient in the `Ridge` model.
#
# Besides, with a strong penalty (i.e. small `C` value), the weight of the
# feature "Culmen Depth (mm)" is almost zero. It explains why the decision
# separation in the plot is almost perpendicular to the "Culmen Length (mm)"
# feature.