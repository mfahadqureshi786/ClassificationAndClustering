import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import re
import os
import math
from pathlib import Path
Lexicons = []

trainingDocsPercentage=[70,70,70,70,70]
Sports = ['athletics', 'cricket', 'football', 'rugby', 'tennis']
def generateProcessedDocument(filePath):
    docObj = open(filePath, 'r')
    document = docObj.read()
    processedDocument = ''
    sentences = nltk.sent_tokenize(document)
    Lemmatizer = WordNetLemmatizer()
    for j in range(len(sentences)):
        processedSentence = re.sub('[^a-zA-Z]', ' ', sentences[j])
        processedSentence = processedSentence.lower()
        wordList = processedSentence.split()
        processedSentence = ''
        newSentence = ''
        for word in wordList:
            if word not in set(stopwords.words('english')):
                newSentence = newSentence + ' ' + Lemmatizer.lemmatize(word)
        sentences[j] = newSentence
    processedDocument = ''.join(sentences)
    return processedDocument
import queue as Q
def buildLexicon():
    global Sports
    classLexicons=[]
    for i in range(len(Sports)):
        classLexicons.append([])
    global trainingDocsPercentage
    trainingDocs=0
    testDocs=0
    print('Building Lexicons..')
    try:
        if not os.path.exists('Lexicons.txt') and not os.path.getsize('Lexicons.txt') > 0:
            raise FileNotFoundError
        print('Lexicons Already built.')
    except FileNotFoundError:
        print('catched exception in build Lexicons')
        fileNumber = '0'
        filePath = ''
        Lexicons = []
        postingList = []
        totalDocs = 0
        "totalProcessedDocs=[None]*totalDocs"
        "Document Preprocessing"

        for sport in Sports:
            DIR = 'bbcsport/' + sport
            filesInCurrent = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
            trainingDocs=int(filesInCurrent*trainingDocsPercentage[Sports.index(sport)]/100)
            q = Q.PriorityQueue()
            wordDictionary={}
            docsRead=0
            for i in range(1,filesInCurrent+1):
                if docsRead<=trainingDocs:
                    docsRead=docsRead+1
                    if i<9:
                        filePath = 'bbcsport/'+sport+'/00' + str(i) + '.txt'
                    if i>9 and i<99:
                        filePath = 'bbcsport/'+sport+'/0' + str(i) + '.txt'
                    if i>99:
                        filePath = 'bbcsport/'+sport+'/' + str(i) + '.txt'
                    print('Processing Document:'+str(i)+','+sport)
                    fileObj = open(filePath + '', 'r')
                    document = fileObj.read()
                    processedDocument = ''
                    sentences = nltk.sent_tokenize(document)
                    Lemmatizer = WordNetLemmatizer()
                    "Sentences Preprocessing"
                    for j in range(len(sentences)):
                        processedSentence = re.sub('[^a-zA-Z]', ' ', sentences[j])
                        processedSentence = processedSentence.lower()
                        wordList = processedSentence.split()
                        processedSentence = ''
                        newSentence = ''
                        for word in wordList:
                            if word not in set(stopwords.words('english')):
                                lemmatizedWord = Lemmatizer.lemmatize(word)
                                newSentence = newSentence + ' ' + lemmatizedWord
                                if len(lemmatizedWord) > 2:
                                    if lemmatizedWord not in wordDictionary:
                                        wordDictionary[lemmatizedWord] = 1
                                    else:
                                        wordDictionary[lemmatizedWord] = wordDictionary[lemmatizedWord] + 1
                                    if lemmatizedWord not in Lexicons:
                                        Lexicons.append(lemmatizedWord)
                                    ###

                                    ###
                        sentences[j] = newSentence
                    processedDocument = ''.join(sentences)
            for w in wordDictionary:
                if wordDictionary[w]>3:
                    q.put((-wordDictionary[w],w))
            while not q.empty():
                classLexicons[Sports.index(sport)].append(q.get()[1])
        ##Updating Total Lexicons
        Lexicons=[]
        for i in range(len(Sports)):
            for j in range(len(classLexicons[i])):
                if classLexicons[i][j] not in Lexicons:
                    presentInAll=True
                    for u in range(len(Sports)):
                        if classLexicons[i][j] in classLexicons[u]:
                            presentInAll=presentInAll and True
                        else:
                            presentInAll = presentInAll and False
                            break
                    if not presentInAll:
                        Lexicons.append(classLexicons[i][j])
            "Not storing processed Documents to save RAM"
            "Writing lexicons to file"
        Lexicons = list(dict.fromkeys(Lexicons))
        fileObj = open('Lexicons.txt', 'w')
        fileObj.write(str(len(Lexicons)))
        fileObj.write('\n')
        Lexicons.sort()
        for a in range(len(Lexicons)):
            fileObj.write(Lexicons[a])
            fileObj.write('\n')
        print('Finished! Lexicons.')
        return None

