# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import os,re
datadir='/home/mfeys/work/muc34/TASK/CORPORA/dev'

# <codecell>

docline=re.compile('DEV-MUC(?P<ed>\d)-(?P<val>\d+)')
descline=re.compile(' *(?P<loc>.*), *(?P<date>.*) -- (?P<msg>.*)')
infoblock=re.compile('\[[^]]*\]')
# <codecell>

with open(os.path.join(datadir,'dev-muc3-0001-0100')) as fd:
    first=True
    msg=''
    descr={}
    docno=0
    for line in fd:
        matchline=re.search(docline, line)
        if matchline == None :
            # process msg
            firstline=re.search(descline, line)
            if firstline == None:
                msg=msg+line.replace('\n','')+' '
            else:
                descr['loc']=firstline.group('loc')
                descr['date']=firstline.group('date')
                msg+=firstline.group('msg')+' '
        else:
            #process msg identifier
            if not first:
                lastdoc=matchdoc
                matchdoc=[matchline.group('ed'),matchline.group('val')]
                if matchdoc != None :
                    msg=re.sub(infoblock,'',msg)
                    print (lastdoc,descr,msg)
                    #yield (lastdoc,descr,msg)
                    docno+=1
                    msg=''
                    descr={}
            else:
                lastdoc=[matchline.group('ed'),matchline.group('val')]
                matchdoc=lastdoc
                first=False
                        
    #yield (lastdoc,descr,msg)
    msg=re.sub(infoblock,'',msg)
    print (matchdoc,descr,msg)
    docno+=1
    msg=''