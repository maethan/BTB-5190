# -*- coding: utf-8 -*-
"""CIS 519 Project Part 2

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1b_QD-NCn8ar701dCNckUEb3qBATcIJmD

#**CIS 5190 Final Project**

By: Ethan Ma, Eric Wang, Chung Un Lee (Richard)

# Sports Betting with ML
### Contribution 2:
In this second contribution, we will focus on adding in line data to our previously created datasets as well as modifying the objective to consider this new line data.

## Installations, Imports, and Set-Up:
"""

!pip install pandasql

import csv
import pandas as pd
import numpy as np
import datetime as dt
import geopy.distance as gp
import matplotlib.image as mpimg
import plotly.express as px
import pandasql as ps #SQL on Pandas Dataframe
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

"""Mount to Drive (need to sign-in to Google Account)

### Datasets

[Link to Drive](https://drive.google.com/drive/folders/1PdNkjqxJQytu9w2NpsDEIv6e0gmn1ZaZ?usp=sharing)

To run:
1: Download 23_players_reg_pergame, 23_win_loss_data, 23_players_reg_pergame as .csv files to your local Google Drive
"""

# Mount to google drive
from google.colab import drive
drive.mount('/content/drive')

"""## Data Import, Cleaning, and Processing

Load the dataset using Pandas.
Please download all .csv files found in the 'Google Colab Data' folder of this drive:
https://drive.google.com/drive/folders/1PdNkjqxJQytu9w2NpsDEIv6e0gmn1ZaZ?usp=sharing
"""

# Initialize news_df using our downloaded csv
combined_df = pd.read_csv('/content/drive/MyDrive/combinedData.csv')
combined_team_df = pd.read_csv('/content/drive/MyDrive/allCombined.csv')
line_df = pd.read_csv('/content/drive/MyDrive/ROTOWIRE_data.csv')

# Show the first 10 rows of news_df
combined_df.head(10)

combined_team_df

line_df.head(10)

"""Drop null values, any cleaning here"""

# TODO

"""# Cleaning Data and Creating Datasets"""

final_df = combined_team_df.drop(columns=['Unnamed: 0', 'home_team', 'away_team', 'season', 'home_score', 'away_score', 'tipoff'])
# final_df = final_df[['home_line', 'label']]
final_df

matching_rows = ((final_df['home_line'] < 0) & (final_df['label'] == 1)) | \
           ((final_df['home_line'] > 0) & (final_df['label'] == 0))
# Calculate the percentage of matching rows
matching_percentage = (matching_rows.sum() / len(final_df)) * 100
print(f"Rate that the home_line is correct: {matching_percentage}")

"""# Data Visualization"""

for col in final_df.columns:
  plt.figure(figsize = (10, 6))
  sns.histplot(final_df[col], kde=True)
  plt.title(f'Distribution of {col}')
  plt.xlabel(col)
  plt.ylabel('Frequency')
  plt.show()

"""# Creating Test/Training Datasets

First, we use sklearn's ```train_test_split``` to split from the ```cleaned_news_df``` into training and testing sets.
"""

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# Create features from all except label
features = final_df.drop(columns='label')

# Extract target from the label
target = final_df['label']

# Set seed to 42, then perform the train test split
seed = 42
X_train, X_test, y_train, y_test = train_test_split(features, target, random_state = seed, test_size = 0.2)

"""## Logistic Regression Model (sklearn)

###Section 3.3.1 The Base Model

WRITE DESCRIPTION HERE
"""

# Import our logistic regression module from sklearn
from sklearn.linear_model import LogisticRegression

# Set seed to 42, then initialize and fit our model
seed = 42
logR = LogisticRegression(max_iter=30000, penalty='l2')

logR.fit(X_train, y_train)

from sklearn.metrics import accuracy_score

# With our newly fitted model, predict on both training and testing data
y_pred = logR.predict(X_test)
y_pred_train = logR.predict(X_train)

lr_test_accuracy = accuracy_score(y_pred, y_test)
lr_train_accuracy = accuracy_score(y_pred_train, y_train)
print("Accuracy of train Logistic Classifier: %.1f%%"% (lr_train_accuracy*100))
print("Accuracy of test Logistic Classifier: %.1f%%"% (lr_test_accuracy*100))

logR.predict_proba(X_train)

"""### Analysis of Feature Importances"""

from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier


pca = PCA(n_components=len(features.columns))
X_pca = pca.fit_transform(features)

rf_pca = RandomForestClassifier(n_estimators=100,
                                max_depth=6,
                                random_state=seed,
                                class_weight='balanced')
rf_pca.fit(X_pca, target)

importances = rf_pca.feature_importances_

sorted_indices = np.argsort(importances)[::-1]

top_features_indices = sorted_indices[:10]
top_features = features.columns[top_features_indices]

