print("Staring Text_analizer imports...")
import re
import timeit
from collections import defaultdict
from operator import itemgetter
from copy import deepcopy

from nltk.tokenize import sent_tokenize
from nltk import pos_tag_sents, word_tokenize, ne_chunk_sents, RegexpParser, RegexpChunkParser, pos_tag
from nltk.chunk import conlltags2tree, ieerstr2tree, tree2conlltags
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus.reader.wordnet import WordNetError

from sklearn.feature_extraction.text import TfidfVectorizer

from numpy import array


alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"    
websites = "[.](com|net|org|io|gov)"


print("Done (Text analizer)")

"""
function xSelectorAll(xpath, doc, on_map=null){
	const query = doc.evaluate(xpath, doc, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
	if(on_map){
		return Array(query.snapshotLength).fill(0).map((element, index) => query.snapshotItem(index)).map(x => on_map(x));
	}
	return Array(query.snapshotLength).fill(0).map((element, index) => query.snapshotItem(index));
}

function parse(e){if(e.data.replace('\n','').trim()){return e.data;} return '';} 

xSelectorAll('//*[not(self::script)][not(self::style)]/text()',document,function(e){if(e.data.replace('\n','').trim()){return e.data;} return null;} )

### TO ONE USE FUNCT ###

function(){
    var query={element}.evaluate({xpath},{element},null,XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,null);
    return Array(query.snapshotLength).fill(0).map((element,index) => query.snapshotLength(index)).map(
                x => function(e){if(e.data.replace('\n','').trim()){return e.data;} return '';}(x))).join('\n');
}()
"""
# Green separator of ideas
"""
Pre/Note: 
    Since this methods look computationally intensive I shoud make use of
        gpu computing and maybe compute them after the crawling

Find noun of interest
Get next verbs (Phrase limit). Are they refering to it?
Then list all data (end phrase from verb. Drop chinking)

## This one could be done on-crawling

Example:
    Noun of interest -> data

    data:
        is hard to get
        is an example

        has something

        wants to get analyzed by me


## classify by object, then compare

Even further: Check veracity

Classify phrases (positive/negative) about the fact/statements
Lemmatize phrases (Optional, verb tenses may change meaning as for
                    something was wrong but now is right
                    )
Find phrases related
Make statistics

Example:
    Relatable information -> data, be, hard, get

    data be hard get:
        data is hard to get (positive)
        data is easy to get (positive)
        data is not hard to get (negative)

    data is hard to get (0.33) -> False


## Teach ai to recognize users then match statements to users

by html nodes (may need to save html so that it can be performed offline)
"""

