from __future__ import division
import codecs
import sys
import re

c2i={} #{col name : col idx}, for fast translation
#                             1  2    3     4      5   6    7    8     9    10    11     12      13      14  
for colIdx,col in enumerate("ID FORM LEMMA PLEMMA POS PPOS FEAT PFEAT HEAD PHEAD DEPREL PDEPREL FILLPRED PRED".split()):
    c2i[col]=colIdx

def printc(cols,out=sys.stdout):
    #always enforce 14 columns from now on
    if len(cols)==15:
        cols=cols[:-1]
    elif len(cols)==13:
        cols.append(u"_")
    elif len(cols)==14:
        pass
    else:
        assert False, ("Whoa, trying to print",len(cols),"columns?", cols)
    print >> out, (u"\t".join(cols)).encode("utf-8")

def checkSentence(currSentence):
    #Fail if there's something structurally wrong here
    roots=0
    for cols in currSentence:
        assert len(cols) in (13,14,15)
        head=int(cols[c2i["HEAD"]])
        phead=int(cols[c2i["PHEAD"]])
        assert head>=0 and head<=len(currSentence)
        if head==0:
            roots+=1
            assert cols[c2i["DEPREL"]]==u"ROOT"
    assert roots==1
    print ".",
    sys.stdout.flush()

def sanity(fileArgs):
    #Sanity-check the file
    currSentence=[] #List of columns
    for (line,) in readFiles(fileArgs):
        if not line:
            checkSentence(currSentence)
            currSentence=[]
        else:
            currSentence.append(line.split(u"\t"))
    else:
        if currSentence:
            checkSentence(currSentence)
    print "ALL OK"

def dropNullsSent(sentenceCounter,currSentence):
    if sentenceCounter!=0:
        print
    nulls=[]
    corrections=[] #Correction at each token position
    nullCounter=0
    for cols in currSentence:
        corrections.append(nullCounter)
        if cols[1]==u"*null*":
            nulls.append(int(cols[0]))
            nullCounter+=1
    assert len(corrections)==len(currSentence)
    for idx,cols in enumerate(currSentence):
        cols[c2i["ID"]]=unicode(int(cols[c2i["ID"]])-corrections[idx])
        if cols[c2i["HEAD"]] not in (u"_",u"0"):
            head=int(cols[c2i["HEAD"]])
            if head in nulls:
                cols[c2i["HEAD"]]=u"0"
                cols[c2i["DEPREL"]]=u"ROOT"
            else:
                cols[c2i["HEAD"]]=unicode(head-corrections[head-1])
        if cols[c2i["PHEAD"]] not in (u"_",u"0"):
            phead=int(cols[c2i["PHEAD"]])
            if phead in nulls:
                cols[c2i["PHEAD"]]=u"0"
                cols[c2i["PDEPREL"]]=u"ROOT"
            else:
                cols[c2i["PHEAD"]]=unicode(phead-corrections[phead-1])
    oldLen=len(currSentence)
    for idx in nulls[::-1]:
        currSentence.pop(idx-1)
    assert len(currSentence)==oldLen-len(nulls)
    for cols in currSentence:
        printc(cols)
    

def dropNulls(fileArgs):
    currSentence=[] #List of columns
    counter=0
    for (line,) in readFiles(fileArgs):
        line=line.strip()
        if not line:
            if currSentence!=[]:
                dropNullsSent(counter,currSentence)
                counter+=1
                currSentence=[]
        else:
            currSentence.append(line.split(u"\t"))
    else:
        if currSentence:
            dropNullsSent(counter,currSentence)


def eval(fileArgs):

    UNK=0 #tokens with GSTAG==UNK
    total=0 #total tokens to take into account
    hardTotal=0

    cats=("LEMMA","POS","POS+FEAT","LEMMA+POS+FEAT","HEAD","DEPREL","HEAD+DEPREL","LEMMA+POS+FEAT+HEAD+DEPREL")
    #cats=("POS+FEAT",)

    longestCat=max(len(combo) for combo in cats) #for result layout
    
    counts={}
    errs={} #{combo:{(gs,sys):count}}
    
    for (line,) in readFiles(fileArgs):
        if not line:
            continue
        cols=line.split(u"\t")
        if cols[c2i["POS"]]==u"UNK":
            UNK+=1
            continue
