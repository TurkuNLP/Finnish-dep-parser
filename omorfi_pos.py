# -*- coding: utf-8 -*-

""" Two functions are relevant here:

*** lemma,tags=analyze_reading(reading)

returns the lemma and the list of tags of the last compound member's last full derivation (i.e. derivation which produces POS)

*** analyze_taglist(tags,retForm) where retForm is one of

RET_DICT -- Return dictionary (cat:tag)
RET_LIST -- Return list (tag,tag,None,tag,None,tag,...) for every possible category
RET_POS_FEAT -- Return a tuple( POS, tagString ) to be put into CoNLL-style data

Recognized categories:

[u'POS', u'SUBCAT', u'NUM', u'CASE', u'POSS', u'PRS', u'VOICE', u'TENSE', u'MOOD', u'NEG', u'PCP', u'INF', u'CLIT', u'DRV', u'CMP', u'CASECHANGE', u'OTHER']

"""

# The raw list below produced like so:
# cat ~/omorfi-20110505/src/tagsets/finntreebank.relabel |-Z]+)=.*?\]\s+(.*)/$1 $2/' | grep -v BOUNDARY |  sort | uniq | tr '\n' ','
#
# Hand edits:
# PCP <Neg><Pcp> to PCP <Pcp>, <Neg> is there already as subcat
# POS <Prop> removed, <Prop> is a SUBCAT
# SUBCAT <Pass> removed, <Pass> is Voice
# SUBCAT <Act> removed, <Act> is Voice
# POS <C> added because CC/CS are subcats, it is not emmited by Omorfi, so we generate it in code
#  - CC and CS subcats are wiped because they have elementary mistakes in Omorfi
# SUBCAT <Sent> added for punct
# SUBCAT <Para> added (and will generate Punct for it)
#
# POS <Null> added to support TDT's null tokens

import re
import codecs
import sys
import os
import cPickle as pickle
import traceback

import unicodedata as udata

SCRIPTDIR=os.path.dirname(os.path.abspath(__file__))
print >> sys.stderr, "Loading Omorfi transducer in Java-as-subprocess inside Python implementation"
import omorfi_wrapper
OmorTransducer=omorfi_wrapper.OmorfiWrapper(os.path.join(SCRIPTDIR,"model/morphology.finntreebank.hfstol"))


import resolve_readings

try:
    import readline #if available, use raw_input with readline
except:
    pass

# try:
#     import hfst_lookup
#     OmorTransducer=hfst_lookup.Transducer("/opt/omorfi-svn/share/hfst/fi/morphology.finntreebank.hfstol")
# except:
#     print >> sys.stderr, "Couldn't load Omorfi transducer. On-the-fly lookup will not work."
#     traceback.print_exc()
#     OmorTransducer=None

SCRIPTDIR=os.path.dirname(os.path.abspath(__file__))

index=None #Index of cached Omorfi-analyzed tokens from TDT. Loaded from omorfi_index.pickle later when needed for the first time in omorfi_tag_token().