def main():
    with open("test.txt",'r',encoding="utf-8") as f:
        text = f.read()

    if(False):
        sentences = array(split_into_sentences(text,True))
        if(not len(sentences)): print("Nothing found"); exit(-1)

        tags = pos_tag_sents(map(word_tokenize, sentences))

        lemmatized = lemmatize_sents(deepcopy(tags)) #Only for aesthetics reasons

        chunker = RegexpParser( "AC: {(<CD>?<TO|IN>?<CD>)+}\n "
                                    "AN: {(<NPP>+<DT|NPP|JJ>*)+}\n "
                                        "}<DT>+{\n "
                                    "PH: {<[B-Z]+>+}\n "
                                        "}<DT|CC|PRP|EX|WDT>+{"
                                    ) 
        chunked = list(chunker.parse_sents(lemmatized))

        droped = setup_search_structure(chunked,tuple)

        if(True):
            num_print = input("Full data of:[None] ")
            if(num_print):
                num_print = int(num_print)
                print()

                for num_print in range(num_print,num_print+10):
                    print(sentences[num_print])
                    print()
                    print(tags[num_print])
                    print()
                    print(lemmatized[num_print])
                    print()
                    #chunks = ne_chunk_sents(tags)
                    #iob = [tree2conlltags(chunk) for chunk in chunks]
                    #iob = tree2conlltags(chunks)
                    #print(iob[num_print])
                    #print()
                    #tree = [conlltags2tree(i) for i in iob]
                    #print(tree[num_print])
                    #print()
                    #"NP: {<IN|TO>?((<IN>?<DT>?<JJ.?>*<CD>?<NN.*>+<POS>?)+<CD>?<FW>?)+}\n "
                    #"VP: {((<WP>?<PRP>?<MD>?<VB.?>?<JJ>*<TO>?<VB.?>+<RB>*(<JJ>*<TO>?)*)+<CC>?)+}\n "
                                            
                    
                    print(chunked[num_print])
                    print("\n###\n")
                    
                    print(droped[0][num_print])
                    print()

                    if(input(f"({num_print}) ?> ")): break
        
    ### Search params
    to_search = input("Search: ") or "work"
    tag = {'1':'n','2':'v','3':'a','4':'r'}.get(input(f"\nWhat '{to_search}'?\n"
                                            "[1]: Noun\n"
                                            "[2]: Verb\n"
                                            "[3]: Adjective\n"
                                            "[4]: Adverb\n\n"
                                            "> "),None)
    syn = 'y' in input("\nFind related words too? ").lower()
    exact = 'y' in input("\nFind exact word? ").lower()
    print()

    _,ph_num_ls,sentences = analize_text(text,exact_words=exact)
    num = 1000000
    num2 = 10

    if(to_search):
        if(syn):
            w_rel = words_related(to_search, tag)
        else:
            w_rel = to_search
            
        ph_nums = find(w_rel, ph_num_ls)

    print()

    if(not len(ph_nums)): print(f"{to_search} not in text."); exit(0)

    if(False):
        print(f"Looking for \"{to_search}\" {num} times...\n")

        print(timeit.timeit("find(w_rel, ph_num_ls)",number=num,globals={**globals(),**locals()}),end=' seconds\n\n')

    if(False):
        print(f"{num2} times text setup...\n")
        print(timeit.timeit("analize_text(text)",number=num2, globals={**globals(),**locals()}),end=' seconds \n')

    if("y" in input("Show found instances?[No] ")):
        from colorama import init as color_init
        color_init()

        print()
        if(not ph_nums is None): # Unnecessary, but clean
            for ph in ph_nums:
                print(_color_sent(sentences[ph], w_rel))
                print()
        else: print("You did not specify any search param")
    

    #nd_phase_chunker = RegexpParser("NICE: {<NP>*<VP>+<NP>+}")
    #final = nd_phase_chunker.parse_sents(chunked) 
    #print(list(final)[num_print])

    #print(timeit.timeit("split_into_sentences(text)",number=1000, globals={**locals(),**globals()})) 
    # 2.779585732000214
    #print(timeit.timeit("sent_tokenize(text)",number=1000,setup="from nltk.tokenize import sent_tokenize", globals=locals()))
    # 25.541579458000342

    #print(timeit.timeit("[conllstr2tree(s) for s in sentences]",number=10, setup="from nltk.chunk import conllstr2tree", globals=locals()))
    # ValueError
    #print(timeit.timeit("[ieerstr2tree(s) for s in sentences]",number=1000, setup="from nltk.chunk import ieerstr2tree", globals=locals()))
    # 29.225451889000396

def analize_text(text:str, *, exact_words:bool=False) -> tuple:
    sentences = array(split_into_sentences(text,True))
    if(not len(sentences)): print("Nothing found"); return []

    tags = pos_tag_sents(map(word_tokenize, sentences))

    if(not exact_words):
        lemmatized = lemmatize_sents(tags)
    else:
        lemmatized = tags

    chunker = RegexpParser( "AC: {(<CD>?<TO|IN>?<CD>)+}\n "
                            "AN: {(<NPP>+<DT|NPP|JJ>*)+}\n "
                                "}<DT>+{\n "
                            "PH: {<[B-Z]+>+}\n "
                                "}<DT|CC|PRP|EX|WDT>+{"
                            ) 
                            
    chunked = list(chunker.parse_sents(lemmatized))

    return (*setup_search_structure(chunked,tuple),sentences)

def find(to_find:list, index_dict:dict) -> list:
    if(isinstance(to_find,str)): return index_dict.get(to_find, [])

    result = set()
    for word in to_find: result.update(index_dict.get(word, []))

    return list(result)

