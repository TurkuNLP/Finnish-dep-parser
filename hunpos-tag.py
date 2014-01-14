import codecs
import sys
import os
import re
import unicodedata as udata

import omorfi_pos as omor

if __name__=="__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-t", "--train", dest="train",action="store_true",default=False, help="Prepare training data")
    parser.add_option("--tempdir", dest="tempdir",action="store",default=".", help="Where temporary files should be kept. Default to current dir.")
    parser.add_option("-p", "--predict", dest="predict",action="store", default=None,help="Fill PLEMMA/PPOS/PFEAT using the hunpos model",metavar="HUNPOSMODEL")
    parser.add_option("--hunpos", dest="hunposbin",action="store", default=None,help="hunpos-train binary")
    (options, args) = parser.parse_args()

    if options.train:
        for line in sys.stdin:
            line=unicode(line,"utf-8").strip()
            if not line:
                print
                continue
            cols=line.split(u"\t")
            assert len(cols) in (13,14,15)
            token,pos,feat=cols[1],cols[4],cols[6]
            tagList=[None for x in range(17)]
            tagList[0]=pos
            if feat!=u"_":
                for cat_tag in feat.split(u"|"):
                    cat,tag=cat_tag.split(u"_",1)
                    tagList[omor.cat2idx[cat]]=tag
            print (token+u"\t"+omor.hun_taglist2tagstring(tagList)).encode("utf-8")
        print >> sys.stderr, "Now you may want to train hunpos for example as"
        print >> sys.stderr, "cat train.hunpos | LIBS/hunpos-1.0-linux/hunpos-train -f 4 model/hunpos.model"
    elif options.predict!=None:
        wForms=set() #morphtab file entries
        f=codecs.open(os.path.join(options.tempdir,"hunpos_in"),"wt","utf-8")
        fM=codecs.open(os.path.join(options.tempdir,"hunpos_in_mtable"),"wt","utf-8")
        lines=[]
        for line in sys.stdin:
            line=unicode(line,"utf-8").strip()
            lines.append(line)
            cols=line.split(u"\t")
            if len(cols)==1:
                print >> f
                continue
            else:
                assert len(cols) in (13,14,15)
                print >> f, cols[1] #wordform
            wForm=cols[1]
            if wForm in wForms:
                continue #Given already
            try:
                tags=u"\t".join(omor.hun_possibletags(wForm))
            except:
                tags=u""
            if not tags:
                continue
            wForms.add(wForm)
            print >> fM, wForm+u"\t"+tags
        f.close()
        fM.close()
        #Now invoke hunpos
        os.system("%s %s -m %s/hunpos_in_mtable < %s/hunpos_in > %s/hunpos_out"%(options.hunposbin,options.predict,options.tempdir,options.tempdir,options.tempdir))
        f=codecs.open(os.path.join(options.tempdir,"hunpos_out"),"rt","utf-8")
        predictions=[]
        for line in f: #reads in HunPos predictions
            line=line.strip()
            predictions.append(line.split(u"\t"))
        f.close()
        
        while predictions[-1]==[u''] or not predictions[-1]:
            predictions.pop(-1)
        
        newSent=True
        assert len(lines)==len(predictions), (len(lines),len(predictions))
        for inLine,pred in zip(lines,predictions):
            inCols=inLine.split(u"\t")
            if len(inCols)==1:
                assert inCols[0]==u""
                assert pred==[u""]
                print
                newSent=True
                continue #New sentence starts
            assert inCols[1]==pred[0] #Tokens must match
            txt=inCols[1]
            if omor.is_punct(txt):
                plemma,ppos,pfeat=txt,u"Punct",u"_"
            elif omor.is_num(txt):
                plemma,ppos,pfeat=txt,u"Num",u"_"
            else:
                plemma,ptaglist=omor.hun_tag2omorfi(pred[0],pred[1]) #Find the most plausible reading
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
            inCols[3],inCols[5],inCols[7]=plemma,ppos,pfeat
            print (u"\t".join(inCols)).encode("utf-8")
            newSent=False
