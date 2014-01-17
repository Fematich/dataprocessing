'''
Created on Oct 14, 2013

@author: mfeys
'''
#datadir='/home/mfeys/.gvfs/vib_search\ on\ ibcnserv.intec.ugent.be/mfeys/data/rcv1/disk1'
#datadir='/datasets/mediargus_2011_be/poor'


import logging,os
from datetime import datetime
from zipfile import ZipFile
from whoosh.fields import Schema, TEXT, NUMERIC, DATETIME
from whoosh.index import create_in

from utils import *
from config import mediargus_datadir as datadir,mediargus_indexdir as indexdir


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger=logging.getLogger("index corpus")

def MakeIndex():
    #create schema
    schema = Schema(
                    title=TEXT(stored=True), 
                    content=TEXT,
                    identifier=NUMERIC(stored=True),
                    date=DATETIME(stored=True, sortable=True)
                    )
    #create index
    if not os.path.exists(indexdir):
        os.mkdir(indexdir)
    ix = create_in(indexdir, schema)  
    
    #fill index with entries
    writer = ix.writer(procs=4, limitmb=512, multisegment=True)
    ziplist=os.listdir(datadir)
    for dayname in ziplist:
        logger.info('transforming %s'%dayname)
        zipday=ZipFile(os.path.join(poordirectory,dayname), "r")
        day=PoorDay(docs=zipday,poordirectory=datadir)
        datexs=dayname[4:12]
        for name,data in day:
            doc=PoorDoc(doc=data)
            writer.add_document(title=doc.gettitle(), 
                            content=doc.getcontent(),
                            identifier=int(name[3:11]),
                            date = datetime(year=int(datexs[0:4]), month=int(datexs[4:6]), day=int(datexs[6:8]))
                            )
    
    writer.commit()

if __name__ == '__main__':
    MakeIndex()