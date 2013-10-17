# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 12:11:02 2013

@author: mfeys
"""
import os,re,zipfile,nltk,logging
from xml.dom.minidom import parseString

logger=logging.getLogger("utils")
poordirectory="/home/mfeys/work/poor"

def getdocuments(directory,extension):
    """
    given a directory, it returns a list of the paths and names of the files with a given extension/format
    """
    filelist=[]
    names=[]
    allfiles=os.listdir(directory)
    for l in allfiles:
        match = re.match(extension,l)
        if match:
            filelist.append(os.path.join(directory,match.group(0)))
            names.append(match.group(0))
            names.sort()
            filelist.sort()
    return filelist,names
    

# Mediargus formats
class PoorDay():
    def __init__(self,docs=None,date=None,zipname=None,poordirectory=poordirectory):
        if docs!=None:
            self.docs=docs
        elif zipname!=None:
            self.docs = zipfile.ZipFile(os.path.join(poordirectory,zipname), "r")
        elif date!=None:
            self.docs = zipfile.ZipFile(os.path.join(poordirectory,"MED_%d.zip"%date), "r")
        else:
            logger.error("no initialization provided")
    
    def __iter__(self):
        for filename in self.docs.namelist():
            yield filename,self.docs.read(filename)

    def getdoc(self,docidentifier):
        return self.docs.read("med%d.xml"%docidentifier)
        
class PoorDoc():
    def __init__(self,docidentifier=None,date=None,docsdate=None,doc=None):
        if doc==None:
            if docsdate==None:
                docsdate = zipfile.ZipFile(os.path.join(poordirectory,"MED_%d.zip"%date), "r")
            doc=docsdate.read("med%d.xml"%docidentifier)
        self.dom=parseString(doc)
        
    def getcontent(self):
        content=self.dom.getElementsByTagName('body.content')
        return nltk.clean_html(content[0].toxml())

    def gettitle(self):
        title=self.dom.getElementsByTagName('headline')[0].getElementsByTagName('hl1')
        return nltk.clean_html(title[0].toxml()).replace('\n',' ').replace('\t',' ')
        
    def getpagenumber(self):
        return self.dom.getElementsByTagName('body.p').item(0).getAttribute("pageNumber")
    
    def getprovider(self):
        return self.dom.getElementsByTagName('id').item(0).getAttribute("title")
    
    def savedoc(self,zpfile,name):
        zpfile.writestr(name,self.dom.toprettyxml(),compress_type=0)