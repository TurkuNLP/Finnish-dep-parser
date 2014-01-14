# -*- coding: utf-8 -*-
##TODO: Warning: if there are words with +-character and if that word gets more than one reading, I don't know what happens.
import re
import sys
import omorfi_pos
OmorTransducer=omorfi_pos.OmorTransducer #hfst_lookup.Transducer("/opt/omorfi-svn/share/hfst/fi/generation.finntreebank.hfstol")

atRe=re.compile(ur"@[A-Za-z.]+@",re.U) #The @....@ tags in the transducer output, want to get rid of them

############################################################################################
# SUPPORT FUNCTIONS:

#True, if one or more readings is compound
def isCompound(readings):
    for r in readings:
        if u"<Cmpnd>" in r: return True
        elif u"+#" in r: return True     
    return False

#True, if one or more readings is derivation
def isDerivation(readings):
    for r in readings:
        if u"<Der_" in r: return True
    return False

#Takes one reading and returns the reading of last member if compound and reading without lemma if normal
def give_last_one(r):
    if u"+" in r:
        columns=r.split(u"+")
        ending=columns[len(columns)-1]
    else: ending=r
    index=0
    for char in ending:
        if char!=u"<": index+=1
        else: break
    ending=ending[index:len(ending)]
    return ending

#Makes all necessary der changes to reading r
def der_changes(r):
    regex="(<Der_[A-Za-z]+>)"
    if u"<Der_" in r:
        m=re.findall(regex,r)
        Der=m[len(m)-1]
        columns=r.split(Der)
        r=columns[len(columns)-1]
        if Der==u"<Der_u>": r=u"<N>"+r #because of missing <N>-tag
        elif Der==u"<Der_llinen>": r=re.sub(u"<A>",u"<A><Pos>",r) #because of missing <Pos>-tag
        elif Der==u"<Der_ton>": r=re.sub(u"<A>",u"<A><Pos>",r)
        elif Der==u"<Der_tse>": r=re.sub(u"<Adv><Prl>",u"<Adv>",r)
        elif Der==u"<Der_ttain>": r=re.sub(u"<Adv><Dis>",u"<Adv>",r)
        elif Der==u"<Der_sti>": r=re.sub(u"<Adv><Comp>",u"<Adv>",r)
        if u"[DRV=UUS]" in r: r=re.sub(u"\[DRV=UUS\]",u"",r) #deletes DRV=UUS-tag
    r=re.sub(u"<cap>",u"",r)
    r=re.sub(u"<Cap>",u"",r)
    r=re.sub(u"<CAP>",u"",r)
    return r
    
#Takes one COMPOUND-reading, returns lemma (like "raja jääkäri pataljoona")
def give_cmpnd_lemma(r):
    lemma=u""
    columns=r.split(u"+")
    for col in columns:
        if u"<" in col:
            c=col.split(u"<")
            lemma+=c[0]+u" "
        else: lemma+=col+u" "
    lemma=lemma.strip()
    lemma=re.sub(u"#",u"",lemma)
    return lemma
##############################################################################################
# COMPARING FUNCTIONS

#Takes two der-readings, returns True if considered as same
def der_vs_der(r1,r2):
    regex="(<Der_[A-Za-z]+>)"
    m1=re.findall(regex,r1)
    m2=re.findall(regex,r2)
    if len(m1)>len(m2):
        Der=m1[0]
        columns=r1.split(Der)
        if len(columns)==2: r1_ending=columns[1]
        else: return False
        r2_ending=give_last_one(r2)
        if r1_ending==r2_ending: return True
        else: return False   
    elif len(r2)>len(r1):
        Der=m2[0]
        columns=r2.split(Der)
        if len(columns)==2: r2_ending=columns[1]
        else: return False
        r1_ending=give_last_one(r1)
        if r2_ending==r1_ending: return True
        else: return False
    else:
        cols=r1.split(u"<")
        lemma1=cols[0].lower()
        cols=r2.split(u"<")
        lemma2=cols[0].lower()
        if lemma1==lemma2: return True
        else: return False 

