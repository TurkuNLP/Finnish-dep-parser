import argparse
from visualize import read_conll
import sys
import codecs

out8=codecs.getwriter("utf-8")(sys.stdout)

ID=0
FORM=1

def cutCandidates(sent):
    #Cut-point candidates for sent (list of CoNLL09 columns)
    candidates=[] #list of: (score, position of cut (new sent starts here))
    for lIdx in range(args.leeway,len(sent)-args.leeway): #Don't want to cut too short
        l=sent[lIdx]
        if l[FORM]==u";": #semicolon is a decent candidate
            candidates.append((0,lIdx+1))
        elif l[FORM]==u")" and sent[lIdx-1][FORM].isdigit() and sent[lIdx-2][FORM]==u",": #lists like ", 2 ) ..."
            candidates.append((5, lIdx-1))
        elif l[FORM] in (u":",): #colon a worse candidate
            candidates.append((10, lIdx+1))
        elif l[FORM] in (u",",): #comma the worst candidate
            candidates.append((20, lIdx+1))

    return candidates

def cutPointsNearPlaces(nearPlaces,cutCandidates):
    cutPoints=[]
    for p in nearPlaces:
        cands=[(ccPenalty,abs(cc-p),cc) for (ccPenalty,cc) in cutCandidates if cc>=p-args.leeway and cc<=p+args.leeway] #list all candidates near cut points
        cands.sort()
        if cands:
            cutPoints.append(cands[0][2]) #This is the best place to cut around this point
        else:
            cutPoints.append(p) #Meh, we're screwed, just cut and never look back
    return cutPoints

def cutSent(sent):
    nearPlaces=list(range(args.chunk_size,len(sent),args.chunk_size)) #The places nearby which a cut should ideally happen
    candidates=cutCandidates(sent)
    cutPoints=cutPointsNearPlaces(nearPlaces,candidates)
    if len(sent)-cutPoints[-1]<args.leeway:
        cutPoints.pop(-1) #We don't want to have too short final segment

    subsents=[]
    prev=0
    for x in cutPoints+[len(sent)]:
        #create a new sub-sentence
        subsents.append(sent[prev:x])
        
        #...renumber tokens
        newSubSent=subsents[-1]
        for idx in range(len(newSubSent)):
            newSubSent[idx][ID]=unicode(idx+1)
        prev=x

    return subsents

def print_sent(sent,comments):
    print >> out8, u"\n".join(comments)
    print >> out8, u"\n".join(u"\t".join(cols) for cols in sent)
    print >> out8

def cutAndPrintSentence(sent,comments):
    subsents=cutSent(sent)

    #The first sub-sentence will take on the comment of the whole sentence
    print_sent(subsents[0],comments)

    #and every other will have a comment marking it as a continuation of the prev. one
    for x in subsents[1:]:
        assert len(x)>0
        print_sent(x,[u"#---sentence---splitter---JOIN-TO-PREVIOUS-SENTENCE---"])

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Split/merge long sentences')
    parser.add_argument('-N', '--max-len', type=int, default=120, help='Pass sentences shorter or equal to this number of tokens through, split the rest. This will also be the absolute maximum chunk size ever fed into the parser.')
    parser.add_argument('-C', '--chunk-size', type=int, default=80, help='Split into chunks of approximately this size.')
    parser.add_argument('input', nargs='?', help='Input. Nothing or "-" for stdin.')
    args = parser.parse_args()
    args.leeway=args.chunk_size//3 #TODO
    
    for sent,comments in read_conll(args.input,0):
        if len(sent)<=args.max_len: #this one's good
            pass#print_sent(sent,comments)
        else:
            cutAndPrintSentence(sent,comments)

        
        
