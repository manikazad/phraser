
from collections import defaultdict, Counter

class PhraseExtracter():
    """
    # This class forms the core of the extractions being done.
    # It's function named "extract_phrase" takes the dependency parser results (dependency relations) as the input
                    and returns the phrases constructed based on the rules defined.
    # The rules defined can be found in the documentation.
    """
    def __init__(self):
        pass

    def extract_phrase(self,  sentence):
        """
        Extracts the phrases based on the dependency relations
        :param: sentence data_objects2
        :return: phrases
        """
        dependencies = sentence.dependencies
        wordIndex = sentence.wordindex

        # for rel, gov, dep in dependencies:
        #     print(rel, gov, dep)
        #     print(rel, [wordIndex[i]['word'] for i in gov.split('_')], [wordIndex[i]['word'] for i in dep.split('_')])

        """
        The following steps are some precprocessing steps required before building the phrases.
        """
        dependencies = self.collate_relation(dependencies, REL = 'nn' )          # Collating the Noun words together.
        dependencies = self.collate_relation(dependencies, REL = 'compound')     # new
        
        dependencies = self.collate_relation(dependencies, REL = 'quantmod')     # new
        dependencies = self.collate_relation(dependencies, REL = 'nummod')       # new
        dependencies = self.collate_relation(dependencies, REL = 'num')          # Collating the numerical entity with associated word.
        dependencies = self.collate_relation(dependencies, REL = 'nmod')         # new
        # dependencies = self.collate_relation(dependencies, REL = 'case')         # new
        # dependencies = self.collate_relation(dependencies, REL = 'poss')         # new
        dependencies = self.collate_relation(dependencies, REL = 'aux')
        dependencies = self.collate_relation(dependencies, REL = 'amod')         # Collating the adjectival modifier together
        dependencies = self.collate_relation(dependencies, REL = 'prt')          # Collating the verb particle words together.
        dependencies = self.conditionally_collate_relation(dependencies,wordIndex, REL = 'pobj', govPos = 'IN', depPos = 'IN')         # Collating the preposition of an object
        dependencies = self.handle_conjunction(dependencies)
        dependencies = self.find_negations(dependencies)                         # Finding negations and putting a 'neg' marker along with the governer word.

        # for rel, gov, dep in dependencies:
        #     print(rel, gov, dep)
        #     print(rel, [wordIndex[i]['word'] for i in gov.split('_') if i != 'neg'], [wordIndex[i]['word'] for i in dep.split('_') if i != 'neg'])

        phrases = self.phrase(dependencies)

        # phrase_value = getPhraseValue(phrases, wordIndex)
        return phrases


    def handle_conjunction(self, dependencies):
        """
        this functions handles the conjuction in a sentence.
        """
        newDeps = []

        conjs = []
        for rel, gov, dep in dependencies:
            if rel in ['conj']:
                conjs.append([gov, dep])
            else:
                newDeps.append([rel, gov, dep])

        for gov, dep in conjs:
            for rel, gove, depe in dependencies:
                if rel in ['nsubj', 'dobj', 'iobj', 'prep', "appos"] and gov == gove and not self.relations_exists(dep, rel, dependencies, True ):
                    newDeps.append([rel, dep, depe])
                if rel in ['nsubj', 'dobj', 'iobj', 'prep', 'appos'] and gov == depe and not self.relations_exists(dep, rel, dependencies, False ):
                    newDeps.append([rel, gove, dep])
        # if same relation exists for the conjunctions second part no need creating a new one.
        return newDeps

    def relations_exists(self, word, rel, dependencies, gov ):
        """
        check if a relation exists for a given word.
        Inputs: index of the word, the relation to be checked, and boolean variable, which is True if the word needs to be governer in the relation.
        """
        for rele, gove, depe in dependencies:
            if gov:
                if rele == rel and word == gove:
                    return True
            if not gov:
                if rele == rel and word == depe:
                    return True
        return False

    def get_all_phrases(self, phrasecomps):
        """
        Gets all the possible phrase formation between two given subhrases.
        """
        phrases = self.create_all_paths(phrasecomps)
        phrases = sorted(phrases, key=lambda x: x[0])
        return phrases

    def create_all_paths(self, nodes):
        """
        A recursive function to find the unique paths between mutliple groups of nodes.
        """
        path = []
        if not nodes:
            return path
        if nodes[1:]:
            for node in nodes[0]:
                for n in self.create_all_paths(nodes[1:]):
                    path.append([node]+n)
        else:
            for node in nodes[0]:
                path.append([node])
            return path
        return path

    def phrase(self, dependencies):
        """
        This function builds the phrases from the prepreocessed dependency relations.
        The phrase being built is of the basic kind, which exists in the form and order of "SUBJECT-VERB-OBJECT", containing two or more of its consecutive parts.
        :param: preprocessed and modified dependencies
        :return: phrases in term of word indices
        """

        so_tuple = self.findAppos(dependencies)
        sv_tuple = self.find_subj(dependencies)                                 # Finding the subject-verb tuples based on "subj" relations.
        obj_tuple = self.find_obj(dependencies)                                 # Finding the verb-object tuples based on the "obj" relations.
        xcomp_tuple = self.find_xcomp(dependencies)

        remaining_obj_tuple = obj_tuple[:]
        phrases = []

        for sotup in so_tuple:
            phrases += self.apposPhrase(sotup, dependencies)

        # for otup in obj_tuple:
        #     overb, obj = otup
        #     for comp in xcomp_tuple:
        #         gov, dep = comp
        #         if gov == overb:
        #             sv_tuple.append((obj, dep))

        for tup in sv_tuple:                                                    # Iterating over the found subj-verb tuples and looking for obj-verb tuples with common verb
            verb, subj = tup

            verb_prep_phrases = self.prep_phrase(verb, dependencies) #, verb_prep)                         # Creating the Verb Sub-phrase with the original word and the prepositional part
            # print("HEY HEY ATTENTION", self.find_rel_recursively('prep', 'pobj', verb, dependencies))
            ventity = [tuple([verbp, 'verb']) for verbp in verb_prep_phrases]  # tuple([ventity, 'verb'])

            subj_prep_phrases = self.prep_phrase(subj, dependencies) # , subj_prep)      # Creating the Subject Sub-phrase with the original word and the prepositional part
            sentity = [tuple([subjp, 'subj']) for subjp in subj_prep_phrases]  # tuple([sentity, 'subj'])

            found_obj = False
            for otup in obj_tuple :
                if len(otup) == 3:
                    overb, prep, obj = otup
                    overb = overb.split('_')[0]
                    if verb == overb:
                        try:
                            remaining_obj_tuple.remove(otup)
                        except ValueError:
                            pass
                        ventity = [tuple([otup, 'verb'])]
                        all_phrases = self.get_all_phrases([sentity, ventity])
                        found_obj = True
                        phrases += all_phrases

                else:
                    overb, obj = otup
                    if verb == overb:
                        try:
                            remaining_obj_tuple.remove(otup)
                        except ValueError:
                            pass
                        obj_prep_phrases = self.prep_phrase(obj, dependencies)
                        found_obj = True
                        oentity = [tuple([objp, 'obj']) for objp in obj_prep_phrases]
                        all_phrases = self.get_all_phrases([sentity, ventity, oentity])

                        phrases += all_phrases

            if not found_obj:
                attr_tuple = self.find_attr(subj, dependencies)
                if attr_tuple != []:
                    for attup in attr_tuple:
                        phrases += self.attrPhrase(subj, attup, dependencies)
                else:
                    all_phrases = self.get_all_phrases([sentity, ventity])
                    phrases += all_phrases

        for otup in remaining_obj_tuple:
            overb, obj = otup
            obj_prep_phrases = self.prep_phrase(obj, dependencies)
            verb_prep_phrases = self.prep_phrase(overb, dependencies)

            ventity = [tuple([verbp, 'verb']) for verbp in verb_prep_phrases]
            oentity = [tuple([objp, 'obj']) for objp in obj_prep_phrases]

            phrase = self.get_all_phrases([ventity, oentity])
            phrases += phrase

        return phrases
        # return new_phrases

    def find_xcomp(self, dependencies):
        xcomp_verb_tup = []
        for row in dependencies:
            rel, gov, dep = row
            if 'comp' in rel:
                xcomp_verb_tup.append([gov, dep])
        return xcomp_verb_tup

    def findAppos(self, dependencies):
        """
        find the appos relations in the dependencies.
        """
        subj_obj_tup = []
        for row in dependencies:
            rel, gov, dep = row
            if 'appos' in rel:
                subj_obj_tup.append([gov, dep])
        return subj_obj_tup


    def attrPhrase(self, subj, so_tuple, dependencies):

        # case 1 : appos has relating prep and pobj relations
        # case 2 : appos has no other relations

        word, word_dep = so_tuple
        phrases = []
        for row in dependencies:
            rel, gov, dep = row
            if gov == word_dep and rel  == 'prep' :
                sentity = tuple([[subj + "_main"] , "subj"])
                dep_tup = self.find_rel(dep, 'pobj', dependencies)
                if dep_tup != None:
                    dep_gov, dep_dep = dep_tup
                    ventity = tuple([ (word + "_main", gov,  dep) ,'verb'] )
                    oentity = tuple([ [dep_dep],'obj'] )

                    phrases.append([sentity, ventity, oentity])

        return phrases

    def apposPhrase(self, so_tuple, dependencies):

        # case 1 : appos has relating poss and case relations
        # case 2 : appos has relating prep and pobj relations
        # case 3 : appos has no other relations

        word, word_dep = so_tuple
        phrases = []
        for row in dependencies:
            rel, gov, dep = row
            if gov == word_dep and rel in ('poss', 'prep'):
                sentity = tuple([[word + "_main"] , "subj"])
                if rel == 'poss':
                    dep_tup = self.find_rel(dep, 'case', dependencies)
                    if dep_tup != None:
                        dep_gov, dep_dep = dep_tup
                        ventity = tuple([ ("is_main", gov, "of" ) ,'verb'] )
                        oentity = tuple([ [dep],'obj'] )

                        phrases.append([sentity, ventity, oentity])

                elif rel == 'prep':
                    dep_tup = self.find_rel(dep, 'pobj', dependencies)
                    if dep_tup != None:
                        dep_gov, dep_dep = dep_tup
                        ventity = tuple([ ("is_main", gov,  dep) ,'verb'] )
                        oentity = tuple([ [dep_dep],'obj'] )

                        phrases.append([sentity, ventity, oentity])
        return phrases

    def find_rel(self, word, rel, dependencies):

        for row in dependencies:
            relt, gov, dep = row
            if relt == rel and gov == word:
                return (gov, dep)
        return None

    def find_attr(self, word, dependencies):
        """
        find the attr relations in the dependencies.
        """
        subj_obj_tup = []
        for row in dependencies:
            rel, gov, dep = row
            if 'attr' in rel:
                subj_obj_tup.append([gov, dep])
        return subj_obj_tup

    def removeRedundantVentity(self, ventities, duplicate):
        """
        removes the duplicate verb sub phrase.
        """
        dupVerb = [t for t in duplicate if main in t.split('_')][0]
        newVens = ventities[:]
        for tup in ventities:
            ven, ptype = tup
            if dupVerb in ven:
                newVens.remove(tup)
        return newVens


    def prep_phrase1(self, word, dependencies): #, prep_tuples):
        """
        build the prepositional phrase for the given word and its corrwspoding prepositional tuple (word and prep)
        :param: word , prepositional tuple
        :result: a complete propositional subphrase
        """
        prep_tuples = self.find_prep(word, dependencies)

        word = word + "_main"
        p_phrases = []
        for prep_tup in prep_tuples:
            if prep_tup != None:
                gov, prep, ent = prep_tup
                entity = sorted([ent, prep, word], key = lambda x: int(x.split('_')[0]) if x.split('_')[0] != 'neg' else int(x.split('_')[1]))
                # entity.insert(1, prep)
            else:
                entity = [word]
            p_phrases.append(entity)
        if p_phrases != []:
            return p_phrases
        else:
            return [[word]]

    def find_prep(self, word, dependencies):
        """
        finds the prepostional relations for a given word.
        :param: word, dependency
        :result: related preposition and associated word.
        """
        tups = []
        for row in dependencies:
            rel, gov, dep = row
            if 'prep' in rel and gov == word:
                dep_tup = self.find_rel(dep, 'pobj', dependencies)
                if dep_tup != None:
                    prep, dep_dep = dep_tup
                    tups.append((gov, dep, dep_dep))

            elif 'prep' in rel and dep == word:
                dep_tup = self.find_rel(gov, 'pobj', dependencies)
                if dep_tup != None:
                    prep, dep_dep = dep_tup
                    tups.append((dep, gov, dep_dep))

        return tups


    def prep_phrase(self, word, dependencies):

        prep_tuple = self.find_rel_recursively('prep', 'pobj', word, dependencies)
        word = word + "_main"
        p_phrases = []

        if prep_tuple != []:
            entity = sorted(prep_tuple + [word], key = lambda x: int(x.split('_')[0]) if x.split('_')[0] != 'neg' else int(x.split('_')[1]))
        else:
            entity = [word]
        p_phrases.append(entity)

        if p_phrases != []:
            return p_phrases
        else:
            return [[word]]

    def find_rel_recursively(self, rel1, rel2, word, dependencies):

        rel_tup = []
        for row in dependencies:
            rel, gov, dep = row
            if rel1 == rel and word == gov:
                rel_tup = [dep]
                rel_tup += self.find_rel_recursively(rel2, rel1, dep, dependencies)

        return rel_tup

    # def find_prep(self, word, dependencies):
    #     for row in dependencies:
    #         rel, gov, dep = row
    #         if 'prep' in rel and gov == word:
    #             for row in dependencies:
    #                 rel1, gov1, dep1 = row
    #                 if rel1 == 'pobj' and gov1 == dep:
    #                     return gov1 , dep1

    #         if 'pobj' in rel and dep == word:
    #             for row in dependencies:
    #                 rel1, gov1, dep1 = row
    #                 if rel1 == 'prep' and dep1 == gov:
    #                     return dep1 , gov1
    #     return None

    

    def find_subj(self, dependencies):
        """
        find the subject relations in the dependencies.
        """
        subj_verb_tup = []
        for row in dependencies:
            rel, gov, dep = row
            if 'subj' in rel:
                subj_verb_tup.append([gov, dep])
        return subj_verb_tup

    def find_obj(self, dependencies):
        """
        find the object relations in the dependencies.
        """
        obj_verb_tup = []
        for row in dependencies:
            rel, gov, dep = row
            if rel in ['dobj', 'iobj']:
                obj_verb_tup.append([gov, dep])

        return obj_verb_tup

    def isMain(self, phrase):
        """
        checks if the given phrase is the main part(returns True) of the subphrase or a prepositional(returns False)
        """
        words = phrase.split('_')
        if "main" in words:
            return True
        return False

    def collate_relation(self, dependencies, REL = 'ROOT'):
        """
        # this function collates the two words which are related by the specified relation
                    \ and also updates the remaining dependency with the newly constructed words entity
        :param: dependencies, relation to be collated
        :return: updated dependencies
        """
        Deps = []
        newIndex = {}
        for rel, gove, depe in dependencies:
            if rel == REL:
                gov = newIndex[gove] if gove in newIndex else gove
                dep = newIndex[depe] if depe in newIndex else depe
                newIndex[gove] = '_'.join(sorted(gov.split('_') + dep.split('_'), key = lambda x: int(x)))
            else:
                Deps.append([rel, gove, depe])

        newIndex = self.reduceNewIndex(newIndex)
        newDeps = []
        for rel, gov, dep in Deps:
            if gov in newIndex: gov = newIndex[gov]
            if dep in newIndex: dep = newIndex[dep]
            newDeps.append([rel, gov, dep])

        return newDeps

    def reduceNewIndex(self, newIndex):
        reducedIndex = {}
        for key, val in newIndex.items():
            if val in newIndex:
                while val in newIndex:
                    val = newIndex[val]
            reducedIndex[key] = val

        return reducedIndex

    def conditionally_collate_relation(self, dependencies, wordindex, REL = 'ROOT', govPos = None, depPos = None ):
        """
        # this function collates the two words which are related by the specified relation but restricted based on the pos tag of the words.
                    \ and also updates the remaining dependency with the newly constructed words entity
        :param: dependencies, relation to be collated
        :return: updated dependencies
        """
        Deps = []
        newIndex = {}
        switch1, switch2, switch3 = [False]*3
        if govPos != None and depPos == None:
            switch1 = True
        if depPos != None and govPos == None:
            switch2 = True
        if govPos != None and depPos != None:
            switch3 = True

        for rel, gove, depe in dependencies:
            try:
                if switch1 and rel == REL and wordindex[gove]['pos'] == govPos:
                    gov = newIndex[gove] if gove in newIndex else gove
                    dep = newIndex[depe] if depe in newIndex else depe
                    newIndex[gove] = '_'.join(sorted(gov.split('_') + dep.split('_'), key = lambda x: int(x)))

                elif switch2 and rel == REL and wordindex[depe]['pos'] == depPos:
                    gov = newIndex[gove] if gove in newIndex else gove
                    dep = newIndex[depe] if depe in newIndex else depe
                    newIndex[gove] = '_'.join(sorted(gov.split('_') + dep.split('_'), key = lambda x: int(x)))

                elif switch3 and rel == REL and wordindex[gove]['pos'] == govPos and wordindex[depe]['pos'] == depPos:
                    gov = newIndex[gove] if gove in newIndex else gove
                    dep = newIndex[depe] if depe in newIndex else depe

                    newIndex[gove] = '_'.join(sorted(gov.split('_') + dep.split('_'), key = lambda x: int(x)))
                else:
                    Deps.append([rel, gove, depe])
            except KeyError:
                Deps.append([rel, gove, depe])

        newDeps = []
        for rel, gov, dep in Deps:
            if gov in newIndex: gov = newIndex[gov]
            if dep in newIndex: dep = newIndex[dep]
            newDeps.append([rel, gov, dep])

        return newDeps


    def find_negations(self, dependencies):
        """
        Finds the negation relations and replaces them with a negation tag along with the associated word.
        :param: dependencies
        :return: updated dependencies
        """
        Deps = []
        newIndex = {}
        for rel, gove, depe in dependencies:
            if rel == 'neg':
                if gove in newIndex: gove = newIndex[gove]
                if depe in newIndex: depe = newIndex[depe]
                newIndex[gove] = '_'.join(['neg'] + gove.split('_'))
            else:
                Deps.append([rel, gove, depe])

        newDeps = []
        for rel, gov, dep in Deps:
            if gov in newIndex: gov = newIndex[gov]
            if dep in newIndex: dep = newIndex[dep]
            newDeps.append([rel, gov, dep])

        return newDeps

