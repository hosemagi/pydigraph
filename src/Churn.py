import random
from random import randrange
from random import choice
import os
import math
from Trie import *
from operator import itemgetter
import time

class ChurnSolver:
    cipher = ''
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    digraphScores = []
    tetragraphScores = []
    key = {}
    reverseKey = {}
    expectedDigraph = {}
    observedDigraph = {}
    goodMutations = {}
    startingKey = {}
    
    targetScore = 0
    trueText = ""
    
    prb = [1,1,1,1,1,1,1,2,2,2,2,2,2,2,3,3,3,3,3,3,3,4,4,4,4,5,5,5,5,5,5,5,6,6,6,6,6,7,7,7,7,7,8,8,9,9,9,9,10,10,10,10,10,11,11,11,11,12,12,12,12,13,13,14,14,15,15,16,16,16,16,17,17,18,18,19,19,20,21,21,22,23,23,24,25,26,27,28,29,30,31,33,34,37,39,41,43,48,57,60]
    letterFrequencies = [0]*26
    #trie = load_dictionary("../lwords.txt")
    
    previousScore = 0

    bestKey = {}
    bestPlaintext = ''
    bestScore = 0
    
    lastCph = (0,0)
    lastPln = (0,0)
    lastOldCph = (0,0)
    lastOldPln = (0,0)
    
    exclusions = []
    
    def __init__(self, cipher):
        self.cipher = cipher
        self.loadDigraphScores()
        self.loadTetragraphScores()
        self.loadStartingKey()
        self.createMutationTable()
        
        self.letterFrequencies[0]    = .08167;
        self.letterFrequencies[1]    = .01492;
        self.letterFrequencies[2]    = .02782;
        self.letterFrequencies[3]    = .04253;
        self.letterFrequencies[4]    = .12702;
        self.letterFrequencies[5]    = .02228;
        self.letterFrequencies[6]    = .02015;
        self.letterFrequencies[7]    = .06094;
        self.letterFrequencies[8]    = .06966;
        self.letterFrequencies[9]    = .00153;
        self.letterFrequencies[10]    = .00772;
        self.letterFrequencies[11]    = .04025;
        self.letterFrequencies[12]    = .02406;
        self.letterFrequencies[13]    = .06749;
        self.letterFrequencies[14]    = .07507;
        self.letterFrequencies[15]    = .01929;
        self.letterFrequencies[16]    = .00095;
        self.letterFrequencies[17]    = .05987;
        self.letterFrequencies[18]    = .06327;
        self.letterFrequencies[19]    = .09056;
        self.letterFrequencies[20]     = .02758;
        self.letterFrequencies[21]     = .00978;
        self.letterFrequencies[22]     = .02360;
        self.letterFrequencies[23]     = .00150;
        self.letterFrequencies[24]     = .01974;
        self.letterFrequencies[25]     = .00074;
        
        #self.exclusions.append((19, 7))
        #self.exclusions.append((7, 4))
                               
        
    def churn(self, cipher, iterations):
        self.bestKey = self.key
        self.bestScore = 0
        
        i = 0
        stagnant = 0
        cycleBestScore = 0
        while i < iterations:
            if stagnant == 1000:
                print "BOOM"
                stagnant = 0
                #self.key = self.startingKey.copy()
                self.generateRandomKey()
                plaintext = self.decipher(cipher)
                self.previousScore = self.score(plaintext)
                cycleBestScore = 0
            numMutations = 1
            if randrange(100) == 1000:
                numMutations = 26
            for j in range(numMutations):
                if randrange(100) > 25:
                    cph = (randrange(26), randrange(26))
                    pln = choice(self.goodMutations[cph])
                    self.mutate(cph, pln)
                else:
                    cph = (randrange(26), randrange(26))
                    pln = (randrange(26), randrange(26))
                    self.mutate(cph, pln)
            plaintext = self.decipher(cipher)
            score = self.score(plaintext)
            if(score > self.previousScore - self.prb[randrange(len(self.prb))]):#*float(stagnant)/2000):
                # accept mutation
                self.previousScore = score
                if score > self.bestScore:
                    self.bestScore = score
                    self.bestPlaintext = plaintext
                    self.bestKey = self.key.copy()    
                
                if score > cycleBestScore:
                    stagnant = 0
                    cycleBestScore = score
                else:
                    stagnant += 1
            else:
                self.revertMutation()
                
            if i%1000 == 0:
                #print str(i) + ' ' + str(int(self.previousScore)) + ' ' + str(int(self.bestScore)) + ' '+str(stagnant) + '\t' + plaintext
                print str(i) + ' ' + str(int(self.previousScore)) + ' ' + str(int(self.bestScore)) + ' '+str(int(self.targetScore)) + " " + str(self.monoMatches(plaintext, self.trueText)) + " " + str(self.diMatches(plaintext, self.trueText)) + '\t' + plaintext
                if i % 10000 == 0:
                    print "BEST TO DATE: " + self.bestPlaintext
                    print self.bestKey
                    
                    if i % 100000 == 0:
                        f = open("../results.txt")
                        fc = f.read()
                        f = open("../results.txt", "w")
                        t = time.time()
                        t = time.ctime(t)
                        f.write(fc)
                        f.write("************************************************************\n")
                        f.write(t + "\t" + str(i) + ": " + str(self.bestScore) + "\t" + str(self.bestPlaintext) + "\n")
                        f.write(str(self.bestKey))
                        f.write("\n")
            
            i += 1
                
        print "RESULTS:"
        print self.bestKey
        
        print self.bestPlaintext
        print self.bestScore
        
    def mutate(self, cph, pln):
        oldpln = self.key[cph]
        if pln in self.exclusions or oldpln in self.exclusions:
           return
        
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
            # tetragraph
            index = self.alphabet.index(plaintext[i])*17576 + self.alphabet.index(plaintext[i+1])*676 + self.alphabet.index(plaintext[i+2])*26 + self.alphabet.index(plaintext[i+3])
            score += self.tetragraphScores[index] * 0.8
            
            # digraph
            #index = self.alphabet.index(plaintext[i])*26 + self.alphabet.index(plaintext[i+1])
            #score += self.digraphScores[index] * 1.17
        
        score = float(score)/float(len(plaintext))
        # trie
        #score += self.trie.scanScore2(plaintext) * .3
        score *= 110
        return score
    
    def monoMatches(self, guessed, real):
        matches = 0
        length = len(guessed)
        if len(real) > length:
            length = len(real)
        for i in range(length):
            if guessed[i] == real[i]:
                matches += 1
        return matches*100/len(guessed)
    
    def diMatches(self, guessed, real):
        matches = 0
        matched = []
        for i in range(0, len(guessed)-1,2):
            if guessed[i:i+2] == real[i:i+2]:
                if guessed[i:i+2] not in matched:
                    score = self.expectedDigraph[self.digraphToTup(guessed[i:i+2])]
                    matches += score
                    matched.append(guessed[i:i+2])       
        return (int(matches*100), matched)
    
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
    
    def analyzeObserved(self, cph):
        self.observedDigraph = {}
        total = 0
        for i in range(0,len(cph)-1, 2):
            digraph = cph[i:i+2]
            tup = self.digraphToTup(digraph)
            if tup not in self.observedDigraph:
                self.observedDigraph[tup] = 0
            self.observedDigraph[tup] += 1.0/(len(cph)/2.0)
            total += 1.0/(len(cph)/2.0)
        for i in range(26):
            for j in range(26):
                if (i, j) not in self.observedDigraph:
                    self.observedDigraph[(i, j)] = 0
            
            

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
                mutations = [(x,y) for (x,y) in self.expectedDigraph if abs(self.expectedDigraph[(x,y)] - self.expectedDigraph[self.key[tup]]) < 0.0025]
                self.goodMutations[(i,j)] = mutations
                #if(i == 15):
                #    print self.tupToDigraph(tup) + " " + str(len(mutations)) + " " + str([self.tupToDigraph((x,y)) for (x, y) in mutations])
                
                    
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
        self.loadExpected()
        self.analyzeObserved(self.cipher)
        
        obs = sorted([(self.observedDigraph[(i, j)], (i, j)) for (i, j) in self.observedDigraph], reverse=True)
        exp = sorted([(self.expectedDigraph[(i, j)], (i, j)) for (i, j) in self.expectedDigraph], reverse=True)
        
        for i in range(len(obs)):
            self.key[obs[i][1]] = exp[i][1]
            self.reverseKey[exp[i][1]] = obs[i][1]
        
        print obs
        print exp
        print self.key
        self.startingKey = self.key
        
    def generateRandomKey(self):
        vals = [(x,y) for x in range(26) for y in range(26)]
        random.shuffle(vals)
        for i in range(26):
            for j in range(26):
                val = vals.pop()
                self.key[(i, j)] = val
                self.reverseKey[val] = (i, j)  
                
    def monoChiScore(self, pln):
        obs = self.getMonoFreqs(pln)
        x = 0.0
        for i in range(26):
            x += (len(pln)*(obs[i] - self.letterFrequencies[i]))**2/(len(pln)*self.letterFrequencies[i])
        return x
        
    def getMonoFreqs(self, pln):
        freqs = [0]*26
        n = float(len(pln))
        for i in range(len(pln)):
            freqs[self.alphabet.index(pln[i])] += 1.0/n
        return freqs
        
                
    def verify(self):
        d = self.key.copy()
        self.mutate((randrange(26), randrange(26)), (randrange(26), randrange(26)))
        print str(d == self.key)
        self.revertMutation()
        print str(d == self.key)
        
    def analyzeMutationTable(self, key, mut):
        correct = 0
        total = 0
        for k in key:
            if key[k] in mut[key[k]]:
                correct += 1
            total += len(mut[k])
        
                
        print "correct subs in mut table: " + str(correct/676.0)
        print "size/original size: " + str(total/(676.0*676.0))

