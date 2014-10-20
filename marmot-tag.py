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

if __name__=="__main__":
    log = logging.getLogger("omorfi")
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-t", "--train", dest="train",action="store_true",default=False, help="Prepare training data")
    parser.add_option("--tempdir", dest="tempdir",action="store",default=".", help="Where temporary files should be kept. Default to current dir.")
    parser.add_option("-m", "--model", dest="model",action="store", default=None,help="Fill PLEMMA/PPOS/PFEAT using this marmot model",metavar="MODELFILE")
    parser.add_option("--marmot", dest="marmotbin",action="store", default=None,help="marmot .jar file")
    (options, args) = parser.parse_args()

    if options.train:
        for line in sys.stdin:
            line=unicode(line,"utf-8").strip()
            if not line:
                print
                continue
            cols=line.split(u"\t")
            assert len(cols) in (13,14,15)
            idx,token,pos,feat=int(cols[0]),cols[1],cols[4],cols[6]
            tagList=[None for x in range(17)]
            #tagList[0]=pos
            if feat!=u"_":
                for cat_tag in feat.split(u"|"):
                    cat,tag=cat_tag.split(u"_",1)
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
            lines.append(line)
            cols=line.split(u"\t")
            if len(cols)==1:
                print >> f
                continue
            else:
                assert len(cols) in (13,14,15)
                pos_set=set(omor.hun_possiblepos(cols[1]))
                marmot_feats=u"#".join(u"POS_"+x for x in sorted(pos_set))
                if not marmot_feats:
                    marmot_feats=u"_"
                print >> f, cols[1]+u"\t"+marmot_feats #wordform tab feats
            wForm=cols[1]
            try:
                tags=u"\t".join(omor.hun_possibletags(wForm))
            except:
                tags=u""
            if not tags:
                continue
            wForms.add(wForm)
            #print >> fM, wForm+u"\t"+tags
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
                raise ValueError("Empty predictions from hunpos in %s"%(os.path.join(options.tempdir,"hunpos_out")))
        except:
            traceback.print_exc()
            log.error("""Did not succeed in launching 'LIBS/%s'. The most common reason for this is that you forgot to run './install.sh'. \n\nIf you get this message even though you did succeed with ./install.sh, it means that the local installation of hunpos is not operating correctly. Try to run the above command, feed into it "koira koira koira koira", one word per line, then one more empty line, and you should get a tagged output. See if there's any obvious problem. Then either open an issue at https://github.com/TurkuNLP/Finnish-dep-parser/issues  or email ginter@cs.utu.fi and jmnybl@utu.fi and we'll try to help you.\n\nGiving up, because the parser cannot run without a tagger."""%(" ".join(args)))
            sys.exit(1)

        
        while predictions[-1]==[u''] or not predictions[-1]:
            predictions.pop(-1)
        while lines[-1]==u'':
            lines.pop(-1)
        
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
            assert inCols[1]==pred[1] #Tokens must match
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