print("Top Features by Importance:")
for feature, importance in zip(top_features, importances[top_features_indices]):
    print(f"{feature}: {importance:.4f}")

import matplotlib.pyplot as plt


component_values = []
test_accuracies = []

for n_components in range(1, 18):
    pca = PCA(n_components=n_components)
    X_train_pca = pca.fit_transform(X_train)
    X_test_pca = pca.transform(X_test)

    seed = 42
    log_pca = LogisticRegression(max_iter=10000)
    log_pca.fit(X_train_pca, y_train)

    y_pred_pca = log_pca.predict(X_test_pca)

    test_accuracy_pca = accuracy_score(y_test, y_pred_pca)

    component_values.append(n_components)
    test_accuracies.append(test_accuracy_pca)

plt.figure(figsize=(10, 6))
plt.plot(component_values, test_accuracies, marker='o')
plt.title('Logistic Regression Accuracy vs. Number of PCA Components')
plt.xlabel('Number of Components')
plt.ylabel('Test Accuracy')
plt.xticks(component_values)
plt.grid(True)
plt.show()

"""## Random Forest Classifier Model

ADD DESCRIPTION
"""

# Import all modules for random forest classifer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

# Setting seed to 42, initialize our Random Forest Classifier
seed = 42
rf = RandomForestClassifier(n_estimators=200,
                            max_depth=5,
                            random_state=seed)

# Fit the classifier on our dataset
rf.fit(X_train.values, y_train.values)

# Find accuracies for both training and test data
y_pred = rf.predict(X_test.values)
y_pred_train = rf.predict(X_train.values)

train_accuracy = accuracy_score(y_train, y_pred_train)
test_accuracy = accuracy_score(y_pred, y_test)

print("Training Accuracy of Random Forest Classifier: %.1f%%"% (train_accuracy*100))
print("Testing Accuracy of Random Forest Classifier: %.1f%%"% (test_accuracy*100))

rf.predict_proba(X_train)

"""# Modifying Objective

We want to modify our objective in order to penalize predictions that match the sports book.

To our (binary) cross entropy loss, we will add the following penalty with hyperparameter c:

$c[max(0, p_o+p_c-1)+max(0,1-p_o-p_c)]$

$p_o\in [0,1]$ is the our output prediction, and $p_c\in\{0,1\}$ is the sports book prediction.

We are essentially penalizing everytime they match, similar to how the custom objective and loss was computed in homework 5, translated into something that is differentiable.

Thus the overall loss is:

$L=\frac{1}{n}\sum_{i=1}^n[y_ilog(p_o)+(1-y_i)log(1-p_o)]+\frac{c}{n}\sum_{i=1}^n[max(0, p_o+p_c-1)+max(0,1-p_o-p_c)]$

Where $p_o=\sigma(\theta^Tx_i)$

Since we want to apply this in gradient descent, the gradient of the inner penalty term is:

$[p_o(1-p_o)x_i]*a-[p_o(1-p_o)x_i]*b$

Where $a$ is an indicator if $p_o+p_c+1\geq 0$ and b is an indicator if $1-p_o-p_c\geq 0$

Custom logistic regression implementation referenced from:
https://medium.com/@koushikkushal95/logistic-regression-from-scratch-dfb8527a4226
"""

class CustomLogisticRegression:
    def __init__(self, learning_rate=0.001, n_iters=1000):
        self.lr = learning_rate
        self.n_iters = n_iters
        self.weights = None
        self.bias = None
        self.losses = []
        self.c = 0.05

    #Sigmoid method
    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def compute_loss(self, y_true, y_pred):
        # binary cross entropy
        epsilon = 1e-9
        y1 = y_true * np.log(y_pred + epsilon)
        y2 = (1-y_true) * np.log(1 - y_pred + epsilon)
        return -np.mean(y1 + y2)

    def sep_loss(self, y_true, y_pred, line):
        diff = (y_true - y_pred) ** 2
        penalty = self.c * (y_pred - self._sigmoid(line))
        n = y_true.shape[0]
        return 1 / n * (diff - penalty)

    def feed_forward(self,X):
        z = np.dot(X, self.weights) + self.bias
        A = self._sigmoid(z)
        return A

    def penalty(self, X, pred):
      sig_grad = pred * (1 - pred)
      p_cs = X[:,0]
      pena = 0
      for i, sig_g in enumerate(sig_grad):
          # print(f"X[i]: {X}")
          # print(f"i: {i}")
          # probability from sports book
          sig_g *= X[i]
          p_c = 1 if p_cs[i] <= 0 else 0
          p_i = pred[i]

          # and
          if p_c + p_i - 1 >= 0:
              pena += sig_g

          # or
          # not A and not B
          if 1 - p_c - p_i >= 0:
              pena -= sig_g


      return (self.c * pena / X.shape[0])

    def fit(self, X, y):
        n_samples, n_features = X.shape

        # init parameters
        self.weights = np.zeros(n_features)
        self.bias = 0

        # gradient descent
        for _ in range(self.n_iters):
            A = self.feed_forward(X)
            self.losses.append(self.compute_loss(y,A))
            dz = A - y # derivative of sigmoid and bce X.T*(A-y)
            # compute gradients
            penalty = self.penalty(X, A)

            dw = (1 / n_samples) * (np.dot(X.T, dz)) + penalty
            db = (1 / n_samples) * np.sum(dz)
            # update parameters
            self.weights -= self.lr * dw
            self.bias -= self.lr * db

    def predict(self, X):
        threshold = .5
        y_hat = np.dot(X, self.weights) + self.bias
        y_predicted = self._sigmoid(y_hat)
        y_predicted_cls = [1 if i > threshold else 0 for i in y_predicted]

        return np.array(y_predicted_cls)

    def predict_proba(self, X):
      threshold = .5
      y_hat = np.dot(X, self.weights) + self.bias
      y_predicted = self._sigmoid(y_hat)

      return np.array(y_predicted)