raw_tag_information=u'CASE <Abe>,CASE <Abl>,CASE <Acc>,CASE <Ade>,CASE <All>,CASECHANGE <cap>,CASECHANGE <Cap>,CASECHANGE <CAP>,CASECHANGE <Up>,CASE <Com>,CASE <Dis>,CASE <Ela>,CASE <Ess>,CASE <Gen>,CASE <Ill>,CASE <Ine>,CASE <Ins>,CASE <Lat>,CASE <Nom>,CASE <Par>,CASE <Prl>,CASE <Sti>,CASE <Tra>,CLIT <Foc_han>,CLIT <Foc_ka>,CLIT <Foc_kaan>,CLIT <Foc_kin>,CLIT <Foc_pa>,CLIT <Foc_s>,CLIT <Qst>,CMP <Comp>,CMP <Pos>,CMP <Superl>,DRV <Der_inen>,DRV <Der_ja>,DRV <Der_lainen>,DRV <Der_llinen>,DRV <Der_maisilla>,DRV <Der_minen>,DRV <Der_oi>,DRV <Der_sti>,DRV <Der_tar>,DRV <Der_tattaa>,DRV <Der_tatuttaa>,DRV <Der_ton>,DRV <Der_tse>,DRV <Der_ttaa>,DRV <Der_ttain>,DRV <Der_u>,DRV <Der_vs>,INF <Inf1>,INF <Inf2>,INF <Inf3>,INF <Inf5>,MOOD <Cond>,MOOD <Eve>,MOOD <Imprt>,MOOD <Ind>,MOOD <Opt>,MOOD <Pot>,NEG <ConNeg>,NUM <Pl>,NUM <Sg>,PCP <AgPcp>,PCP <Pcp>,PCP <PrfPrc>,PCP <PrsPrc>,POS <A>,POS <Adp>,POS <Adv>,POS <C>,POS <Interj>,POS <N>,POS <Null>,POS <Num>,POS <Pcle>,POS <Pron>,POS <Punct>,POSS <PxPl1>,POSS <PxPl2>,POSS <PxPl3>,POSS <PxSg1>,POSS <PxSg2>,POSS <PxSg3>,POSS <Px3>,POS <V>,PRS <Pe4>,PRS <Pl1>,PRS <Pl2>,PRS <Pl3>,PRS <Sg1>,PRS <Sg2>,PRS <Sg3>,SUBCAT <Abbr>,SUBCAT <Acro>,SUBCAT <Approx>,SUBCAT <Card>,SUBCAT <CC>,SUBCAT <CS>,SUBCAT <Dem>,SUBCAT <Indef>,SUBCAT <Interr>,SUBCAT <Neg>,SUBCAT <Ord>,SUBCAT <Para>,SUBCAT <Pers>,SUBCAT <Pfx>,SUBCAT <Po>,SUBCAT <Pr>,SUBCAT <Prop>,SUBCAT <Qnt>,SUBCAT <Real>,SUBCAT <Recipr>,SUBCAT <Refl>,SUBCAT <Rel>,SUBCAT <Sent>,SUBCAT <Sfx>,TENSE <Prs>,TENSE <Prt>,VOICE <Act>,VOICE <Pass>,OTHER <Typo>,OTHER <Cllq>,POS <Trash>,POS <Symb>,POS <Foreign>,OTHER <UNK>'

tag_cat_dict={} #key: tag value: category
cat_tag_dict={} #key: category value: list of tags
tag_set=set() #set of all tags
cat_set=set() #set of all categories

#a semi-random ordering on categories to ensure consistent results

cat_list=[u'POS', u'SUBCAT', u'NUM', u'CASE', u'POSS', u'PRS', u'VOICE', u'TENSE', u'MOOD', u'NEG', u'PCP', u'INF', u'CLIT', u'DRV', u'CMP', u'CASECHANGE', u'OTHER']

cat2idx={} #{category:index in cat_list}
for idx,cat in enumerate(cat_list):
    cat2idx[cat]=idx

for cat_tag in raw_tag_information.split(u","):
    cat,tag=cat_tag.split()
    assert tag[0]==u"<" and tag[-1]==u">"
    tag=tag[1:-1] #strip < >
    tag_set.add(tag)
    cat_set.add(cat)
    assert tag not in tag_cat_dict, tag
    tag_cat_dict[tag]=cat
    cat_tag_dict.setdefault(cat,[]).append(tag)


class CompoundElement (object):

    pass

#print cat_tag_dict[u"POS"]
#sys.exit()    

####################################################
####### Additional readings to inject into Omorfi's output are defined here


#token additional_reading
#add more as needed, but never look into the official test set!
additionalReadingDefs=u"""
esimerkiksi esimerkiksi<Adv>
Esimerkiksi esimerkiksi<Adv><Up>
mm. mm<Adv>
Mm. mm<Adv><Up>
"""

additionalReadings={} #{token:set of readings}
for line in additionalReadingDefs.split(u"\n"):
    line=line.strip()
    if not line:
        continue
    token,r=line.split()
    additionalReadings.setdefault(token,set()).add(r)

####################################################


