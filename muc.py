# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 11:50:54 2013

@author: mfeys
"""



import os
import logging
import re
from datetime import datetime

import whoosh
from whoosh.fields import Schema, TEXT, NUMERIC, DATETIME
from whoosh.index import create_in

from utils import getdocuments
from config import muc_datadir as datadir,muc_indexdir as indexdir


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger=logging.getLogger("muc-data")

def MakeIndex():
    #create schema
    schema = Schema(
                    title=TEXT(stored=True), 
                    content=TEXT,
                    identifier=NUMERIC(stored=True),
                    date=DATETIME(stored=True)
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
        zipday=ZipFile(os.path.join(datadir,dayname), "r")
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