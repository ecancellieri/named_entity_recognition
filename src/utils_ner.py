import re
import pyap
import spacy
import numpy as np
import pandas as pd

spacy_nlp = spacy.load('en_core_web_lg')

def check_address(s):
    # uses "pyap" library to check if the string is an address
    # (https://pypi.org/project/pyap/)
    nations = ['US', 'CA' , 'GB']
    for nation in nations:
        if pyap.parse(s, country=nation) != []:
            return s+' is: Address'

def check_serial(s):
    # uses regular expressions to check
    # 4 different types of serial numbers
    regexes = ["[a-zA-Z]{4}\d{2}E",
               "\w{4}-\w{4}-\w{4}",
               "^(?:\w*[0-9]\w* ){2}",
               "[0-9]{4}/[0-9]{4}/[0-9]{4}"]
    for regex in regexes:
        if re.match(regex, s):
            return s+' is: Serial number'

def get_category(s):
    # given a string it finds its category checking in order:
    # Address, Serisl, Entity, Location, Goods. Assign "Unknown" otherwise
    if check_address(s):
        return 'Address'
    if check_serial(s):
        return 'Serial'
    doc = spacy_nlp(str.title(s))
    if len(doc.ents) != 0 and set([ent.label_ for ent in doc.ents]).issubset(['ORG']):
        return 'Entity'
    if len(doc.ents) != 0 and set([ent.label_ for ent in doc.ents]).issubset(['GPE', 'LOC']):
        return 'Location'
    doc = spacy_nlp(s.lower())
    if set([t.pos_ for t in doc]).issubset(['ADJ', 'NOUN']):
        return 'Goods'
    return 'Unknown'

def find_closest_groupid_and_similarity(doc, dfin):
    # uses spacy doc-to-doc similarity function.
    # takes one string and compare it to all the
    # strings in the same category
    maxsim = 0
    for s in dfin['String'].values:
        similarity = doc.similarity(spacy_nlp(s))
        if similarity > maxsim:
            maxsim  = similarity
            groupid = dfin[dfin['String'] == s]['GroupId'].unique()[0]
    return maxsim, groupid

def find_groupid_or_update_counter(string, dfin, idcounter):
    # for a given doc checks if it belongs to a new category
    # otherwise it checks if the doc is similar to another one
    # and assigns a groupid
    if len(dfin) == 0:
        idcounter   = idcounter + 1
        aux_groupid = idcounter
    else:
        max_similarity, aux_groupid = find_closest_groupid_and_similarity(spacy_nlp(string), dfin)
        if max_similarity < 0.8:
            idcounter   = idcounter + 1
            aux_groupid = idcounter
    return idcounter, aux_groupid