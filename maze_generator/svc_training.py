import random

from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC


def start_training():
    # Load the iris dataset
    iris = load_iris()

    # Split the data into features and target variable
    X = iris.data
    y = iris.target

    # Split the data into training and testing sets - increasing the test_size increases the accuracy
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.45, random_state=31)

    # Create the model and set the kernel
    model = SVC(kernel='linear')

    # Train the model on the training data
    model.fit(X_train, y_train)

    return model, X_test, y_test

def get_random_test_object(X_test):
    # Get a random test object
    return X_test[random.randint(0, len(X_test)-1)]

def get_random_test_object_prediction(model, X_test, y_test):
    # Get a random test object
    test_object = get_random_test_object(X_test)
    # Predict the class of the test object
    prediction = model.predict(test_object.reshape(1, -1))[0]
    # Get the actual class of the test object
    actual = y_test[X_test.tolist().index(test_object.tolist())]
    return prediction == actual