import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

def spamChecker(text):
    #reading data/emails from file
    file = pd.read_csv('spamham.csv')
    df = pd.DataFrame(file)
    x_train, x_test, y_train, y_test = train_test_split(
        df['v2'], df['v1'], random_state=1)
    cv = CountVectorizer()
    training_data = cv.fit_transform(x_train)
    testing_data = cv.transform([text])
    naive_bayes = MultinomialNB()
    naive_bayes.fit(training_data, y_train)
    predictions = naive_bayes.predict(testing_data)
    # print('The predictions was : ', predictions)
    return predictions
    # print('The accuracy is: ', format(accuracy_score(y_test, x_train)))