#        if cols[c2i["POS"]]==u"_": #NO GS TO WORK AGAINST
#            continue
        total+=1
        for combo in cats:
            gsR=u"---".join(cols[c2i[c]] for c in combo.split("+"))
            sysR=u"---".join(cols[c2i["P"+c]] for c in combo.split("+"))
            if gsR!=sysR:
                err=(gsR,sysR)
                #print >> sys.stderr, cols[1].encode("utf-8"), gsR, sysR
                errDict=errs.setdefault(combo,{})
                errDict[err]=errDict.get(err,0)+1
            else:
                counts[combo]=counts.get(combo,0)+1
    for combo in cats:
        corr=counts.get(combo,0)
        print "%s %5.1f (%6d /%6d)"%(combo.rjust(longestCat),corr/total*100,corr,total)
    print
    #printErrs(errs,"POS+FEAT",1000)

def printErrs(err,combo,limit=100):
    lst=list(err[combo].items())
    lst.sort(key=lambda item: item[1],reverse=True)
    for gs_sys,cnt in lst[:limit]:
        print (u"% 6d   GS: %s   SYS: %s"%(cnt,gs_sys[0],gs_sys[1]))



def filter(feat,rewrites):
    tags=feat.split(u"|")
    res=[]
    for t in tags:
        for (exp,replacement) in rewrites:
            if exp.match(t):
                if replacement!=None:
                    res.append(replacement)
                break #First hit applies
        else: #No hits
            res.append(t)
    if res:
        return u"|".join(res)
    else:
        return u"_"
                    
def lines2sentences(lineList):
    sentences=[[]]
    for line in lineList:
        line=line.strip()
        if not line:
            if sentences[-1]: #new sentence
                sentences.append([])
        else:
            sentences[-1].append(line)
    while sentences[-1]==[]:
        sentences.pop(-1)
    return sentences
    
        
def readFiles(args):
    if not args:
        args.append("-") #assume single stdin input
    assert args.count("-")<=1
    fNames=[]
    for fName in args:
        if fName=="-":
            fNames.append("/dev/stdin")
        else:
            fNames.append(fName)
    files=[codecs.open(fName,"rt","utf-8") for fName in fNames]
    all_sentences=[lines2sentences(f.readlines()) for f in files] #Read everything in F lists of sentences
    for sList in all_sentences:
        assert len(sList)==len(all_sentences[0]) #all must be same length
    for tupleIdx,sentenceTuple in enumerate(zip(*all_sentences)):
        for sentence in sentenceTuple:
            assert len(sentence)==len(sentenceTuple[0])
        for lineTuple in zip(*sentenceTuple):
            yield lineTuple
        if tupleIdx<len(all_sentences[0])-1:
            yield tuple(u"" for f in files) #Pretend empty lines
        
       