def getPhraseValue(phrases, wordindex):
    """
    Returns the phrase in text taking the indexes as input
    """
    # val = []
    phs = []
    for phrase in phrases:
        ph = []
        for subphrase,ptype in phrase:
            sph = []
            val = []
            for entity in subphrase:
                for num in entity.split('_'):
                    try:
                        word = wordindex[num]['word']
                        val.append(word)
                    except KeyError:
                        if num not in ["main", "prep"]:
                            val.append(num)
            val = " ".join(val)
            sph = [ptype, val]
            ph.append(sph)

        phs.append(ph)
    return phs


class Sentence():
    """
    # After the dependency parse is run, this object stores the result in a structured manner for them to be used with ease later.
    # It stores all the dependency relations, and information about each word.
    # The dependency relations are  originally available in the form of [rel, word1-index1, word2-index2], this oject stores these relations
        in the form of more simpler form as [rel, index1, index2], which is essential and quite easier to deal with for further processing.
    # However the original form of dependencies are also retained in another variable
    # Each word information is stored as an indexed dictionary, with index being the ordinal position of the word in the sentence.
    # Other meta information of a word like, its POS tag, lemma form of word and character offsets are also stored in the abovementioned dictionary.
    # This object also has the provision for storing the phrase extraction result and concept mapping result for each of the phrase extracted.
    """

    def __init__(self, sent):
        self.text = sent.text
        self.words = [word.text for word in sent]
        self.tags = [tok.tag_ for tok in sent]
        self.lemmas = [tok.lemma_ for tok in sent]
        self.index = [tok.i+1 for tok in sent]
        self.tagged_words = self.tagged(sent)
        self.wordindex, self.offset = self.tagged_index_namedEntities(sent)
        self.namedEntities =  sent.ents
        self.dependencies, self.dependencies_with_words = self.get_dependencies(sent)  #dependencies as list of triples with word index.
        self.dependency_tree = self.sent_tree(self.dependencies)                #contains graph-tree in dict format
                      #word index in dict format
        # self.phrases = []
        self.phraseAndconcepts = []

    def get_dependencies(self, sent):
        word_triples = [(tok.dep_, tok.head.text, tok.text) for tok in sent]
        idx_triples = [(tok.dep_, str(tok.head.i+1), str(tok.i+1) ) for tok in sent]
        return idx_triples, word_triples

    def tagged(self, sent):
        return [TaggedWord(tok.text, tok.tag_, tok.lemma_, tok.i+1, begin = tok.idx, end= tok.idx+len(tok.text)) for tok in sent]

    def sent_tree(self, graph):
        """
        creates a graphical structure of the sentence based on the dependency results.
        :param: dependency relations
        :return: a graph representaion of the relations between words.
        """
        graphDict = {}
        for rel,a,b in graph:
            if a in graphDict:
                graphDict[a].append(b)
            else:
                 graphDict[a] = [b]
            #if undirected:         # Assuming dependency graphs to be undirected
            if b in graphDict:
                graphDict[b].append(a)
            else:
                graphDict[b] = [a]
        return graphDict

    def tagged_index_namedEntities(self, sent):
        """
        structures all the relvant information available for each word from the dependency parser results and creates a dictionary with key as the word index.
        the word index is used as key because the dependency relations are in the form of word index instead of words.
        :param: "words" from dependency result
        :return: 1. Word python object, 2. Word Index, 3. Named Entities(dependecy result), 4. Sentence Offsets
        """
        namedEntities = defaultdict(list)
        wordIndex = {}
        wordIndex['0']= {}
        wordIndex['0']['word'] = u'ROOT'
        wordIndex['0']['pos'] = u'ROOT'
        wordIndex['0']['lemma'] = u'ROOT'
        tagged = []
        sentenceBegin = -1
        sentenceEnd = 0
        for i, tok in enumerate(sent):
            index = str(tok.i+1)
            wordIndex[index] = {}
            wordIndex[index]['word'] = tok.text
            wordIndex[index]['lemma'] = tok.lemma_

            wordIndex[index]['pos'] = tok.tag_
            wordIndex[index]['choffbegin'] = tok.idx
            wordIndex[index]['choffend'] = tok.idx + len(tok.text)

            if sentenceBegin == -1:
                sentenceBegin = sent.start_char
                sentenceEnd = sent.end_char

        offsets = tuple([sentenceBegin, sentenceEnd])
        return wordIndex, offsets

    def __str__(self):
        return self.text


class TaggedWord():
    def __init__(self, word, tag, lemma, index, begin=0, end=0):
        self.word = word
        self.tag = tag
        self.lemma = lemma
        self.index = index
        self.begin = begin
        self.end = end

    def __str__(self):
        return "(%s, %s, %s)" % (self.word, self.tag, self.tag)