f = open("../warandpeace.txt")
fc = f.read()

encipherer = ChurnSolver("asdfasdfasdfasdfasdf")
encipherer.generateRandomKey()
cipher = encipherer.encipher(fc)

#print cipher

#print "*************************"


#f = open("../cipher.txt")
#fc = f.read()
#cipher = fc
c = ChurnSolver(cipher)
c.cipher = cipher[0:550]

c.trueText = fc[0:550]
c.targetScore = c.score(c.trueText)
c.analyzeMutationTable(encipherer.key, c.goodMutations)

#start = "enveedxbeprtgsnsthyonandeperaghitohqovndshauczkeyuwganosnoavmceagreliotoggstrissouteaghetxfoeianlechaselhljeheumhordqvwqxvaiichewepygwtuedodthhecbstinajallkufhkreareoqvpdseithosewyekqohahpriovlihaetbetindhipionthyodarecastesrhereekertinringmanaterafthmhessdstharemonwheditmialinanthchipajalinaispenderelohelxjseloyortaandroklihatierxbeyprerouteatinrigemyftgafhcmjytdowatezjshamderouteatakedweqdbfhetcfihkstovcaocamanowvsitoldshengitsefmarhiiratanheminberitstradereqqcerenookonetedarnerqnowaspenderewenxewehadslshhieqnepvhizvrnadnainpownznitrimeoranxbmffyatdwnindesledeeneoidormxmvmvvebeowmfczwamecrbranheestharpoonetedtothjraenowaytsgmbannehvndeadaiodsthennhnwhahkhosirvintoesrutiaytucoioaicoaehithasaswesludinpzczvsotasesaledgmpetathausieiiodhaenoiehaateafbesthorbgsidcelusewbhasyansrtzgffrdpweuadomereanithremchdomsianslotatamanhethaslothicrowroutaetavayetpetokthkeripvedroniotointonsomerboerateatedfoustwatharcwidonbeanmefostpithqvgihitathtothreenfoashxuzheslalbohohxrhergrbhdaesarowogsnorceirluna"
#for i in range(len(cipher)-1):
#    cph = c.digraphToTup(cipher[i:i+2])
#    pln = c.digraphToTup(start[i:i+2])
#    c.mutate(cph, pln)
#print c.score(c.decipher(c.cipher))
#c.startingKey = c.key.copy()
print c.startingKey
time.sleep(3)
c.generateRandomKey()
c.churn(c.cipher, 100000000)



#pltx = "InPythonthestringobjectisimmutableeachtimeastringisassignedtoavariableanewobjectiscreatedinmemorytorepresentthenewvalueThiscontrastswithlanguageslikeperlandbasicwhereastringvariablecanbemodifiedinplaceThecommonoperationofconstructingalongstringoutofseveralshortsegmentsisnotveryefficientinPythonifyouusetheobviousapproachofappendingnewsegmentstotheendoftheexistingstringEachtimeyouappendtotheendofastringthePythoninterpretermustcreateanewstringobjectandcopythecontentsofboththeexistingstringandtheappendedstringintoitAsthestringsyouaremanipulatingbecomelargethisprocesbecomesincreasinglyslow".lower()