def createDocVector(docID,classType):
    try:
        fileObj=open("DocumentVectors/"+classType+'/'+docID+ ".txt", 'r')
        trainDocumentVector = []
        totalWords = int(fileObj.readline().rstrip('\n'))
        while (totalWords > 0):
            trainDocumentVector.append(fileObj.readline().rstrip('\n'))
            totalWords = totalWords - 1
        convDocVec=[]
        for i in range(len(trainDocumentVector)):
            if type(trainDocumentVector[i]) == str and trainDocumentVector[i].isdigit():
                convDocVec.append(int(trainDocumentVector[i]))
        return convDocVec
    except Exception:
        LexiconPath = Path("Lexicons.txt")
        if not LexiconPath.is_file():
            buildLexicon()
        LexiconObj = open("Lexicons.txt", 'r')
        Lexicons=[]
        totalLexicons = int(LexiconObj.readline().rstrip('\n'))
        while (totalLexicons > 0):
            Lexicons.append(LexiconObj.readline().rstrip('\n'))
            totalLexicons = totalLexicons - 1
        dir = os.path.join("DocumentVectors")
        if not os.path.exists(dir):
            os.mkdir(dir)
        dir = os.path.join('DocumentVectors' + '/' + classType)
        if not os.path.exists(dir):
            os.mkdir(dir)
        documentVectorPath = Path("DocumentVectors/" + classType + docID + ".txt")
        if documentVectorPath.is_file():
            return True
        else:
            filePath = 'bbcsport/' + classType + '/' + docID + '.txt'
            processedDocument=generateProcessedDocument(filePath)
            documentTokens = nltk.word_tokenize(processedDocument)
            documentVector = []
            for word in Lexicons:
                if word in documentTokens:
                    count = 0
                    current = -1
                    bool_should_run = True
                    while bool_should_run:
                        current = processedDocument.find(word, current + 1)
                        if current == -1:
                            bool_should_run = False
                        else:
                            count = count + 1
                    documentVector.append(count)
                else:
                    documentVector.append(0)
            fileObj = open("DocumentVectors/" + classType + '/' + docID + ".txt", 'w')
            #Writing as one by one
            fileObj.write(str(len(documentVector)))
            fileObj.write('\n')
            for a in range(len(documentVector)):
                fileObj.write(str(documentVector[a]))
                fileObj.write('\n')
            #fileObj.write(str(documentVector))
            fileObj.close()
            return documentVector
Correct=0
Total=0
K=3
def buildDocumentVectors():
    global trainingDocsPercentage
    global Total
    global Sports
    docsRead = 0
    for sport in Sports:
        DIR = 'bbcsport/' + sport
        filesInCurrent = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
        trainingDocs = int(filesInCurrent * trainingDocsPercentage[Sports.index(sport)]/100)
        docsRead=0
        for i in range(1, filesInCurrent + 1):
            if docsRead <= trainingDocs:
                if i < 9:
                    fileID = '00' + str(i)
                if i > 9 and i < 99:
                    fileID = '0' + str(i)
                if i > 99:
                    fileID = str(i)
                createDocVector(fileID,sport)
                docsRead=docsRead+1

