# ===============LICENSE_START=======================================================
# Acumos Apache-2.0
# ===================================================================================
# Copyright (C) 2017-2018 AT&T Intellectual Property & Tech Mahindra. All rights reserved.
# ===================================================================================
# This Acumos software file is distributed by AT&T and Tech Mahindra
# under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============LICENSE_END=========================================================


import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn import tree
from sklearn.ensemble import VotingClassifier
from acumos.modeling import List
from acumos.session import AcumosSession
from acumos.modeling import Model


if __name__ == "__main":
    mydata = pd.read_csv("./dataset/creditcard.csv")
    X = np.array(mydata.iloc[:,2:31])
    y = np.array(mydata.iloc[:,-1])
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
    clf = tree.DecisionTreeClassifier()
    lr = LogisticRegression()
    svm = SVC()
    model = VotingClassifier(estimators=[('lr', lr), ('clf', clf), ('svm', svm)])
    model.fit(x_train, y_train)
    def fraud_predict(X: List[float])-> List[int]:
        '''
        :param X: a list of float
        :return: a list of int
        '''
        yhat = model.predict(np.array(X).reshape(1, -1))
        return yhat
    acumos_model = Model(classify=fraud_predict)
    session = AcumosSession()
    session.dump(model,'fraud_detection','.')