tagRe=re.compile(ur'<([^<>]+)>',re.U)
#Note: use analyze_tagset below!
def _raw_analyze_taglist(tags):
    """tags can be a string like '<N><Nom><Sg>' or anything iterable. Returns a dictionary {cat:tag} for all categories that have a tag. Brackets get stripped."""
    if isinstance(tags,str):
        tags=unicode(tags,"utf-8") #enforce unicode, wherever you are
    if isinstance(tags,unicode):
        tags=[match.group(1) for match in tagRe.finditer(tags)]
    #now tags is an iterable which gives the individual tags
    res={} #key: cat value: list of tags
    for tag in tags:
        cat=tag_cat_dict[tag]
        res.setdefault(cat,[]).append(tag)

    for cat,tags in list(res.iteritems()):
        if cat in (u"CLIT",u"DRV",u"OTHER") and len(tags)>1:
            tags[:]=[u"+".join(tags)]
        assert len(tags)==1, (cat,tags)
        res[cat]=tags[0] #turn the lists into strings, so we have one value per category
    if u"POS" not in res:
        subcat=res.get(u"SUBCAT",None)
        if subcat in (u"CC",u"CS"):
            res[u"POS"]=u"C" #Omorfi fails to generate POS for CC&CS
        elif subcat in (u"Para",):
            res[u"POS"]=u"Punct"
    if not u"POS" in res:
        #happens with sun and sunkin at least, maybe others?
        raise ValueError((u"There is no POS among %s, doesn't look like a valid reading."%(u"".join(tags))).encode("utf-8"))
    return res

#Return modes:
RET_DICT=0 #Return dictionary (cat:tag)
RET_LIST=1 #Return list [tag,tag,None,tag,None,tag,...] for every category in cat_list (see above)
RET_TUPLE=4 #Return tuple (tag,tag,None,tag,None,tag,...) for every category in cat_list (see above)
RET_POS_FEAT=2 #Return a tuple( POS, tagString ) to be put into CoNLL-style data
#Raises ValueError if something goes haywire
def analyze_taglist(tags,retForm=RET_LIST):
    ct_dict=_raw_analyze_taglist(tags)
    if retForm==RET_DICT:
        return ct_dict
    elif retForm==RET_LIST:
        return [ct_dict.get(cat,None) for cat in cat_list]
    elif retForm==RET_TUPLE:
        return tuple(analyze_taglist(tags,RET_LIST))
    elif retForm==RET_POS_FEAT:
        pos=ct_dict[u"POS"]
        tagString=u"|".join(cat+u":"+ct_dict[cat] for cat in cat_list if cat!=u"POS" and cat in ct_dict)
        return pos,tagString

UNIQUE_NOLEMMA=0
UNIQUE=1
def unique_readings(lemma_tags,form=UNIQUE):
    #in: list of (lemma,taglist) out: list of (lemma,taglist)
    s=set()
    if form==UNIQUE_NOLEMMA: #Return None, taglist
        for lemma,tags in lemma_tags:
            tagTuple=analyze_taglist(tags,RET_TUPLE)
            s.add(tagTuple)
        return [(None,t) for t in s]
    elif form==UNIQUE:
        for lemma,tags in lemma_tags:
            tagTuple=analyze_taglist(tags,RET_TUPLE)
            s.add((lemma,tagTuple))
        return list(s)

#Returns the lemma and list of readings which you can then feed into analyze_tagset
#Raises ValueError if something goes haywire
def analyze_reading(reading):
    if isinstance(reading,str):
        reading=unicode(reading,"utf-8")
    if reading.endswith(u"+?"):
        return reading[:-2],[]
    compoundParts=reading.split(u"+") #TODO: what if "+" is part of the token? ;)
    lemma=[]
    for compoundPart in compoundParts:
        if compoundPart.startswith(u"#") and len(compoundPart)>1 and compoundPart!=u"#<Punct>":
            compoundPart=compoundPart[1:]
        firstTag=tagRe.search(compoundPart)
        if firstTag==None:
            lemma.append(compoundPart)
        else:
            lemma.append(compoundPart[:firstTag.start()])
    lemma=u"|".join(lemma)
    #compoundPart is now set to the last compoundPart
    tags=[match.group(1) for match in tagRe.finditer(compoundPart)]
    #Now I will yet need to get the actual tagset, sans derivations
    foundPOS=False
    for idx in range(len(tags)-1,-1,-1):
        cat=tag_cat_dict[tags[idx]]
        if cat==u"POS":
            assert foundPOS==False #this would mean two POS tags in one reading, not masked by a Deriv
            foundPOS=True
        elif cat==u"DRV":
            if foundPOS: #looks like I'm done here!
                break
            else:
                if tags[idx] not in (u"Der_u",u"Der_inen"): #checked these and they're okay
                    print >> sys.stderr, tags[idx], "is a deriv before POS in", reading.encode("utf-8")
        elif foundPOS:
            print >> sys.stderr, tags[idx], "is a tag ahead of POS in", reading.encode("utf-8")
    tags=tags[idx:]
    return lemma, tags