print(f"train: {X_train}, values: {X_train.values}")
lr = CustomLogisticRegression()
lr.fit(X_train.values, y_train.values)

print(lr.predict_proba(X_train.values))
print(lr.predict(X_train.values))
# print(lr.losses)

y_pred_train = lr.predict(X_train.values)
y_pred = lr.predict(X_test.values)
train_accuracy = accuracy_score(y_train.values, y_pred_train)
test_accuracy = accuracy_score(y_pred, y_test.values)

print("Training Accuracy of Modified LR: %.1f%%"% (train_accuracy*100))
print("Testing Accuracy of Modified LR: %.1f%%"% (test_accuracy*100))

def create_adjusted_pred(row):
  return lr.predict(np.array(row.drop(columns=["label"])).reshape(-1, 1))

output_df = final_df

features = final_df.drop(columns=['label'])

# Create a new list to store the predictions
predictions = []

# Iterate through each row and apply rf.predict()
for index, row in features.iterrows():
    # Exclude the label column for prediction
    # print(row)
    prediction = lr.predict_proba(row.values)

    # Append the prediction to the list
    predictions.append(prediction)

# Add predictions as a new column to the original DataFrame
output_df['predictions'] = predictions
output_df = output_df[['label', 'home_line', 'predictions']].sort_values(by=['predictions'], ascending=False)

# sorted by prediction descending
output_df.head(20)

def count_differing(df):
    matching_rows = ((df['home_line'] < 0) & (df['label'] == 0) & (df['predictions'] <= 0.5)) | \
           ((df['home_line'] > 0) & (df['label'] == 1) & (df['predictions'] > 0.5))
    # matching_rows = ((df['home_line'] < 0) & (df['label'] == 0)) | \
    #        ((df['home_line'] > 0) & (df['label'] == 1))
    return matching_rows
first = output_df.head(200)

# Select the last 20 rows
last = output_df.tail(20)
# print(f"first: {first}, last: {last}")
print(count_differing(first).sum())
# print(count_differing(first).sum() + count_differing(last).sum())

from google.colab import files

output_df.to_csv('output.csv', encoding = 'utf-8-sig')
files.download('output.csv')

"""# Evaluation"""

def count_differing(df):
    matching_rows = ((df['home_line'] < 0) & (df['label'] == 0) & (df['predictions'] <= 0.5)) | \
           ((df['home_line'] > 0) & (df['label'] == 1) & (df['predictions'] > 0.5))
    # matching_rows = ((df['home_line'] < 0) & (df['label'] == 0)) | \
    #        ((df['home_line'] > 0) & (df['label'] == 1))
    return matching_rows

rates = [0, .001, 0.0015, 0.002, 0.003 , 0.005, 0.01, 0.0105, 0.011, 0.012, 0.013, .025 , 0.05, 0.07, 0.09, 0.095, .1, .2, .3, .5, 0.7, 1, 2, 4, 7, 10]
eval_magnitude = [10, 50, 100, 500, 1000]
different = []
differents = {}

for mag in eval_magnitude:
  differents[mag] = []


for c in rates:
    lr = CustomLogisticRegression()
    lr.c = c
    lr.fit(X_train.values, y_train.values)

    output_df = final_df
    features = final_df.drop(columns=['label'])

    # Create a new list to store the predictions
    predictions = []

    # Iterate through each row and apply rf.predict()
    for index, row in features.iterrows():
        # print(row)
        # Exclude the label column for prediction
        prediction = lr.predict_proba(row.values[:-1])

        # Append the prediction to the list
        predictions.append(prediction)

    # Add predictions as a new column to the original DataFrame
    output_df['predictions'] = predictions
    output_df = output_df[['label', 'home_line', 'predictions']].sort_values(by='predictions', ascending=False)

    for mag in eval_magnitude:
        # Select the first 20 rows
        first = output_df.head(mag)

        # Select the last 20 rows
        last = output_df.tail(200)
        # print(f"first: {first}, last: {last}")
        # different.append((c, count_differing(first).sum() + count_differing(last).sum()))
        differents[mag].append((c, count_differing(first).sum()))



