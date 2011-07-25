class Node(object):
    scanWord = ""
    scanDepth = 0
    def __init__(self, letter='', final=False):
        self.letter = letter
        self.final = final
        self.children = {}
    def __contains__(self, letter):
        return letter in self.children
    def get(self, letter):
        return self.children[letter]
    def add(self, letters, n=-1, index=0):
        if n < 0: n = len(letters)
        if index >= n: return
        letter = letters[index]
        if letter in self.children:
            child = self.children[letter]
        else:
            child = Node(letter, index==n-1)
            self.children[letter] = child
        child.add(letters, n, index+1)
    
    def score(self, word):
        score = 0
        depth = 0
        node = self
        for i in range(0, len(word)):
            if word[i] in node.children: 
                node = node.get(word[i])
                depth += 1
                print node.letter
            else:
                return 0
        if node.final:
            score = depth**2
            return score
        else:
            return 0
                
                
    def scanScore(self, text):
        score = 0
        depth = 0
        node = self
        i = 0
        reset = 0
        while i < len(text):
            c = text[i]
            if c in node.children:
                node = node.get(c)
                depth += 1
                score += depth**2
                reset = i + 1
            else:
                node = self
                depth = 0
                i = reset
            i += 1
        return score/(float(len(text))) * 8
    
    def scanForward(self, text, startIndex):
        score = 0
        node = self
        index = startIndex
        c = text[index]
        streak = 0
        minstreak = 0
        lindex = 0
        while c in node.children and index < len(text):
            node = node.get(c)
            streak += 1
            index += 1
            if index != len(text):
                c = text[index]
            if node.final:
                minstreak = streak
                lindex = index
        if node.final:
            return (streak, startIndex, index)
        return (minstreak, startIndex, lindex)
        
    def scanScore2(self, text):
        score = 0
        wordBounds = []
        for i in range(len(text)):
            res = self.scanForward(text, i)
            if res[0] > 1:
                if i in wordBounds:
                    score += 2*res[0]**2
                else:
                    score += res[0]**2
                
                if res[2] not in wordBounds:
                    wordBounds.append(res[2])
        return float(score)/len(text)
    
    def wordScore(self, text):
        score = 0
        i = 0
        while i < len(text):
            res = self.scanForward(text, i)
            length = res[0]
            if length == 0:
                length = 1
            i += length
            score += length**2
        return score
            
    
def load_dictionary(path):
    result = Node()
    for line in open(path, 'r'):
        word = line.strip().lower()
        result.add(word)
    return result