############## ON-THE-FLY TAGGING OF STUFF ###############################
#Relies on the omorfi index now, so only works for tokens present in TDT
#
# the index holds the readings cleaned-up by Jenna, so once that code is ported to here, these functions can be
# rewritten so as to use the on-the-fly tagging and we can retire the omorfi-index as such

def init_index():
    global index
    indexFileName=os.path.join(SCRIPTDIR,"omorfi-index.pickle")
    indexFile=open(indexFileName,"rb")
    index=pickle.load(indexFile)
    indexFile.close()
    #Done

def omorfi_tag_token(token): #Token() from tree
    global index #key: wordform value: list of (lemma, taglist, reading)

    if index==None:
        init_index()

    token.posTags=[] #Wipe these
    readings=index.get(token.text,[])
    for lemma,tags,whole_reading in readings:
        try:
            taglist=analyze_taglist(tags,RET_LIST)
        except ValueError:
            print >> sys.stderr, "Odd analysis, skipping:", whole_reading.encode("utf-8")
            continue
        token.posTags.append([None,lemma,u" ".join(t for t in tags if t),taglist])
    #Done

def omorfi_tag_tset(tSet):
    for dTree in tSet:
        for token in dTree.tokens:
            omorfi_tag_token(token)
    #Done

capRe=re.compile(ur"<(Cap|cap|CAP)>",re.U) #The @....@ tags in the transducer output, want to get rid of them
pxRe=re.compile(ur"<Px(Sg|Pl)3>",re.U)
def omorfi_postprocess(token,readings):
    global additionalReadings #See at the beginning
    #The raw output of Omorfi is fed through here, adding additional readings, doing things like <CC> & <CS>, etc
    #Pcle2Adv
    readings=[r.replace(u"Pcle",u"Adv") for r in readings]
    #Px3
    readings=[pxRe.sub(u"<Px3>",r) for r in readings]
    readings=[capRe.sub(u"",r) for r in readings] #Remove cap if any
    if is_up(token):
        readings=[r+u"<Up>" for r in readings]
    res=set(readings)
    for r in readings:
        res.add(r.replace(u"<CC>",u"<CS>"))
        res.add(r.replace(u"<CS>",u"<CC>"))
        if token in additionalReadings:
            res.update(additionalReadings[token])
    return sorted(res)

atRe=re.compile(ur"@[A-Za-z.]+@",re.U) #The @....@ tags in the transducer output, want to get rid of them
def omorfi_lookup(token):
    #Bypass punctuation and digits:
    if is_punct(token):
        return [token+u"<Punct>"]
    if is_num(token):
        return [token+u"<Num>"]
    #Returns all readings for the token, running Omorfi on-the-fly
    global OmorTransducer
    if OmorTransducer==None:
        raise ValueError("Omorfi is not loaded correctly, cannot do lookup")
    #r is returned as utf-8 byte string, so first decode to Unicode, then erase the @[A-Za-z.]+@ tags
    readings=[atRe.sub(u"",unicode(r,"utf-8")) for r,score in OmorTransducer.lookup(token.encode("utf-8"))]
    s=omorfi_postprocess(token,readings)
    return resolve_readings.main(s)

######### SUPPORT FUNCTIONS FOR POS-TAGGING ########################

def is_punct(s):
    """s is a unicode string"""
    for c in s:
        #Unicode data category for the character: see http://www.fileformat.info/info/unicode/category/index.htm
        cat=udata.category(c)
        #P stands for punctuation, Sm for mathematical symbols, Sk for modifier symbols
        if not (cat.startswith(u"P") or cat==u"Sm" or cat==u"Sk"): #none of the others? Not a punctuation
            return False
    return True #all characters in the string were punctuation, so the string is punctuation

numRe=re.compile(u"^[0-9.,:\u2012\u2013\u2014\u2015\u2053~-]+$",re.U) #The unicode chars are various dashes
def is_num(s):
    if numRe.match(s):
        return True
    else:
        return False

def is_up(s):
    """s is a unicode string"""
    cat=udata.category(s[0])
    if cat in (u"Lt",u"Lu"):
        return True
    else:
        return False