# print(different)

for mag in eval_magnitude:
  different = differents[mag]
  print([row[1] for row in different])

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))  # Create one figure

for mag in eval_magnitude:
  different = differents[mag]
  diff_values = [row[1] for row in different]
  plt.plot(rates, diff_values, marker='o', label=f'Eval Magnitude {mag}')  # Add label for legend

plt.xlabel('Rates')
plt.ylabel('Number of Correct Differing Predictions')
plt.title('Number of Correct Differing Predictions as a Function of Rates for Different Eval Magnitudes')
plt.grid(True)
plt.legend()  # Add legend to the plot
plt.show()

plt.figure(figsize=(10, 6))  # Create one figure

for mag in eval_magnitude:
  different = differents[mag]
  diff_values = [row[1] / mag for row in different]
  plt.plot(rates, diff_values, marker='o', label=f'Eval Magnitude {mag}')  # Add label for legend

plt.xlabel('Rates')
plt.ylabel('Ratio of Correct Differing Predictions to Total Evaluated Predictions')
plt.title('Number of Correct Differing Predictions as a Function of Rates for Different Eval Magnitudes')
plt.grid(True)
plt.legend()  # Add legend to the plot
plt.show()

def count_differing(df):
    matching_rows = ((df['home_line'] < 0) & (df['label'] == 0) & (df['predictions'] <= 0.5)) | \
           ((df['home_line'] > 0) & (df['label'] == 1) & (df['predictions'] > 0.5))
    # matching_rows = ((df['home_line'] < 0) & (df['label'] == 0)) | \
    #        ((df['home_line'] > 0) & (df['label'] == 1))
    return matching_rows

rates = [0, .001, 0.0015, 0.002, 0.003 , 0.005, 0.01, 0.0105, 0.011, 0.012, 0.013, .025 , 0.05, 0.07, 0.09, 0.095, .1, .2, .3, .5, 0.7, 1, 2, 4, 7, 10]
eval_magnitude = [10, 50, 100, 200, len(X_test)]
different = []
differents = {}

for mag in eval_magnitude:
  differents[mag] = []


for c in rates:
    lr = CustomLogisticRegression()
    lr.c = c
    lr.fit(X_train.values, y_train.values)

    output_df = X_test
    output_df['label'] = y_test
    features = output_df.drop(columns=['label'])

    # Create a new list to store the predictions
    predictions = []

    # Iterate through each row and apply rf.predict()
    for index, row in features.iterrows():
        # print(row)
        # Exclude the label column for prediction
        if (len(row) == 19):
          prediction = lr.predict_proba(row.values)
        else:
          prediction = lr.predict_proba(row.values[:-1])

        # Append the prediction to the list
        predictions.append(prediction)

    # Add predictions as a new column to the original DataFrame
    output_df['predictions'] = predictions
    output_df = output_df[['label', 'home_line', 'predictions']].sort_values(by='predictions', ascending=False)

    for mag in eval_magnitude:
        # Select the first 20 rows
        first = output_df.head(mag)

        # Select the last 20 rows
        last = output_df.tail(200)
        # print(f"first: {first}, last: {last}")
        # different.append((c, count_differing(first).sum() + count_differing(last).sum()))
        differents[mag].append((c, count_differing(first).sum()))



# print(different)

plt.figure(figsize=(10, 6))  # Create one figure

for mag in eval_magnitude:
  different = differents[mag]
  diff_values = [row[1]  for row in different]
  plt.plot(rates, diff_values, marker='o', label=f'Eval Magnitude {mag}')  # Add label for legend

plt.xlabel('Rates')
plt.ylabel('Number of Correct Differing Predictions')
plt.title('(Test Data) Number of Correct Differing Predictions as a Function of Rates for Different Eval Magnitudes')
plt.grid(True)
plt.legend()  # Add legend to the plot
plt.show()

plt.figure(figsize=(10, 6))  # Create one figure

for mag in eval_magnitude:
  different = differents[mag]
  diff_values = [row[1] / mag for row in different]
  plt.plot(rates, diff_values, marker='o', label=f'Eval Magnitude {mag}')  # Add label for legend

plt.xlabel('Rates')
plt.ylabel('Ratio of Correct Differing Predictions to Total Evaluated Predictions')
plt.title('(Test Data) Number of Correct Differing Predictions as a Function of Rates for Different Eval Magnitudes')
plt.grid(True)
plt.legend()  # Add legend to the plot
plt.show()