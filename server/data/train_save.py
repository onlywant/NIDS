# import warnings filter
from warnings import simplefilter

# ignore all future warnings
simplefilter(action='ignore', category=FutureWarning)
import numpy as np
import pandas as pd
import multiprocessing
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

sizeDbow = 50
sizeDm = 30
list_flag = ['normal', 'dos', 'probe']

'''      数据预处理函数        '''

def PreProgressData():
    csvDataTrain = pd.read_csv('../data/nsl-train.csv')  # 读取训练数据
    arrCsvTrain = np.array(csvDataTrain)
    csvDataTest = pd.read_csv('../data/nsl-test.csv')  # 读取测试数据
    arrCsvTest = np.array(csvDataTest)
    docTrain = arrCsvTrain[:, :-1]
    tagTrain = arrCsvTrain[:, -1]
    docTest = arrCsvTest[:, :-1]
    tagTest = arrCsvTest[:, -1]
    docTrain_Tagged = []
    docTest_Tagged = []

    for i in range(len(docTrain)):
        docTrain_Tagged.append(TaggedDocument(' '.join(docTrain[i]).split(' '), [str(tagTrain[i])]))
    for i in range(len(docTest)):
        docTest_Tagged.append(TaggedDocument(' '.join(docTest[i]).split(' '), [str(tagTest[i])]))
    return docTrain_Tagged, docTest_Tagged

def VecForLearning(model, tagged_docs):
    sents = tagged_docs
    targets, regressors = zip(*[(doc.tags[0], model.infer_vector(doc.words, steps=20)) for doc in sents])
    return targets, regressors


'''      余弦相似度预测函数     '''


def CalCosSim(token, X_test, y_test):
    y_pred_cos = []
    for i in range(len(X_test)):
        maxdis = -1
        cur = -1
        for j in range(3):
            dis = float(np.dot(X_test[i], token[j]) / (np.linalg.norm(X_test[i]) * np.linalg.norm(token[j])))
            if maxdis < dis:
                maxdis = dis
                cur = j
        y_pred_cos.append(list_flag[cur])

    num_acc = 0
    num_attack = 0
    num_attack_p = 0
    num_normal = 0
    num_p_attack = 0
    with open('../model/test/3.txt', 'w', newline='') as file:
        for i in range(len(y_pred_cos)):
            if y_test[i] != 'normal':
                num_attack += 1
                if y_pred_cos[i] != 'normal':
                    num_attack_p += 1
            else:
                num_normal += 1
                if y_pred_cos[i] != 'normal':
                    num_p_attack += 1

            if y_test[i] == y_pred_cos[i]:
                num_acc += 1
            else:
                file.write(str(y_pred_cos[i] + ' ' + str(y_test[i]) + '\n'))

    print( "余弦相似度准确率为：{}\n".format(num_acc / len(y_pred_cos)) + \
                         "检测率（DR）：{}\n".format( num_attack_p / num_attack) + \
                         "误报率（DR）：{}".format( num_p_attack / num_normal))

'''      逻辑回归预测函数      '''


def calculate_logist_sim(X_train, y_train, X_test, y_test):
    logreg = LogisticRegression(n_jobs=1, C=1e5)
    logreg.fit(X_train, y_train)
    y_pred_logis = logreg.predict(X_test)
    with open('../model/test/4.txt', 'w', newline='') as file:
        for i in range(len(y_pred_logis)):
            file.write(str(y_pred_logis[i]+' '+str(y_test[i]) +'\n'))

    print('逻辑回归Testing accuracy :%s\n' % accuracy_score(y_test, y_pred_logis) + \
           '逻辑回归Testing F1 score: {}'.format(f1_score(y_test, y_pred_logis, average='weighted')))


'''      训练并保存 dbow模型        '''


def TrainDbow(docs):
    print('start dbow train')
    cores = multiprocessing.cpu_count()
    docmodel_dbow = Doc2Vec(dm=0, min_count=1, workers=cores, vector_size=20)
    # docmodel_dbow = gensim.models.Doc2Vec(alpha=0.025, dm_mean=None, dm=1, min_count=1, window=2, vector_size=16,
    #                                     sample=1e-3, min_alpha=0.0001, epochs=10, negative=5,workers=cores)
    docmodel_dbow.build_vocab(docs)
    for epoch in range(3):
        docmodel_dbow.train(docs, total_examples=len(docs), epochs=10)
        docmodel_dbow.alpha -= 0.0001
        docmodel_dbow.min_alpha = docmodel_dbow.alpha
    print("dbow train over")
    docmodel_dbow.save('../model/test/docmodel__dbow__standard__cos_and_logis.model')


'''      训练并保存 dm模型        '''


def train_dm(docs):
    print('start train dm')
    cores = multiprocessing.cpu_count()
    docmodel_dm =Doc2Vec(dm=1, vector_size=200,
                                         epochs=20, workers=cores)
    docmodel_dm.build_vocab(docs)
    docmodel_dm.train(docs, total_examples=len(docs), epochs=docmodel_dm.epochs)
    print("dm over")
    docmodel_dm.save('../model/test/docmodel__dm__standard__cos_and_logis.model')


'''      加载dbow模型，获得向量，预测结果，显示结果  目前74        '''


def TestModel(model, docs, docstest):
    print('start test model')
    y_train, X_train = VecForLearning(model, docs)
    y_test, X_test = VecForLearning(model, docstest)
    # 获得标签向量
    token = []
    for i in range(3):
        token.append(model.docvecs[list_flag[i]])
    #  余弦相似度预测
    CalCosSim(token, X_test, y_test)
    # calculate_logist_sim(X_train,y_train,X_test,y_test)
    #  逻辑回归预测
    # CalLogisSim(X_train, y_train, X_test, y_test)

'''      段向量加和求平均 和 标签向量结合 提高2%左右        '''

def CalTokenDoc(self, tags, X_train, size):
    num_doc = [0] * 5
    token_doc = np.zeros((5, size))
    for i in range(len(tags)):
        index = int(tags[i])
        token_doc[index] += X_train[i]
        num_doc[index] += 1
    for i in range(5):
        token_doc[i] = token_doc[i] / num_doc[i]
    return token_doc

'''      词向量加和求平均 和 标签向量结合 提高   左右        '''

def CalTokenWord(self, tags, model, size, docTrain):
    num_word = [0] * 5
    token_word = np.zeros((5, size))
    for i in range(len(tags)):
        index = int(tags[i])
        words = docTrain[i].split()
        for j in range(len(words)):
            token_word[index] += model.wv.get_vector(words[j])
            num_word[index] += 1
    for i in range(5):
        token_word[i] = token_word[i] / num_word[i]
    return token_word


if __name__ == '__main__':
    ############加载数据
    docTrain_Tagged, docTest_Tagged = PreProgressData()

    ############训练模型
    TrainDbow(docTrain_Tagged)
    # train_dm(docTrain_Tagged)
    ############加载模型
    modelDbow = Doc2Vec.load('../model/test/docmodel__dbow__standard__cos_and_logis.model')

    # modelDm = Doc2Vec.load('../model/test/docmodel__dm__standard__cos_and_logis.model')
    ############测试模型
    # TestModel(modelDbow, docTrain_Tagged, docTest_Tagged)
    # print('dm model test：', end='')
    TestModel(modelDbow, docTrain_Tagged, docTest_Tagged)