def words_related(to_find:str, tag:str=None, keep_only:int=10) -> list:
    lemmatizer = WordNetLemmatizer()
    
    if(tag is None): tag = pos_tag([to_find])[0][1][0].lower()

    try:
        st_lemma = wordnet.synset(f"{to_find}.{tag}.01")
    except WordNetError:
        st_lemma = wordnet.synset(f"{lemmatizer.lemmatize(to_find, tag)}.{tag}.01")

    by_similarity = next(zip(*sorted(((lemma,
                        st_lemma.wup_similarity(lemma)*st_lemma.path_similarity(lemma))
                        for lemma in wordnet.synsets(to_find) 
                        if not st_lemma.wup_similarity(lemma) is None),
                        reverse=True, key=itemgetter(1))))
    filtered = {to_find:to_find}
    for lemma in by_similarity:
        tag = lemma.pos()
        if tag in ['a','v','n','r']:
            for name in lemma.lemma_names():
                name = lemmatizer.lemmatize(name, tag)
                filtered[name] = name

    filtered = list(filtered.keys())
   
    if(not keep_only is None): filtered = filtered[:keep_only]

    print(f"Searching for the words {', '.join(filtered)}")
    return filtered 

def split_into_sentences(text:str, join_:bool=False, reg_filter:"regex"=None) -> list:
    text = f" {text} "
    if join_: text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub(f"\s{alphabets}[.] "," \\1<prd> ",text)
    text = re.sub(f"{acronyms} {starters}","\\1<stop> \\2",text)
    text = re.sub(f"{alphabets}[.]{alphabets}[.]{alphabets}[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(f"{alphabets}[.]{alphabets}[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(f" {suffixes}[.] {starters}"," \\1<stop> \\2",text)
    text = re.sub(f" {suffixes}[.]"," \\1<prd>",text)
    text = re.sub(f" {alphabets}[.]"," \\1<prd>",text)
    text = re.sub(r"\[|\]|-(?=[0-9])"," ", text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>").replace("?","?<stop>").replace("!","!<stop>").replace("\n","\n<stop>").replace("<prd>",".")
    if not reg_filter is None:
        return [s.strip() for s in text.split("<stop>")[:-1] if any(re.findall(reg_filter, s, re.IGNORECASE))]
    return [s.strip() for s in text.split("<stop>")[:-1]]

def lemmatize_sents(tagged_sentences:list) -> list:
    lemmatizer = WordNetLemmatizer()
    for sentence in tagged_sentences:
        for num, (word, tag) in enumerate(sentence):
            pos_tag = tag[0].lower()
            if(pos_tag in ['n','a','r','v']):
                sentence[num] = (lemmatizer.lemmatize(word,pos=pos_tag), tag)

    return tagged_sentences

def setup_search_structure(sentences:list, drop_type:type=tuple) -> "Tuple[list,dict]":
    result = set()
    by_word = defaultdict(list)
    custom_groups = ["AC","AN"]

    for s_num, sent in enumerate(sentences):
        sent_by_pos = defaultdict(set)
        for group in sent:
            if(type(group) is drop_type): continue
            
            if(group._label in custom_groups):
                for word,tag in group:
                    word = word.lower()

                    sent_by_pos[tag[:2]].add(word)
                    sent_by_pos[group._label].add(word)

                    by_word[word.lower()].append(s_num)
            else:
                for word,tag in group:
                    word = word.lower()

                    sent_by_pos[tag[:2]].add(word)
                    
                    by_word[word.lower()].append(s_num)

        result.update(sent_by_pos)
        
    return (list(result),by_word)

def _color_sent(sents:list, words:list, color:str='green'):
    if(isinstance(words, str)): words = [words]

    words = [f" {w.strip()} " for w in words]

    if(isinstance(sents, str)): 
        for word in words:
            sents.replace(word, colored(word, color))
        return sents

    for num,sent in enumerate(sents):
        for word in words:
            sent = sent.replace(word, colored(word, color))
        sents[num] = sent

    return sents

if __name__ == "__main__":
    main()