#Takes two readings, checks if the readings of last members are same (this one just skips lemmas)
def isSameAnalysis(r1,r2):
    r1_ending=give_last_one(r1)
    r2_ending=give_last_one(r2)
    r1_ending=der_changes(r1_ending)
    r2_ending=der_changes(r2_ending)            
    if r1_ending==r2_ending: return True
    else: return False
        
#Splits compounds to parts and compares those, returns True, if all parts match
def split_compounds(r1,r2):
    parts1=r1.split(u"+")
    parts2=r2.split(u"+")              
    if len(parts1)==len(parts2):
        for i in range(0,len(parts1)):
            part1=parts1[i]
            part1=re.sub(u"#",u"",part1)
            part1=re.sub(u"<Cmpnd>",u"",part1)
            part2=parts2[i]
            part2=re.sub(u"#",u"",part2)
            part2=re.sub(u"<Cmpnd>",u"",part2)        
            if u"<" in part1 and u"<" in part2: #both have reading, no talvi+#uni cases
                if u"<Der_" in part1 or u"<Der_" in part2: #if other have der-tag check also readings
                    if isSameLemma(part1,part2)==False or isSameAnalysis(part1,part2)==False: return False
                else:
                    if not isSameLemma(part1,part2): return False
            else: # other (or both) doesn't have tags, use omorfi generation if needed
                if u"<" not in part1 and u"<" not in part2: #both #-tag compounds
                    if part1 != part2: return False
                elif u"<" in part1: #part1 has reading
                    cols=part1.split(u"<")
                    lemma1=cols[0]
                    if lemma1==part2: continue #lemma is same, continue to next part
                    #different lemma, try omorfi generation
                    if OmorTransducer==None: raise ValueError("Omorfi is not loaded correctly, cannot do lookup")
                    wordforms=[atRe.sub(u"",unicode(r,"utf-8")) for r,score in OmorTransducer.lookup(part1.encode("utf-8"))]
                    match=False
                    for form in wordforms:
                        form=re.sub(u"-",u"",form)
                        form=re.sub(u"\u2010",u"",form)
                        if form==part2:
                            match=True
                            break
                    if not match: return False #no match using omorfi generation
                else:#same but part2 has reading
                    cols=part2.split(u"<")
                    lemma2=cols[0]
                    if lemma2==part1: continue
                    if OmorTransducer==None: raise ValueError("Omorfi is not loaded correctly, cannot do lookup")
                    wordforms=[atRe.sub(u"",unicode(r,"utf-8")) for r,score in OmorTransducer.lookup(part2.encode("utf-8"))]
                    match=False
                    for form in wordforms:
                        form=re.sub(u"-",u"",form)
                        form=re.sub(u"\u2010",u"",form)
                        if form==part1:
                            match=True
                            break
                    if not match: return False                 
        #same len and all part matches --> is same                
        return True
    else: return False # different len, can't be same   