def tagListDistance(tagList1,tagList2,ignoreCategories=set()):
    score=0
    for catIDX,cat in enumerate(cat_list):
        if cat in ignoreCategories:
            continue
        if tagList1[catIDX]==tagList2[catIDX]:
            if catIDX==0:
                score+=5 #weigh POS higher
            else:
                score+=1
    return score #the higher, the more similar

def cand_cmp((lemma1,taglist1,dist1),(lemma2,taglist2,dist2)):
    if dist1!=dist2:
        return -cmp(dist1,dist2) #the higher, the better
    #Same-distance, make a guess on lemma
    return cmp(lemma1.count(u"|"),lemma2.count(u"|")) #The lower, the better

def omorfi_reading_compatible_with(token,plemma,ptaglist):
    #Given a token, a predicted lemma, and predicted taglist (list of cats), give an omorfi reading most like the predicted one. plemma can be None as well, but will be returned as None if the tokens is not in omorfi!
    omorfiRawReadings=omorfi_lookup(token)
    if not omorfiRawReadings:
        ptaglist[cat2idx[u"OTHER"]]=u"UNK" #mark as guess
        return plemma, ptaglist
    #Okay, we have something to work with
    candidates=[]
    for r in omorfiRawReadings:
        try:
            lemma,tags=analyze_reading(r)
            taglist=analyze_taglist(tags,RET_LIST)
        except:
            #Broken reading from Omorfi, ignore
            continue
        candidates.append((lemma,taglist,tagListDistance(ptaglist,taglist)))
    candidates.sort(cmp=cand_cmp)
    return candidates[0][0],candidates[0][1] #lemma, taglist

#####################################################################
    
##########  HunPOS related functions #####################

upRe=re.compile(ur"^[A-ZÅÄÖ]")
def fill_ortho(token,tagList):
    if upRe.match(token):
        tagList[cat2idx["CASECHANGE"]]=u"Up"
    else:
        tagList[cat2idx["CASECHANGE"]]=None

def hun_possibletags(token):
    res=set()
    for r in omorfi_lookup(token):
        try:
            lemma,taglist=analyze_reading(r)
            fullTagList=analyze_taglist(taglist)
            res.add(hun_taglist2tagstring(fullTagList))
        except ValueError:
            print >> sys.stderr, "Skipping lemma:", lemma.encode("utf-8")
    return list(res)

def hun_taglist2tagstring(tagList):
    hunposCats=(u'POS', u'SUBCAT', u'NUM', u'CASE', u'PRS', u'VOICE', u'TENSE', u'MOOD', u'NEG', u'PCP', u'INF', u'CLIT', u'CMP')
    tags=[]
    for cat in hunposCats:
        tag=tagList[cat2idx[cat]]
        if tag!=None:
            tags.append(cat+u"_"+tag)
    return u"|".join(tags)

def hun_tagstring2taglist(tagString):
    tagList=[None for x in range(len(cat_list))]
    for cat_tag in tagString.split(u"|"):
        cat,tag=cat_tag.split(u"_",1)
        tagList[cat2idx[cat]]=tag
    return tagList

def hun_tag2omorfi(token,tagString):
    """Returns the Omorfi reading best matching the given hunpos tag"""
    tagList=hun_tagstring2taglist(tagString)
    lemma,new_taglist=omorfi_reading_compatible_with(token,token,tagList)
    return lemma,new_taglist

###########################################################


if __name__=="__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="python omorfi_pos.py [options]")
    parser.add_option("-n", "--no-interactive", dest="interactive", action="store_false", default=True, help="Don't use the interactive prompt, read the data from stdin")
    (options, args) = parser.parse_args()
    
    

    if options.interactive:
        while True:
            try:
                s = raw_input('token> ')
            except EOFError:
                print
                break
            readings=omorfi_lookup(unicode(s,"utf-8"))
            if not readings:
                print "--unrecognized--"
                print
            else:
                for r in readings:
                    print (u"-- "+r).encode("utf-8")
                print
    else:
        for token in sys.stdin:
            token=unicode(token,"utf-8").strip()
            if not token:
                continue
            readings=omorfi_lookup(token)
            if not readings:
                readings.append(u"--unrecognized--")
            for r in readings:
                print (token+u"\t"+r).encode("utf-8")
            print
