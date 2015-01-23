import codecs
import sys
import os
import re
import unicodedata as udata
import subprocess
import logging
logging.basicConfig(level=logging.WARNING)

import traceback
import omorfi_pos as omor

def load_readings(m_readings):
    words={} #{wordform -> set of (lemma,pos,feat)}
    with codecs.open(m_readings,"r","utf-8") as f:
        for line in f:
            line=line.rstrip(u'\n')
            if not line:
                continue
            form, lemma, pos, feat=line.split(u' ')
            words.setdefault(form,set()).add((lemma,pos,feat))
    return words

def score(ppos,pfeat,pos,feat):
    s=0
    if ppos==pos:
        s+=1
    pfeat_set=set(pfeat.split(u"|"))
    feat_set=set(feat.split(u"|"))
    s+=len(pfeat_set & feat_set)
    return s

def best_reading(plemma,ppos,pfeat,readings):
    if not readings:
        return plemma,ppos,pfeat
    best=max(((lemma,pos,feat,score(ppos,pfeat,pos,feat)) for lemma,pos,feat in readings),key=lambda k:k[3])
    return best[0],ppos,pfeat#best[1],best[2]

if __name__=="__main__":
    log = logging.getLogger("omorfi")
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-t", "--train", dest="train",action="store_true",default=False, help="Prepare training data")
    parser.add_option("--tempdir", dest="tempdir",action="store",default=".", help="Where temporary files should be kept. Default to current dir.")
    parser.add_option("-m", "--model", dest="model",action="store", default=None,help="Fill PLEMMA/PPOS/PFEAT using this marmot model",metavar="MODELFILE")
    parser.add_option("--marmot", dest="marmotbin",action="store", default=None,help="marmot .jar file")
    parser.add_option("--mreadings",action="store", default=None,help="File with the morphological readings")
    parser.add_option("--ud",action="store_true", default=False,help="UD")
    (options, args) = parser.parse_args()

    if options.mreadings:
        readings=load_readings(options.mreadings)
    else:
        readings=None

    if options.train:
        for line in sys.stdin:
            line=unicode(line,"utf-8").strip()
            if line.startswith(u"#"):
                continue
            if not line:
                print
                continue
            cols=line.split(u"\t")
            if len(cols)==10: #UD
                idx,token,pos,feat=int(cols[0]),cols[1],cols[3],cols[5]
            else:
                assert len(cols) in (13,14,15)
                idx,token,pos,feat=int(cols[0]),cols[1],cols[4],cols[6]
            tagList=[None for x in range(17)]
            #tagList[0]=pos
            if options.ud:
                pos_set=set(x[1] for x in readings.get(token,[]))
                s=feat
            else:
                if feat!=u"_":
                    for cat_tag in feat.split(u"|"):
                        if u"=" in cat_tag:
                            cat,tag=cat_tag.split(u"=",1)
                        else:
                            cat,tag=cat_tag.split(u"_",1)
                        if cat not in omor.cat2idx:
                            print >> sys.stderr, "Unknown cat:", cat
                        else:
                            tagList[omor.cat2idx[cat]]=tag
                s=omor.hun_taglist2tagstring(tagList)
                pos_set=set(omor.hun_possiblepos(token))
            #pos_set.add(pos)
            marmot_feats=u"#".join(u"POS_"+x for x in sorted(pos_set))
            if not marmot_feats:
                marmot_feats=u"_"
            if not s:
                s=u"_"
            print (unicode(idx-1)+u"\t"+token+u"\t"+pos+u"\t"+s+u"\t"+marmot_feats).encode("utf-8")
    elif options.model!=None:
        f=codecs.open(os.path.join(options.tempdir,"marmot_in"),"wt","utf-8")
        lines=[]
        for line in sys.stdin:
            line=unicode(line,"utf-8").strip()
            if line.startswith(u"#"):
                continue
            lines.append(line)
            cols=line.split(u"\t")
            if len(cols)==1:
                print >> f
                continue
            else:                
                assert len(cols) in (10,13,14,15)
                if options.ud:
                    pos_set=set(x[1] for x in readings.get(cols[1],[]))
                else:
                    pos_set=set(omor.hun_possiblepos(cols[1]))
                marmot_feats=u"#".join(u"POS_"+x for x in sorted(pos_set))
                if not marmot_feats:
                    marmot_feats=u"_"
                print >> f, cols[1]+u"\t"+marmot_feats #wordform tab feats
        f.close()
        #Now invoke marmot
        try:
            name_in=os.path.join(options.tempdir,"marmot_in")
            name_out=os.path.join(options.tempdir,"marmot_out")
            args=["java","-cp",options.marmotbin,"marmot.morph.cmd.Annotator","--model-file",options.model,"--pred-file",name_out,"--test-file","form-index=0,token-feature-index=1,"+name_in]
            p=subprocess.call(args)

            f=codecs.open(name_out,"r","utf-8")
            predictions=[]
            for line in f: #reads in MarMot predictions
                line=line.strip()
                predictions.append(line.split(u"\t"))
            f.close()

            if len(predictions)==0:
                raise ValueError("Empty predictions from Marmot in %s"%(os.path.join(options.tempdir,"marmot_out")))
        except:
            traceback.print_exc()
            log.error("""Did not succeed in launching 'LIBS/%s'. The most common reason for this is that you forgot to run './install.sh'. \n\nGiving up, because the parser cannot run without a tagger."""%(" ".join(args)))
            sys.exit(1)

        while predictions[-1]==[u''] or not predictions[-1]:
            predictions.pop(-1)
        while lines[-1]==u'':
            lines.pop(-1)
        
        newSent=True
        assert len(lines)==len(predictions), (len(lines),len(predictions))
        if options.ud:
            for inLine,pred in zip(lines,predictions):
                inCols=inLine.split(u"\t")
                if len(inCols)==1:
                    assert inCols[0]==u""
                    assert pred==[u""]
                    print
                    newSent=True
                    continue #New sentence starts
                assert inCols[1]==pred[1] #Tokens must match
                txt=inCols[1]
                ppos=pred[5]
                pfeat=pred[7]
                plemma,ppos,pfeat=best_reading(txt,ppos,pfeat,readings.get(txt,[]))
                if len(inCols)==10:
                    inCols[2],inCols[3],inCols[5]=plemma,ppos,pfeat
                else:
                    inCols[3],inCols[5],inCols[7]=plemma,ppos,pfeat
                print (u"\t".join(inCols)).encode("utf-8")
                newSent=False

        else:

            for inLine,pred in zip(lines,predictions):
                inCols=inLine.split(u"\t")
                if len(inCols)==1:
                    assert inCols[0]==u""
                    assert pred==[u""]
                    print
                    newSent=True
                    continue #New sentence starts
                assert inCols[1]==pred[1] #Tokens must match
                txt=inCols[1]
                if omor.is_punct(txt):
                    plemma,ppos,pfeat=txt,u"Punct",u"_"
                elif omor.is_num(txt):
                    plemma,ppos,pfeat=txt,u"Num",u"_"
                else:
                    tl=u"POS_"+pred[5]
                    if pred[7]!=u"_":
                        tl+=u"|"+pred[7]
                    plemma,ptaglist=omor.hun_tag2omorfi(pred[1],tl) #Find the most plausible reading
                    omor.fill_ortho(txt,ptaglist)
                    if txt==u"*null*":
                        ptaglist[omor.cat2idx[u"OTHER"]]=None
                    ppos=ptaglist[0]
                    #Guess proper nouns
    #                if ppos==u"N" and not newSent and ptaglist[omor.cat2idx[u"CASECHANGE"]]==u"Up" and ptaglist[omor.cat2idx[u"OTHER"]]==u"UNK":
    #                    ptaglist[omor.cat2idx[u"SUBCAT"]]=u"Prop"
                    pfeat=[]
                    for cat,tag in zip(omor.cat_list[1:],ptaglist[1:]):
                        if tag!=None:
                            pfeat.append(cat+u"_"+tag)
                    if not pfeat:
                        pfeat=u"_"
                    else:
                        pfeat=u"|".join(pfeat)
                if len(inCols)==10:
                    inCols[2],inCols[3],inCols[5]=plemma,ppos,pfeat
                else:
                    inCols[3],inCols[5],inCols[7]=plemma,ppos,pfeat
                print (u"\t".join(inCols)).encode("utf-8")
                newSent=False