if __name__=="__main__":

    def arg_option_callback(option,opt,value,parser,*args):
        #stores the name of the option as "action" and its arguments as action_args
        parser.values.action=opt.replace("--","")
        parser.values.action_args=value


    
    from optparse import OptionParser, OptionGroup
    parser = OptionParser(usage="python conllUtil.py --<action> [options] (mainfile.conll09|-) [auxfile.conll09|-]\n\nIf any of the file arguments is specified as '-', it is read from stdin. If no files are given a single '-' is assumed. So you can chain as cat somefile | python conllUtil.py ... | python conllUtil.py ... - file2 | ... Output is always written to stdout.\n\n --!!!-- Careful: only a single action at a time for now, thank you!")

    actionG=OptionGroup(parser, "Action", description="Pick a single action from these:")
    
    actionG.add_option("--retagUNK", dest="action", action="store_const", const="retagUNK", help="Retags UNK. Same as LEMMA:=PLEMMA,POS:=PPOS,FEAT:=PFEAT restricted to tokens where POS==UNK in the first file")
    actionG.add_option("--swap", action="callback", callback=arg_option_callback, type="string", help="Comma separated list of swaps to perform (will be done in left-to-right order). COL1<->COL2 swaps the values of COL1 and COL2, COL1:=COL2 sets COL1 to the value of COL2, COL1:=None sets the value of COL1 to '_'. If two arguments are given, <-> works on left file and := assigns to left file taking values from right file",metavar="SWAP LIST")
    actionG.add_option("--fix14", dest="action", action="store_const", const="fix14", help="Add or remove empty columns to get the standard 14 columns (add max 1 or remove max 1)")
    actionG.add_option("--eval", dest="action", action="store_const", const="eval", help="Evaluates columns versus Pcolumns.")
    actionG.add_option("--sanity", dest="action", action="store_const", const="sanity", help="Do basic sanity check on the file. Checks the tree for single root and dependencies not being all over the place")
    actionG.add_option("--cat", dest="action", action="store_const", const="cat", help="Catenate the input files.")
    actionG.add_option("--dropnulls", dest="action", action="store_const", const="dropnulls", help="Drop *null* tokens from the data. Reattaches their dependents to root.")
    actionG.add_option("--droptags", action="callback", callback=arg_option_callback, type="string", help="Comma separated list of morpho tags to drop/rewrite in FEAT and PFEAT. Format: tagregularexpression->string|None Example: POSS_.*3->POSS_3,CASECHANGE_cap->None,CLIT_->None will merge 3rd person poss sufixes into POSS_3, delete CASECHANGE_cap, and delete all clitics. The regular expressions are matched from start, so use $ if you need exact match. ",metavar="LIST")
    
    
    
    
    parser.add_option_group(actionG)

    (options, args) = parser.parse_args()

    if options.action=="cat":
        for inFile in args:
            f=open(inFile,"rt").read()
            sys.stdout.write(f)
            print
    elif options.action=="retagUNK":
        assert len(args)==2, "you need two files on input"
        for mainLine,auxLine in readFiles(args):
            if not mainLine:
                assert not auxLine
                print
                continue
            mainCols=mainLine.split(u"\t")
            auxCols=auxLine.split(u"\t")
            assert mainCols[:2]==auxCols[:2]
            if mainCols[c2i["POS"]].startswith(u"UNK"):
                mainCols[c2i["POS"]]=auxCols[c2i["PPOS"]]
                mainCols[c2i["LEMMA"]]=auxCols[c2i["PLEMMA"]]
                mainCols[c2i["FEAT"]]=auxCols[c2i["PFEAT"]]
                printc(mainCols)
            else:
                print mainLine.encode("utf-8")
    elif options.action=="swap":
        assert options.action_args, "Need a list of swapped fields"
        #parse what to swap
        assignments=[] #(src,dst,"set|swap")
        pairs=options.action_args.split(",")
        for p in pairs:
            if "<->" in p:
                L,R=p.split("<->")
                A="swap"
            elif ":=" in p:
                L,R=p.split(":=")
                A="set"
            else:
                assert False, ("Do not understand:", p)
            L=c2i[L]
            if R=="None":
                R=None
            else:
                R=c2i[R]
            assignments.append((L,R,A))
        for lines in readFiles(args):
            if len(lines)==1:
                mainLine=lines[0]
                auxLine=None
            else:
                mainLine,auxLine=lines
            if not mainLine:
                print
                continue
            cols=mainLine.split(u"\t")
            assert len(cols) in (13,14,15)
            for L,R,A in assignments:
                if A=="set":
                    if R==None:
                        cols[L]=u"_"
                    else: #Assignment
                        if auxLine!=None: #we have two files
                            auxCols=auxLine.split(u"\t")
                            assert len(auxCols) in (13,14,15), (len(auxCols), auxCols)
                            assert auxCols[:2]==cols[:2], "Mismatch in the files!" #token number and token text should always match
                            cols[L]=auxCols[R]
                        else:
                            cols[L]=cols[R]
                elif A=="swap":
                    tmp=cols[L]
                    cols[L]=cols[R]
                    cols[R]=tmp
            printc(cols)
    elif options.action=="fix14":
        assert len(args)<2, "Only one file can be on input"
        for (mainLine,) in readFiles(args):
            if not mainLine:
                print
                continue
            cols=mainLine.split(u"\t")
            if len(cols)==15: #all okay
                del cols[-1]
            elif len(cols)==14:
                pass #all okay
            elif len(cols)==13:
                cols.append(u"_")
            else:
                assert False #odd-looking file
            printc(cols)
    elif options.action=="eval":
        assert len(args)<2, "Only one file is expected"
        eval(args)
    elif options.action=="sanity":
        assert len(args)<2, "Only one file is expected"
        sanity(args)
    elif options.action=="dropnulls":
        assert len(args)<2, "Only one file is expected"
        dropNulls(args)
    elif options.action=="droptags":
        rewrites=[] #[(regexp,result|None),...]
        pairs=options.action_args.split(",")
        for p in pairs:
            regexp,result=p.rsplit("->",1)
            if result=="None":
                result=None
            exp=re.compile(unicode(regexp,"utf-8"),re.U)
            rewrites.append((exp,result))
        #Now I have all expressions compiled, can process the data
        for (mainLine,) in readFiles(args):
            if not mainLine:
                print
                continue
            cols=mainLine.split(u"\t")
            if cols[c2i["PFEAT"]]!=u"_":
                cols[c2i["PFEAT"]]=filter(cols[c2i["PFEAT"]],rewrites)
            if cols[c2i["FEAT"]]!=u"_":
                cols[c2i["FEAT"]]=filter(cols[c2i["FEAT"]],rewrites)
            printc(cols)
                