testDocumentVector=[]
def createTestVector(filePath):
    global testDocumentVector
    Lexicons=[]
    try:
        LexiconObj = open("Lexicons.txt", 'r')
        totalLexicons = int(LexiconObj.readline().rstrip('\n'))
        while (totalLexicons > 0):
            Lexicons.append(LexiconObj.readline().rstrip('\n'))
            totalLexicons = totalLexicons - 1
    except Exception:
        LexiconPath = Path("Lexicons.txt")
        if not LexiconPath.is_file():
            buildLexicon()
            buildDocumentVectors()#Training
    processedDocument=generateProcessedDocument(filePath)
    documentTokens = nltk.word_tokenize(processedDocument)
    documentVector = []
    for word in Lexicons:
        if word in processedDocument:
            count = 0
            current = -1
            bool_should_run = True
            while bool_should_run:
                current = processedDocument.find(word, current + 1)
                if current == -1:
                    bool_should_run = False
                else:
                    count = count + 1

            documentVector.append(count)
        else:
            documentVector.append(0)
    otherWords=[]
    for word in documentTokens:
        if word not in Lexicons:
            if word not in otherWords:
                count = 0
                current = -1
                bool_should_run = True
                while bool_should_run:
                    current = processedDocument.find(word, current + 1)
                    if current == -1:
                        bool_should_run = False
                    else:
                        count = count + 1
        if word not in otherWords:
            documentVector.append(count)
            otherWords.append(word)
    testDocumentVector=documentVector
    return None
import ast
def calculateED(trainVec,testVec):
    result=0
    u=0
    trainVecNew=[]
    for i in range(len(trainVec)):
        if type(trainVec[i])==str and trainVec[i].isdigit():
            trainVecNew.append(int(trainVec[i]))
    if type(trainVec[0])==int:
        trainVecNew=trainVec

    for i in range(len(trainVecNew)):
        Vi = trainVecNew[i]
        Vj = testVec[i]
        if ( Vj - Vi ) > 0:
            result = result+math.pow(Vj - Vi,2)
        u=i+1
    for U in range(u,len(testVec)):
        Vi = 0
        Vj = testVec[u]
        if (Vj - Vi) > 0:
            result = result + math.pow(Vj - Vi, 2)
    if(result>0):
        result=math.sqrt(result)
    else:
        result=-1
    return result

def classify():
    global K
    global Sports
    EDSimilarity=[]
    docsRead=0
    for T in range(len(Sports)):
        EDSimilarity.append([])
        DIR = 'bbcsport/' + Sports[T]
        filesInCurrent = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
        trainingDocs = int(filesInCurrent * trainingDocsPercentage[T]/100)
        docsRead=0
        for i in range(1, filesInCurrent + 1):
            if docsRead <= trainingDocs:
                if i < 9:
                    filePath = 'DocumentVectors/' + Sports[T] + '/00' + str(i) + '.txt'
                    fileID = '00' + str(i)
                if i > 9 and i < 99:
                    filePath = 'DocumentVectors/' + Sports[T] + '/0' + str(i) + '.txt'
                    fileID = '0' + str(i)
                if i > 99:
                    filePath = 'DocumentVectors/' + Sports[T] + '/' + str(i) + '.txt'
                    fileID = str(i)
                docsRead=docsRead+1
                #trainDocObj=open(filePath,'r')

                #trainDocumentVector=[]
                trainDocumentVector=createDocVector(fileID,Sports[T])

                res=calculateED(trainDocumentVector,testDocumentVector)
                EDSimilarity[T].append(res)
                print('ED of category:'+Sports[T]+',document:'+str(i)+':'+str(res))
    min=9223372036854775807
    minScale=[]
    SimilarityScale=[]
    for sport in Sports:
        minScale.append([])
    for i in range(len(Sports)):
        for k in range(K):
            minScale[i].append(min)
    for A in range(K):
        for i in range(len(Sports)):
            for j in range(len(EDSimilarity[i])):
                if EDSimilarity[i][j]!=-1 and EDSimilarity[i][j]<=min and EDSimilarity[i][j]<=minScale[i][A] :
                    min=EDSimilarity[i][j]

            minScale[i][A]=min
    return minScale

