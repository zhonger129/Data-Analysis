#!/usr/bin/python

import sys
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data, test_classifier
from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest
from sklearn.model_selection import GridSearchCV,StratifiedShuffleSplit
from sklearn.tree import DecisionTreeClassifier

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ['poi','salary'] # You will need to use more features

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)


# dict to dataframe
df = pd.DataFrame.from_dict(data_dict, orient='index')

df.replace('NaN', np.nan, inplace = True)
####--------------------------------------------------#########
#import pprint
#pprint.pprint(data_dict)
####--------------------------------------------------#########


### Task 2: Remove outliersi
df.drop('TOTAL', inplace = True)

### Task 3: Create new feature(s)
features_list = [
                 'poi',
                 'salary',
                 'deferral_payments',
                 'total_payments',
                 'loan_advances',
                 'bonus',
                 'bonus_salary_ratio',
                 'restricted_stock_deferred',
                 'deferred_income',
                 'total_stock_value',
                 'expenses',
                 'exercised_stock_options',
                 'other',
                 'long_term_incentive',
                 'restricted_stock',
                 'director_fees',
                 'to_messages',
                 'from_poi_to_this_person',
                 'from_messages',
                 'from_this_person_to_poi',
                 'shared_receipt_with_poi'
]

df["bonus_salary_ratio"] = df["bonus"].astype(float) / df["salary"].astype(float)
df["bonus_salary_ratio"].replace(np.nan, 0, inplace = True)

### Store to my_dataset for easy export below.
#my_dataset = df.to_dict('index')

filled_df = df.fillna(value='NaN') # featureFormat expects 'NaN' strings
data_dict = filled_df.to_dict(orient='index')

### Store to my_dataset for easy export below.
my_dataset = data_dict

data = featureFormat(my_dataset,features_list)
labels, features = targetFeatureSplit(data)

#features_train, features_test, labels_train, labels_test = \
#    train_test_split(features, labels, test_size=0.3, random_state=42)

### Cross-validation
sss = StratifiedShuffleSplit(n_splits=10, test_size=0.2, random_state=42)
### Extract features and labels from dataset for local testing
#data = featureFormat(my_dataset, features_list, sort_keys = True)
#labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.
#from sklearn.naive_bayes import GaussianNB
#clf = GaussianNB()

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# Example starting point. Try investigating other evaluation techniques!

from sklearn import svm
estimators = [('scaler',StandardScaler()),
              ('feature_selection', SelectKBest()),
              ('reducer', PCA(random_state=42)),
              ('svm',svm.SVC())]
pipe = Pipeline(estimators)
param_grid = ([{'feature_selection__k':[10, 13, 15, 'all'],
                'reducer__n_components':[2, 4, 6, 8, 10],
                'svm__C': np.logspace(-2, 3, 6),
                'svm__gamma': np.logspace(-4, 1, 6),
                'svm__class_weight':['balanced', None],
                'svm__kernel': ['rbf', 'sigmoid']}])

grid_search = GridSearchCV(pipe, param_grid, scoring='precision', cv=sss)
grid_search.fit(features, labels)
#labels_predictions = grid_search.predict(features_test)

clf = grid_search.best_estimator_
print "\n", "Best parameters are: ", grid_search.best_params_, "\n"

test_classifier(clf, my_dataset, features_list)

# Print features selected and their scores
kbest = grid_search.best_estimator_.named_steps['feature_selection']

features_array = np.array(features_list)
features_array = np.delete(features_array, 0)
indices = np.argsort(kbest.scores_)[::-1]

feature_selected = []
feature_scores = []
for i in range(len(kbest.get_support(indices=True))):
    feature_selected.append(features_array[indices[i]])
    feature_scores.append(kbest.scores_[indices[i]])
    print "feature no.{} is {},  score is [{}]".format(i+1, features_array[indices[i]],kbest.scores_[indices[i]])

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)
