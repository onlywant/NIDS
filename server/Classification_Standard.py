# import warnings filter
from warnings import simplefilter

# ignore all future warnings
simplefilter(action='ignore', category=FutureWarning)
import numpy as np
import pandas as pd
from time import sleep
from queue import Queue
import multiprocessing
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from logging import basicConfig,INFO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Feature_DB import Fea_test, Fea_train, Extra_train
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score

# from gensim.test.test_doc2vec import ConcatenatedDoc2Vec

basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=INFO)


class Classification:
    '''
        1. init -> get_category_from_feature
        2. init ->  -train_dbow  ->test
                    -train_dm
    '''

    def __init__(self):
        self.sizeDbow = 50
        self.sizeDm = 16
        self.circle = 5
        self.epoch = 4
        self.rate = 0.5
        self.derate = 0.0025
        self.success = None
        self.addNew = False
        self.docTrain_Tagged = None
        self.docTest_Tagged = None
        self.vec_token_dbow = None
        self.mid_model_dbow = None
        self.modelDbow = None
        self.list_flag = ['normal', 'dos', 'probe']
        # self.list_flag = ['normal.', 'err.']
        ############加载模型

        self.load_model_dbow()
        print(self.modelDbow)
        self.set_token_dbow(self.modelDbow)

        print('classification init finished')

    # 从特征获得分类
    def get_category_from_feature(self, fea):
        # TODO
        # 1. fea to taggled sentence
        # 2. get vec of sentence
        # 3.
        sents = fea
        for i in range(len(sents)):
            sents[i] = str(sents[i])

        vec = self.modelDbow.infer_vector(sents, steps=20)
        cur = -1
        maxdis = -1
        for i in range(3):
            dis = float(
                np.dot(vec, self.vec_token_dbow[i]) / (np.linalg.norm(vec) * np.linalg.norm(self.vec_token_dbow[i])))
            if maxdis < dis:
                maxdis = dis
                cur = i
        return self.list_flag[cur]

    # 设置训练参数
    def set_para(self, sizeDbow, circle, epoch, rate, derate, addNew):
        self.sizeDbow = sizeDbow
        self.circle = circle
        self.epoch = epoch
        self.rate = rate
        self.derate = derate
        self.addNew = addNew

    # 通过模型设置标签向量
    def set_token_dbow(self, model):
        self.vec_token_dbow = []
        for i in range(len(self.list_flag)):
            self.vec_token_dbow.append(model.docvecs[self.list_flag[i]])

    def set_token_dm(self):
        self.vec_token_dm = []
        for i in range(len(self.list_flag)):
            self.vec_token_dm.append(self.modelDm.docvecs[self.list_flag[i]])

    # 加载模型
    def load_model_dbow(self):
        self.modelDbow = Doc2Vec.load(
            './model/docmodel__dbow__standard__cos_and_logis.model')

    def load_model_dm(self):
        self.modelDm = Doc2Vec.load(
            './model/docmodel__dm__standard__cos_and_logis.model')

    # 保存中间模型并重新加载
    def save_model_from_mid(self):
        self.modelDbow = Doc2Vec.load(
            './model/docmodel__mid__dbow__standard__cos_and_logis.model')
        self.modelDbow.save(
            './model/docmodel__dbow__standard__cos_and_logis.model')
        self.set_token_dbow(self.modelDbow)
        print('cover finish')


    '''      数据预处理        '''
    def data_preprocess(self):
        # csvDataTrain = pd.read_csv('./data/nsl-train.csv')  # 读取训练数据
        # arrCsvTrain = np.array(csvDataTrain)
        # csvDataTest = pd.read_csv('./data/nsl-test.csv')  # 读取测试数据
        # arrCsvTest = np.array(csvDataTest)
        # docTrain = arrCsvTrain[:, :-1]
        # tagTrain = arrCsvTrain[:, -1]
        # docTest = arrCsvTest[:, :-1]
        # tagTest = arrCsvTest[:, -1]
        # docTrain_Tagged = []
        # docTest_Tagged = []
        #
        # for i in range(len(docTrain)):
        #     docTrain_Tagged.append(
        #         TaggedDocument(' '.join(docTrain[i]).split(' '), [str(tagTrain[i])]))
        # for i in range(len(docTest)):
        #     docTest_Tagged.append(TaggedDocument(' '.join(docTest[i]).split(' '), [str(tagTest[i])]))
        # self.docTrain_Tagged = docTrain_Tagged
        # self.docTest_Tagged = docTest_Tagged
        engine = create_engine('sqlite:///./data/Fea.db')
        DBSession = sessionmaker(bind=engine)
        # 创建session对象:
        session = DBSession()
        train_data = session.query(Fea_train).all()
        test_data = session.query(Fea_test).all()
        extra_data = session.query(Extra_train).all()
        session.close()
        docTrain_Tagged = []
        docTest_Tagged = []

        for i in range(len(train_data)):
            docTrain_Tagged.append(
                TaggedDocument(train_data[i].feature.split(' '), [train_data[i].classification]))
        if self.addNew:
            for i in range(len(extra_data)):
                docTrain_Tagged.append(
                    TaggedDocument(train_data[i].feature.split(' '), [train_data[i].classification]))
        for i in range(len(test_data)):
            docTest_Tagged.append(
                TaggedDocument(test_data[i].feature.split(' '), [test_data[i].classification]))
        print(docTest_Tagged[0])

        self.docTrain_Tagged = docTrain_Tagged
        self.docTest_Tagged = docTest_Tagged

    '''      获得向量函数        '''
    def get_vector_for_learning(self, model, tagged_docs):
        sents = tagged_docs
        targets, regressors = zip(*[(doc.tags[0], model.infer_vector(doc.words, steps=20)) for doc in sents])
        return targets, regressors

    '''      余弦相似度预测函数     '''
    def calculate_cos_sim(self, X_test, y_test, buffer_p=None):
        y_pred_cos = []
        for i in range(len(X_test)):
            maxdis = -1
            cur = -1
            for j in range(len(self.list_flag)):
                dis = float(np.dot(X_test[i], self.vec_token_dbow[j]) / (
                            np.linalg.norm(X_test[i]) * np.linalg.norm(self.vec_token_dbow[j])))
                if maxdis < dis:
                    maxdis = dis
                    cur = j
            y_pred_cos.append(self.list_flag[cur])

        if buffer_p is not None:
            buffer_p.put(90.0)

        # with open('C:\\Users\\ThinkPad\\Desktop\\bishe\\test\\2.txt', 'w', newline='') as file:
        #     for i in range(len(y_pred_cos)):
        #         file.write(str(y_pred_cos[i]))
        # with open('C:\\Users\\ThinkPad\\Desktop\\bishe\\test\\3.txt', 'w', newline='') as file:
        #     for i in range(len(y_test)):
        #         file.write(str(y_test[i]))
        # f = open('./test.txt', 'w')
        num_acc = 0
        num_attack = 0
        num_attack_p = 0
        num_normal = 0
        num_p_attack = 0
        for i in range(len(y_pred_cos)):
            # f.write(y_pred_cos[i] + '\n')
            # print(y_test[i],y_pred_cos[i])
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

        # f.close()

        if buffer_p is not None:
            buffer_p.put(100.0)
        sleep(1)
        if buffer_p is not None:
            buffer_p.put(None)
            buffer_p.put("余弦相似度正确率为："+str(num_acc / len(y_pred_cos)) +
                         "  检测率（DR）："+str( num_attack_p / num_attack) +
                         "  误报率（DR）："+str( num_p_attack / num_normal))

        # print("余弦相似度正确率为：{}".format(num_acc / len(y_pred_cos)) + \
        #                  "检测率（DR）：{}".format( num_attack_p / num_attack) + \
        #                  "误报率（DR）：{}".format( num_p_attack / num_normal))

    '''      logistics回归预测函数     '''
    def calculate_logist_sim(X_train, y_train, X_test, y_test):
        logreg = LogisticRegression(n_jobs=1, C=1e5)
        logreg.fit(X_train, y_train)
        y_pred_logis = logreg.predict(X_test)
        # with open('../model/test/4.txt', 'w', newline='') as file:
        #     for i in range(len(y_pred_logis)):
        #         file.write(str(y_pred_logis[i] + ' ' + str(y_test[i]) + '\n'))

        print('逻辑回归Testing accuracy :%s' % accuracy_score(y_test, y_pred_logis) + \
              '逻辑回归Testing F1 score: {}'.format(f1_score(y_test, y_pred_logis, average='weighted')))


    '''      训练并保存 dbow模型        '''
    def train_dbow(self, buffer_p=None):
        print('start dbow train')
        self.data_preprocess()
        if buffer_p is not None:
            buffer_p.put(1 / self.circle * 100 - 1)
        cores = multiprocessing.cpu_count()
        self.mid_model_dbow = Doc2Vec(dm=0, min_count=1, workers=cores, vector_size=self.sizeDbow)
        self.mid_model_dbow.build_vocab(self.docTrain_Tagged)
        for epoch in range(self.circle):
            self.mid_model_dbow.train(self.docTrain_Tagged, total_examples=len(self.docTrain_Tagged), epochs=self.epoch)
            self.mid_model_dbow.alpha -= self.derate
            self.mid_model_dbow.min_alpha = self.mid_model_dbow.alpha
            if buffer_p is not None:
                buffer_p.put(((epoch + 1) / self.circle) * 100)
        sleep(1)
        print("dbow train over")
        self.mid_model_dbow.save(
            './model/docmodel__mid__dbow__standard__cos_and_logis.model')
        self.test_model(self.mid_model_dbow, self.docTest_Tagged, buffer_p)

    '''      训练并保存 dm模型        '''
    def train_dm(self):
        print('start train dm')
        cores = multiprocessing.cpu_count()
        docmodel_dm = Doc2Vec(alpha=0.025, dm_mean=None, dm=1, min_count=1, window=2, vector_size=16,
                                            sample=1e-3, min_alpha=0.0001, epochs=10, negative=5, workers=4)
        docmodel_dm.build_vocab(self.docTrain_Tagged)
        docmodel_dm.train(self.docTrain_Tagged, total_examples=len(self.docTrain_Tagged), epochs=docmodel_dm.epochs)
        print("dm over")
        docmodel_dm.save('./model/docmodel__dm__standard__cos_and_logis.model')

    '''      加载dbow模型，获得向量，预测结果，显示结果  目前74        '''
    def test_model(self, model, docstest, buffer_p=None, docs=None):
        print('start test model')
        self.set_token_dbow(model)
        if buffer_p is not None:
            buffer_p.put(20.0)
        # y_train, X_train = self.get_vector_for_learning(model,docs)
        y_test, X_test = self.get_vector_for_learning(model, docstest)

        if buffer_p is not None:
            buffer_p.put(50.0)
        #  余弦相似度预测
        self.calculate_cos_sim(X_test, y_test, buffer_p)
        #  逻辑回归预测
        # y_train, X_train = self.get_vector_for_learning(model, docs)
        # self.calculate_logist_sim(X_train, y_train, X_test, y_test)

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
    c = Classification()
    q = Queue()
    c.train_dbow(q)