def printSim(minScale,c,obj):
    text=''
    for i in range(len(minScale)):
        text = text+'Class='+str(i)+'\n'
        for k in range(len(minScale[i])):
            text=text+'d'+str(k)+' , T = '+str(minScale[i][k])+'\n'
    text=text+'\n'+'Classified to class:'+Sports[c]
    obj.result_classification.setText(text)

def calculateAccuracy():
    global  K
    global Total
    totalDocs = 0
    global Sports
    global testDocumentVector
    for sport in Sports:
        DIR = 'bbcsport/' + sport
        filesInCurrent = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
        trainingDocs = int(filesInCurrent * trainingDocsPercentage[Sports.index(sport)]/100)
        testDocs = filesInCurrent - trainingDocs
        docsRead = 0
        for i in range(trainingDocs+1, filesInCurrent + 1):
            if docsRead <= testDocs:
                if i < 9:
                    fileID = '00' + str(i)
                if i > 9 and i < 99:
                    fileID = '0' + str(i)
                if i > 99:
                    fileID = str(i)
                #createTestVector('bbcsport/'+ sport+'/'+fileID+'.txt')
                docsRead=docsRead+1
                testDocumentVector=createDocVector(fileID,sport)
                result = classify()
                classSum = []
                for i in range(len(Sports)):
                    classSum.append(-1)
                    for j in range(K):
                        classSum[i] = classSum[i] + result[i][j]
                minClassSum = classSum[0]
                classifiedClass = 0
                for i in range(len(classSum)):
                    if classSum[i] < minClassSum and classSum[i] != -1:
                        minClassSum = classSum[i]
                        classifiedClass = i
                isClassifiedRight(sport,Sports[classifiedClass])


def isClassifiedRight(actual,assigned):
    global Correct
    global Total
    if actual==assigned:
        Correct=Correct+1
    Total=Total+1
##############################Clustering#############################################
import random
oldClusters=[]
cluster_original=[]
def clustering():
    import random
    global K
    global oldClusters
    global cluster_original
    DocsPath=[]
    totalDocs = 0
    global Sports
    #Selecting K seeds
    kth=0
    KClusters=[]
    #Contains list of vector centroid
    KCentroids=[]
    #Contains list of cluster no. where each index of docsAssigned corresponds to DocsPath
    docsAssigned=[]
    cluster_original=[]
    t=0
    import os
    import pathlib
    for sport in Sports:
        DIR = 'bbcsport/' + sport
        filesInCurrent = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
        totalDocs = totalDocs + filesInCurrent
        cluster_original.append([])
        for i in range(1, filesInCurrent + 1):
            if i < 9:
                fileID = '00' + str(i)
            if i > 9 and i < 99:
                fileID = '0' + str(i)
            if i > 99:
                fileID = str(i)
            filePath='bbcsport/' + sport+'/'+fileID+'.txt'
            print(filePath)
            DocsPath.append(filePath)
            docsAssigned.append(-1)
            cluster_original[Sports.index(sport)].append(t)
            t=t+1

    from datetime import datetime
    random.seed(datetime.now())

    for i in range(K):
        kth = random.randint(0, len(DocsPath))
        while kth in KClusters:
            kth=random.randint(0,len(DocsPath))
        KClusters.append(kth)



    #First cluster centroid assigning
    #check if doc is present otherwise create its doc vector
    clusters = []
    for i in range(K):
        clusters.append([])
        cluster_original[i]=set(cluster_original[i])
        ID=DocsPath[KClusters[i]].split('/')[-1][:-4]
        classType=DocsPath[KClusters[i]].split('/')[-2]
        KCentroids.append(createDocVector(ID,classType))
    #Assigning labels to docs
    iterationsRan=0
    centerChanged=True
    oldClusters=[]
    while centerChanged:#Setting stopping criteria
        centerChanged=False
        iterationsRan=iterationsRan+1
        #Assigning docs to Cluster
        for i in range(len(DocsPath)):
            assignedLabel = 0
            minDistance = 9223372036854775807
            for j in range(K):
                ID = DocsPath[i].split('/')[-1][:-4]
                classType = DocsPath[i].split('/')[-2]
                tVec = createDocVector(ID, classType)
                if len(KCentroids[j])>0:
                    dist = calculateED(tVec, KCentroids[j])
                if dist < minDistance and dist!=-1:
                    minDistance = dist
                    assignedLabel = j
            docsAssigned[i] = assignedLabel
            clusters[assignedLabel].append(i)
        # Recomputation of centroid

        for a in range(K):
            centeroid = [0]*len(KCentroids[0])
            for i in range(len(clusters[a])):
                docVec=createDocVector(DocsPath[clusters[a][i]].split('/')[-1][:-4],DocsPath[clusters[a][i]].split('/')[-2])
                for b in range(len(docVec)):
                    centeroid[b] = centeroid[b] + docVec[b]
            for u in range(len(centeroid)):
                if len(centeroid) > 0 and len(clusters[a])>0:
                    centeroid[u] = centeroid[u] / len(clusters[a])
            if centeroid!=KCentroids[a]:
                centerChanged=True
                KCentroids[a] = centeroid
            print('Centeroid calculated')
        oldClusters = clusters
        clusters = []
        for t in range(len(oldClusters)):
            clusters.append([])

    print('Clustering Ends')
    return [oldClusters,KCentroids]