#Takes two readings and checks if lemmas are same
#NORMAL CMPND: Lemmas has to be exactly same, or omorfi generated
#NORMAL Der_: 1) If der vs. normal, returns always True (because lemmas are different, can't know for real) 2) If der vs der, calls der_vs_der()
#BOTH CMPND AND DER: splits to sub words and compare those
def isSameLemma(r1,r2):
    if u"Cmpnd" in r1 or u"+#" in r1:
        if u"Cmpnd" in r2 or u"+#" in r2:
            if u"Der_" in r1 or u"Der_" in r2: return split_compounds(r1,r2) #BOTH COMPOUNDS + DERIVATION AT LEAST IN OTHER   
            else: #both are COMPOUNDS WITHOUT DERIVATIONS
                if give_cmpnd_lemma(r1).lower()==give_cmpnd_lemma(r2).lower(): return True
                else: return split_compounds(r1,r2) #try generated forms  
        else: #r1 is compound, r2 isn't --> if lemmas are same, true --> isoisä vs. iso|isä
            compound=give_cmpnd_lemma(r1).lower()
            compound_lemma=re.sub(u"\s",u"",compound)
            compound_hash=re.sub(u"\s",u"-",compound) #try also put "-" between, beacause omorfi drops those
            columns=r2.split("<")
            lemma=columns[0].lower()
            if compound_lemma==lemma or compound_hash==lemma: return True
            else: return False
    elif u"Cmpnd" in r2 or u"+#" in r2: #r2 is compound, r1 isn't --> if lemmas are same, true
        compound=give_cmpnd_lemma(r2).lower()
        compound_lemma=re.sub(u"\s",u"",compound)
        compound_hash=re.sub(u"\s",u"-",compound)
        columns=r1.split("<")
        lemma=columns[0].lower()
        if compound_lemma==lemma or compound_hash==lemma: return True
        else: return False
    elif u"Der_" in r1 or u"Der_" in r2: #JUST DERIVATIONS:
        if u"Der_" in r1 and u"Der_" in r2: return der_vs_der(r1,r2) #both are derivations 
        else: return True    
    else:#both are NORMALS 
        columns=r1.split("<")
        lemma1=columns[0].lower()
        columns=r2.split("<")
        lemma2=columns[0].lower()
        if lemma1==lemma2: return True
        else: return False
            
#compare 1vs1,return better or None if equal, better is the one with less Der_-tags or if same number, more #-tags
def compare(r1,r2):
    if isSameLemma(r1,r2) and isSameAnalysis(r1,r2):
        compound_count1=re.findall(u"\+",r1)
        compound_count2=re.findall(u"\+",r2)
        der_count1=re.findall(u"Der_",r1)
        der_count2=re.findall(u"Der_",r2)
        if len(compound_count1) < len(compound_count2): return r1
        elif len(compound_count2) < len(compound_count1): return r2
        elif len(der_count1) < len(der_count2): return r1
        elif len(der_count2) < len(der_count1): return r2
        else:
            hash_count1=re.findall(u"#",r1)
            hash_count2=re.findall(u"#",r2)
            if len(hash_count2)>len(hash_count1): return r2
            else: return r1     
    else: return None
                   
####################################################################################################            
# MAINS, GO TROUGHT READINGS

#Takes readings (set) and compares those 1vs1 --> if same, marks notwanted with "???". Returns readings (set) with no "???" in them
def handle_cmpnds_and_ders(readings):
    readings=list(readings) #convert set to list, because we need indices.
    for index in range(0,len(readings)):
        r=re.sub(u"\+\+#",u"+#",readings[index]) #because some adj-der-cmpnd:s have ++# instead of +#
        #example: pidempijaksoinen    pitkä<A><Comp><Sg><Nom><Cmpnd>++#jaksoinen<A><Pos><Sg><Nom><cap>
        if r.startswith(u"???"): r=re.sub(u"\?\?\?",u"",r)
        for i in range(index+1,len(readings)):
            if readings[index].startswith(u"???") and readings[i].startswith(u"???"):
                continue #both discarded --> no need to compare berween these
            else:
                other=re.sub(u"\+\+#",u"+#",readings[i])
                other=re.sub(u"\?\?\?",u"",other)
                better=compare(r,other)
                if better!=None: #mark the reading we don't want choose
                    if better==r:
                        if not readings[i].startswith(u"???"):
                            readings[i]=u"???"+readings[i]
                    else:
                        if not readings[index].startswith(u"???"):
                            readings[index]=u"???"+readings[index]
    left_readings=set()
    for r in readings:
        if not r.startswith(u"???"): left_readings.add(r)
    assert len(left_readings)!=0, u"Every reading discarded"
    return left_readings

# main function, calls handle_cmpnds_and_ders() if needed, otherwise just returns same set
def main(readings):
    if len(readings)>1:
        if isCompound(readings) or isDerivation(readings):
            return handle_cmpnds_and_ders(readings)
        else: #all readings are normal, return just same list
            return readings
    else: #just one reading, just return it
        return readings
      
