# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 11:50:54 2013

@author: mfeys
"""

"""
module to handle the MUC-files
"""


import os,logging,re
from datetime import datetime

import whoosh
from whoosh.fields import Schema, TEXT, NUMERIC, DATETIME,ID
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser

from utils import getdocuments
from config import muc_datadir as datadir,muc_indexdir as indexdir, MAX_SEARCH_RESULTS

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger=logging.getLogger("muc-data")

devline=re.compile('DEV-MUC(?P<ed>\d)-(?P<val>\d+)')
testline=re.compile('TST.*-MUC(?P<ed>\d)-(?P<val>\d+)')
descline=re.compile('(?P<loc>.*),(?P<date>.*)--(?P<msg>.*)')
infoblock=re.compile('\[[^]]*\]')

class MUCmessages():
    '''
    class to handle the indexed messages
    '''
    def __init__(self,indexdir=indexdir):
        self.ix = open_dir(indexdir)
    
    def finddocs(self,query,max_search_results=MAX_SEARCH_RESULTS):
        res=[]
        with self.ix.searcher() as searcher:
            parser = QueryParser("content", self.ix.schema)
            myquery = parser.parse(query)
            results = searcher.search(myquery,limit=max_search_results)
            ndocs=results.estimated_length()
            for result in results:
                res.append({'identifier':result['identifier'],'content':result['content'],'location':result['location'],'date':result['date']})
        return res,ndocs

    def __iter__(self):
        reader=self.ix.reader()
        return reader.iter_docs()
        
def MakeIndex(Train=True):
    #create schema
    schema = Schema(
                    identifier=TEXT(stored=True), 
                    content=TEXT(stored=True),
                    location=TEXT(stored=True),
                    date=TEXT(stored=True)
                    )
    #create index
    if not os.path.exists(indexdir):
        os.mkdir(indexdir)
    ix = create_in(indexdir, schema)
    
    #fill index with entries    
    writer = ix.writer(procs=1, limitmb=512, multisegment=False) 
    cnt=0
    cnts=0
    for msg in IterateMessages(Train):
        try:
            #print msg
            writer.add_document(identifier=msg[0].decode('unicode-escape'), 
                            content=msg[2],
                            location=(msg[1]['loc']).decode('unicode-escape'),
                            date=(msg[1]['date']).decode('unicode-escape')
                            )
            cnts+=1
        except Exception, e:
            print e,msg
            cnt+=1
    writer.commit()
    print 'Failed documents:%d \t Succeeded:%d'%(cnt,cnts)
class MessageFile():
    '''
    given a string containing different messages, it identifies the different messages and corresponding header-date
    '''
    def __init__(self,text=None,doc=None,docline=devline):
        self.docline=docline
        if text!=None:
            self.text=text
        elif doc!=None:
            with open(doc) as f:
                text=f.readlines()
                self.text=text
        else:
            logger.error("no initialization provided")
    
    def __iter__(self):
        first=True
        msg=''
        descr={}
        docno=0
        for line in self.text:
            matchline=re.search(self.docline, line)
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
                    matchdoc=matchline.group(0)
                    if matchdoc != None :
                        msg=re.sub(infoblock,'',msg)
                        #print (lastdoc,descr,msg)
                        yield (lastdoc,descr,msg.decode('unicode-escape'))
                        docno+=1
                        msg=''
                        descr={}
                else:
                    lastdoc=matchline.group(0)
                    matchdoc=lastdoc
                    first=False
        msg=re.sub(infoblock,'',msg)                    
        yield (matchdoc,descr,msg.decode('unicode-escape'))
        #print (matchdoc,descr,msg)
        docno+=1
        msg=''


def IterateMessages(train=True):
    if train:
        docline=devline
        msgdir=os.path.join(datadir,'dev')
        docs=getdocuments(msgdir,re.compile('dev-.*'))[0]
    else:
        docline=testline
        docs=[]
        for i in range(1,5):
            msgdir=os.path.join(datadir,'tst%d'%i)
            docs+=getdocuments(msgdir,re.compile('tst.*'))[0]
    for docpath in docs:
        logger.info('start processing: %s'%docpath)
        msgfile=MessageFile(doc=docpath,docline=docline)
        for msg in msgfile:
            yield msg


if __name__ == '__main__':
    MakeIndex(True)
    MakeIndex(False)
#    cnt=0
#    for msg in IterateMessages(False):
#        cnt+=1
#    print cnt