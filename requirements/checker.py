from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn
import progressbar





class SemanticChecker:
    def __init__(self, req, minScore=0.75, maxScore=1.0):
        self.requirements = req
        self.similarities = []
        self.threshold = minScore
        self.maxScore = maxScore
        self.valueRanges = {}

    def penn_to_wn(self, tag):
        """ Convert between a Penn Treebank tag to a simplified Wordnet tag """
        result = None

        for l in ('N', 'V', 'J', 'R'):
            if tag.startswith(l):
                result = l.lower()
                if l == 'J':
                    result = 'a'

                break

        return result

    def tagged_to_synset(self, word, tag):
        wn_tag = self.penn_to_wn(tag)
        if wn_tag is None:
            return None

        try:
            return wn.synsets(word, wn_tag)[0]
        except:
            return None

    def getSimilarity(self, sentence1, sentence2):
        """ compute the sentence similarity using Wordnet """
        # Tokenize and tag
        sentence1 = pos_tag(word_tokenize(sentence1))
        sentence2 = pos_tag(word_tokenize(sentence2))

        # Get the synsets for the tagged words
        synsets1 = [self.tagged_to_synset(*tagged_word) for tagged_word in sentence1]
        synsets2 = [self.tagged_to_synset(*tagged_word) for tagged_word in sentence2]

        # Filter out the Nones
        synsets1 = [ss for ss in synsets1 if ss]
        synsets2 = [ss for ss in synsets2 if ss]

        score, count = 0.0, 0

        # For each word in the first sentence
        for synset in synsets1:
            # Get the similarity value of the most similar word in the other sentence
            best=-1
            for ss in synsets2:
                sc = synset.path_similarity(ss)
                if sc is not None and sc > best:
                    best = sc

            #best_score = max([synset.path_similarity(ss) for ss in synsets2])
            best_score = best

            # Check that the similarity could have been computed
            if best_score is not None:
                score += best_score
                count += 1

        # Average the values
        if count > 0:
            score /= count
        else:
            score = 0

        return score

    def check(self):
        similarities = []
        counter=0
        self.valueRanges={}

        print("Using threshold %s to %s" % (self.threshold, self.maxScore))
        with progressbar.ProgressBar(max_value=len(self.requirements)) as bar:
            for reqkey1, req1 in self.requirements.items():
                for reqkey2, req2 in self.requirements.items():
                    if reqkey1 != reqkey2 and not self.isDuplicatePair(similarities, [req1, req2]):
                        score = self.getSimilarity(req1.getFullText(), req2.getFullText())
                        self.updateRanges(score)

                        if score >= self.threshold and score <= self.maxScore:
                            similarities.append(  { "reqs": [req1, req2], "score": score } )

                counter = counter + 1
                bar.update(counter)

        return (similarities, self.valueRanges)

    def isDuplicatePair(self, pool, newPair):
        result = False
        for item in pool:
            s = item['score']
            pair = item['reqs']
            if newPair[0] in pair and newPair[1] in pair:
                result = True
                break

        return result

    def updateRanges(self, score):
        if score < 0:
            score = 0

        v = int(score*10)
        if v not in self.valueRanges.keys():
            self.valueRanges[v] = 0

        self.valueRanges[v] += 1

    def prettyPrint(self, similarities):
        for s in similarities:
            print("Req1: %s\nReq2: %s\n*** Score: %s\n" % (s['reqs'][0], s['reqs'][1], s['score']))