def printClusters():
    result=clustering()
    clusters=result[0]
    kCenters=result[1]
    text=""
    for i in range(len(clusters)):
        text=text+'Cluster '+str(i)+'\n'
        for a in range(len(clusters[i])):
            text=text+"Document "+str(clusters[i][a])+'\n'
        #text=text+'Centroid:'+'('+','.join(map(str,kCenters[i]))+')'+'\n\n'
    return text

def calculate_purity():
    global oldClusters
    global cluster_original
    result=[0]*K
    total=0
    foundMaxIndex=0
    purity=0
    for i in range(K):
        oldClusters[i]=set(oldClusters[i])
        total=total+len(cluster_original[i])
    for i in range(K):
        for j in range(K):
            ans=len(oldClusters[i] and cluster_original[j])
            if result[i]<ans:
                result[i]=ans
                foundMaxIndex=j
        cluster_original[j]={}
    for i in range(K):
        purity=purity+result[i]
    if total>0:
        purity=purity*(1/total)
    return purity
#Now we need K max intersections

#######################################GUI Begins##############################################3
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(450, 587)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(200, 200, 200))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(200, 200, 200))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(200, 200, 200))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(200, 200, 200))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        MainWindow.setPalette(palette)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.button_train = QtWidgets.QPushButton(self.centralwidget)
        self.button_train.setGeometry(QtCore.QRect(230, 320, 211, 51))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.button_train.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.button_train.setFont(font)
        self.button_train.setObjectName("button_train")
        self.class_1_percentage = QtWidgets.QTextEdit(self.centralwidget)
        self.class_1_percentage.setGeometry(QtCore.QRect(130, 80, 81, 31))
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        self.class_1_percentage.setFont(font)
        self.class_1_percentage.setObjectName("class_1_percentage")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 40, 81, 21))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.label_2.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(20, 80, 81, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.label_3.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(20, 130, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.label_4.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.class_2_percentage = QtWidgets.QTextEdit(self.centralwidget)
        self.class_2_percentage.setGeometry(QtCore.QRect(130, 130, 81, 31))
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        self.class_2_percentage.setFont(font)
        self.class_2_percentage.setObjectName("class_2_percentage")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(20, 180, 71, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.label_5.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(20, 230, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.label_6.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(20, 280, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.label_7.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.class_4_percentage = QtWidgets.QTextEdit(self.centralwidget)
        self.class_4_percentage.setGeometry(QtCore.QRect(130, 230, 81, 31))
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        self.class_4_percentage.setFont(font)
        self.class_4_percentage.setObjectName("class_4_percentage")
        self.class_5_percentage = QtWidgets.QTextEdit(self.centralwidget)
        self.class_5_percentage.setGeometry(QtCore.QRect(130, 280, 81, 31))
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        self.class_5_percentage.setFont(font)
        self.class_5_percentage.setObjectName("class_5_percentage")
        self.class_3_percentage = QtWidgets.QTextEdit(self.centralwidget)
        self.class_3_percentage.setGeometry(QtCore.QRect(130, 180, 81, 31))
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        self.class_3_percentage.setFont(font)
        self.class_3_percentage.setObjectName("class_3_percentage")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(180, 0, 131, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.label_8.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(120, 40, 111, 21))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.label_9.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.button_classify = QtWidgets.QPushButton(self.centralwidget)
        self.button_classify.setGeometry(QtCore.QRect(230, 80, 101, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.button_classify.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.button_classify.setFont(font)
        self.button_classify.setObjectName("button_classify")
        self.result_classification = QtWidgets.QTextEdit(self.centralwidget)
        self.result_classification.setGeometry(QtCore.QRect(230, 130, 211, 181))
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        self.result_classification.setFont(font)
        self.result_classification.setObjectName("result_classification")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(10, 370, 101, 21))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.label_10.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.result_clustering = QtWidgets.QTextEdit(self.centralwidget)
        self.result_clustering.setGeometry(QtCore.QRect(230, 390, 211, 151))
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.result_clustering.setFont(font)
        self.result_clustering.setObjectName("result_clustering")
        self.button_cluster = QtWidgets.QPushButton(self.centralwidget)
        self.button_cluster.setGeometry(QtCore.QRect(120, 480, 101, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.button_cluster.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.button_cluster.setFont(font)
        self.button_cluster.setObjectName("button_cluster")
        self.button_classification_accuracy = QtWidgets.QPushButton(self.centralwidget)
        self.button_classification_accuracy.setGeometry(QtCore.QRect(340, 80, 101, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.button_classification_accuracy.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.button_classification_accuracy.setFont(font)
        self.button_classification_accuracy.setObjectName("button_classification_accuracy")
        self.clustering_k = QtWidgets.QTextEdit(self.centralwidget)
        self.clustering_k.setGeometry(QtCore.QRect(80, 420, 81, 31))
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        self.clustering_k.setFont(font)
        self.clustering_k.setObjectName("clustering_k")
        self.button_cluster_accuracy = QtWidgets.QPushButton(self.centralwidget)
        self.button_cluster_accuracy.setGeometry(QtCore.QRect(10, 480, 101, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.button_cluster_accuracy.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.button_cluster_accuracy.setFont(font)
        self.button_cluster_accuracy.setObjectName("button_cluster_accuracy")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(10, 420, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.label_11.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.classification_k = QtWidgets.QTextEdit(self.centralwidget)
        self.classification_k.setGeometry(QtCore.QRect(130, 330, 81, 31))
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        self.classification_k.setFont(font)
        self.classification_k.setObjectName("classification_k")
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(20, 330, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.label_12.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 450, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Classification-Clustering"))
        self.button_train.setText(_translate("MainWindow", "Train"))
        self.class_1_percentage.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Sans Serif\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.class_1_percentage.setPlaceholderText(_translate("MainWindow", "70"))
        self.label_2.setText(_translate("MainWindow", "Classes"))
        self.label_3.setText(_translate("MainWindow", "Athletics"))
        self.label_4.setText(_translate("MainWindow", "Cricket"))
        self.class_2_percentage.setPlaceholderText(_translate("MainWindow", "70"))
        self.label_5.setText(_translate("MainWindow", "Football"))
        self.label_6.setText(_translate("MainWindow", "Rugby"))
        self.label_7.setText(_translate("MainWindow", "Tennis"))
        self.class_4_percentage.setPlaceholderText(_translate("MainWindow", "70"))
        self.class_5_percentage.setPlaceholderText(_translate("MainWindow", "70"))
        self.class_3_percentage.setPlaceholderText(_translate("MainWindow", "70"))
        self.label_8.setText(_translate("MainWindow", "Classification"))
        self.label_9.setText(_translate("MainWindow", "Train Percent"))
        self.button_classify.setText(_translate("MainWindow", "Classify"))
        self.result_classification.setPlaceholderText(_translate("MainWindow", "Results For Classification"))
        self.label_10.setText(_translate("MainWindow", "Clustering"))
        self.result_clustering.setPlaceholderText(_translate("MainWindow", "Results For Clustering"))
        self.button_cluster.setText(_translate("MainWindow", "Cluster"))
        self.button_classification_accuracy.setText(_translate("MainWindow", "Accuracy"))
        self.clustering_k.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Sans Serif\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.clustering_k.setPlaceholderText(_translate("MainWindow", "3"))
        self.button_cluster_accuracy.setText(_translate("MainWindow", "Accuracy"))
        self.label_11.setText(_translate("MainWindow", "Set K"))
        self.classification_k.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Sans Serif\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.classification_k.setPlaceholderText(_translate("MainWindow", "3"))
        self.label_12.setText(_translate("MainWindow", "Set K"))
        self.button_train.clicked.connect(self.trainHandler)
        self.button_classify.clicked.connect(self.classify_uploadHandler)
        self.button_classification_accuracy.clicked.connect(self.classification_accuracy_uploadHandler)
        self.button_cluster.clicked.connect(self.cluster)
        self.button_cluster_accuracy.clicked.connect(self.cluster_accuracy)
    def cluster_accuracy(self):
        purity=calculate_purity()
        self.result_clustering.setText('Purity:'+str(purity))
    def trainHandler(self):
        global trainingDocsPercentage
        self.result_classification.setText('Training Model')
        global K
        if self.classification_k.toPlainText() !='':
            K = int(self.classification_k.toPlainText())
        if self.class_1_percentage.toPlainText() != '':
            trainingDocsPercentage[0]=  int(self.class_1_percentage.toPlainText())
        if self.class_2_percentage.toPlainText() != '':
            trainingDocsPercentage[1] = int(self.class_2_percentage.toPlainText())
        if self.class_3_percentage.toPlainText() != '':
            trainingDocsPercentage[2] = int(self.class_3_percentage.toPlainText())
        if self.class_4_percentage.toPlainText() != '':
            trainingDocsPercentage[3] = int(self.class_4_percentage.toPlainText())
        if self.class_5_percentage.toPlainText() != '':
            trainingDocsPercentage[4] = int(self.class_5_percentage.toPlainText())
        buildLexicon()
        buildDocumentVectors()
        self.result_classification.setText('Training Completed Successfully')




    def classify_uploadHandler(self):
        global K
        global Sports
        filename = QFileDialog.getOpenFileName()
        self.result_classification.setText('Classifying..')
        if self.classification_k.toPlainText() != '':
            K = int(self.classification_k.toPlainText())
        createTestVector(filename[0])
        print(testDocumentVector)
        result = classify()
        classSum = []
        for i in range(len(Sports)):
            classSum.append(-1)
            for j in range(K):
                classSum[i] = classSum[i] + result[i][j]
        minClassSum = classSum[0]
        classifiedClass = 0
        for i in range(len(classSum)):
            if classSum[i] < minClassSum and classSum[i] != -1:
                minClassSum = classSum[i]
                classifiedClass = i
        printSim(result, classifiedClass, self)
    def classification_accuracy_uploadHandler(self):
        global K
        global Total
        global Correct
        if self.classification_k.toPlainText() != '':
            K = int(self.classification_k.toPlainText())
        else:
            K=3
        if self.class_1_percentage.toPlainText() != '':
            trainingDocsPercentage[0]=  int(self.class_1_percentage.toPlainText())
        if self.class_2_percentage.toPlainText() != '':
            trainingDocsPercentage[1] = int(self.class_2_percentage.toPlainText())
        if self.class_3_percentage.toPlainText() != '':
            trainingDocsPercentage[2] = int(self.class_3_percentage.toPlainText())
        if self.class_4_percentage.toPlainText() != '':
            trainingDocsPercentage[3] = int(self.class_4_percentage.toPlainText())
        if self.class_5_percentage.toPlainText() != '':
            trainingDocsPercentage[4] = int(self.class_5_percentage.toPlainText())
        calculateAccuracy()
        self.result_classification.setText("Accuracy="+str(Correct)+'/'+str(Total)+'='+str(Correct/Total))
        Total=0
        Correct=0

    def cluster(self):
        global K
        global trainingDocsPercentage
        if self.clustering_k.toPlainText() != '':
            K = int(self.clustering_k.toPlainText())
        else:
            K=2

        text = printClusters()
        self.result_clustering.setText(text)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
