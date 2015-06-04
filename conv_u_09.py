import sys
import argparse

ID,FORM,LEMMA,UCPOS,UPOS,UFEAT,UHEAD,UDEPREL,UDEPS,UMISC=range(10)
ID,FORM,LEMMA,PLEMMA,POS,PPOS,FEAT,PFEAT,HEAD,PHEAD,DEPREL,PDEPREL=range(12)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Convert conllu to conll09 and back. Infers the direction on its own if no arguments given.')
    parser.add_argument('--output-format', default=None, help='Output format can be "u" or "09". If the input is in this format already, the conversion is a no-op and simply passes data through.')
    parser.add_argument('--drop-comments', default=False, action="store_true", help='Remove comments from the data')
    args = parser.parse_args()
    
    for line in sys.stdin:
        line=line.strip()
        if not line:
            print
        elif line.startswith('#'):
            if not args.drop_comments:
                print line
        else:
            cols=line.split('\t')
            if len(cols)==10:
                #UD in
                if args.output_format=="u":
                    #UD out, no-op
                    print '\t'.join(cols)
                else:
                    #UD -> 09
                    print '\t'.join((cols[ID],cols[FORM],cols[LEMMA],cols[LEMMA],cols[UCPOS],cols[UCPOS],cols[UFEAT],cols[UFEAT],cols[UHEAD],cols[UHEAD],cols[UDEPREL],cols[UDEPREL],'_','_'))
            else:
                #09 in
                assert len(cols) in (12,13,14), cols
                if args.output_format=="09":
                    #09 out, no-op
                    print '\t'.join(cols)
                else:
                    #09 -> UD
                    print '\t'.join((cols[ID],cols[FORM],cols[PLEMMA],cols[PPOS],'_',cols[PFEAT],cols[PHEAD],cols[PDEPREL],'_','_'))

        
