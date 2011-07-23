import random
from random import randrange
import os
import math

class ChurnSolver:
    cipher = ''
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    digraphScores = []
    tetragraphScores = []
    key = {}
    reverseKey = {}
    expectedDigraph = {}
    goodMutations = {}
    prb = [1,1,1,1,1,1,1,2,2,2,2,2,2,2,3,3,3,3,3,3,3,4,4,4,4,5,5,5,5,5,5,5,6,6,6,6,6,7,7,7,7,7,8,8,9,9,9,9,10,10,10,10,10,11,11,11,11,12,12,12,12,13,13,14,14,15,15,16,16,16,16,17,17,18,18,19,19,20,21,21,22,23,23,24,25,26,27,28,29,30,31,33,34,37,39,41,43,48,57,60]
    
    previousScore = 0

    bestKey = {}
    bestPlaintext = ''
    bestScore = 0
    
    lastCph = (0,0)
    lastPln = (0,0)
    lastOldCph = (0,0)
    lastOldPln = (0,0)
    
    def __init__(self):
        self.loadDigraphScores()
        self.loadTetragraphScores()
        self.loadCiphertext()
        self.loadExpected()
        
    def churn(self, cipher, iterations):
        self.bestKey = self.key
        self.bestScore = 0
        
        i = 0
        stagnant = 0
        while i < iterations:
            if stagnant > 1000000:
                stagnant = 0
                self.loadStartingKey()
                plaintext = self.decipher(cipher)
                self.previousScore = self.score(plaintext)
            self.mutate()
            plaintext = self.decipher(cipher)
            score = self.score(plaintext)
            if(score > self.previousScore - self.prb[randrange(len(self.prb))]):
                # accept mutation
                self.previousScore = score
                if score > self.bestScore:
                    self.bestScore = score
                    self.bestPlaintext = plaintext
                    self.bestKey = self.key.copy()
                    stagnant = 0
                else:
                    stagnant += 1
            else:
                self.revertMutation()
                
            if i%1000 == 0:
                print str(i) + ' ' + str(self.previousScore) + ' ' + str(self.bestScore) + ' ' + plaintext
            
            i += 1
                
        print "RESULTS:"
        print self.bestKey
        print self.bestPlaintext
        print self.bestScore
        
    def mutate(self):
        cph = (randrange(26), randrange(26))
        pln = (randrange(26), randrange(26))
        oldpln = self.key[cph]
        oldcph = self.reverseKey[pln]
        self.key[cph] = pln
        self.reverseKey[pln] = cph
        self.key[oldcph] = oldpln
        self.reverseKey[oldpln] = oldcph
        
        self.lastCph = cph
        self.lastPln = pln
        self.lastOldCph = oldcph
        self.lastOldPln = oldpln
        
    def revertMutation(self):
        self.key[self.lastCph] = self.lastOldPln
        self.key[self.lastOldCph] = self.lastPln
        self.reverseKey[self.lastPln] = self.lastOldCph
        self.reverseKey[self.lastOldPln] = self.lastCph
        
    def score(self, plaintext):
        score = 0
        for i in range(len(plaintext) - 3):
            index = self.alphabet.index(plaintext[i])*17576 + self.alphabet.index(plaintext[i+1])*676 + self.alphabet.index(plaintext[i+2])*26 + self.alphabet.index(plaintext[i+3])
            score += self.tetragraphScores[index]*8.8
            #index = self.alphabet.index(plaintext[i])*26 + self.alphabet.index(plaintext[i+1])
            #score += self.digraphScores[index] * 2.34
        return float(score)/float(len(plaintext)) * 110
    
    def decipher(self, cipher):
        str_list = []
        for i in range(0, len(cipher) - 1, 2):
            cph = (self.alphabet.index(cipher[i]), self.alphabet.index(cipher[i+1]))
            pln = self.key[cph]
            str_list.append(self.alphabet[pln[0]])
            str_list.append(self.alphabet[pln[1]])
        return ''.join(str_list)
    
    def encipher(self, plaintext):
        str_list = []
        for i in range(0, len(plaintext) - 1, 2):
            pln = (self.alphabet.index(plaintext[i]), self.alphabet.index(plaintext[i+1]))
            cph = self.reverseKey[pln]
            str_list.append(self.alphabet[cph[0]])
            str_list.append(self.alphabet[cph[1]])
        return ''.join(str_list)

    def loadExpected(self):
        f = open("../DigraphFrequencies.txt")
        fc = f.read()
        lines = fc.split("\n")
        total = 0
        for line in lines:
            map = line.split("=")
            key = map[0]
            if(key == "total"):
                total = int(map[1])
                break
        for line in lines:
            map = line.split("=")
            key = map[0]
            val = map[1]
            
            keyTup = (self.alphabet.index(key[0]), self.alphabet.index(key[1]))
            if(key != "total"):
                self.expectedDigraph[keyTup] = float(val)/float(total)
        
    def createMutationTable(self):
        self.goodMutations = {}
        for i in range(26):
            for j in range(26):
                tup = (i, j)
                print self.alphabet[tup[0]] + self.alphabet[tup[1]] + ": " + str(len([(x, y) for (x, y) in self.expectedDigraph if abs(self.expectedDigraph[(x,y)] - self.expectedDigraph[tup]) < 0.0001]))
                if tup == (15, 0):
                    print [self.tupToDigraph((x,y)) for (x, y) in self.expectedDigraph if abs(self.expectedDigraph[(x,y)] - self.expectedDigraph[tup]) < 0.0001]
                    
        print self.expectedDigraph[self.digraphToTup("pa")]
                    
    def digraphToTup(self, digraph):
        return (self.alphabet.index(digraph[0]), self.alphabet.index(digraph[1]))
    
    def tupToDigraph(self, tup):
        return self.alphabet[tup[0]] + self.alphabet[tup[1]]
                
            
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def loadCiphertext(self):
        f = open("../cipher.txt")
        self.cipher = f.read()
    
    def loadDigraphScores(self):
        f = open("../digraphfreqs.txt")
        str = f.read()
        vals = str.split(",")
        for i in range(len(vals)):
            self.digraphScores.append(int(vals[i]))
            
    def loadTetragraphScores(self):
        f = open("../tetrafreqs.txt")
        fc = f.read()
        vals = fc.split(",")
        for i in range(len(vals)):
            self.tetragraphScores.append(int(vals[i]))
            
    def loadStartingKey(self):
        f = open("../startingkey.txt")
        fc = f.read()
        mappings = fc.split("\n")
        for map in mappings:
            pair = map.split(":")
            cph = (self.alphabet.index(pair[0][0]), self.alphabet.index(pair[0][1]))
            pln = (self.alphabet.index(pair[1][0]), self.alphabet.index(pair[1][1]))
            self.key[cph] = pln
            self.reverseKey[pln] = cph
        
    def generateRandomKey(self):
        vals = [(x,y) for x in range(26) for y in range(26)]
        random.shuffle(vals)
        for i in range(26):
            for j in range(26):
                val = vals.pop()
                self.key[(i, j)] = val
                self.reverseKey[val] = (i, j)  
                
    def verify(self):
        d = self.key.copy()
        self.mutate()
        print str(d == self.key)
        self.revertMutation()
        print str(d == self.key)
        
c = ChurnSolver()
c.loadStartingKey()
c.createMutationTable()

#c.churn(c.cipher[0:600], 10000000)

#pltx = "InPythonthestringobjectisimmutableeachtimeastringisassignedtoavariableanewobjectiscreatedinmemorytorepresentthenewvalueThiscontrastswithlanguageslikeperlandbasicwhereastringvariablecanbemodifiedinplaceThecommonoperationofconstructingalongstringoutofseveralshortsegmentsisnotveryefficientinPythonifyouusetheobviousapproachofappendingnewsegmentstotheendoftheexistingstringEachtimeyouappendtotheendofastringthePythoninterpretermustcreateanewstringobjectandcopythecontentsofboththeexistingstringandtheappendedstringintoitAsthestringsyouaremanipulatingbecomelargethisprocesbecomesincreasinglyslow".lower()
#cph = c.encipher(pltx)
#c.generateRandomKey()
#self.loadStartingKey()
#c.cipher = cph

#c.churn(c.cipher, 1000000)


avg = 0
for i in range(676*26*26):
    avg += int(c.tetragraphScores[i])
avg = float(avg)/(676*26*26)
#print str(avg*8.8)
