#!
__author__ = "Saksham Singhal"

"""
THE following code is specific for data extraction from books. <BEGIN>
"""

class ContentExtractor:
    """
    This is the main content extractor class which will form the basis for pipelining
    for extracting any content form the books
    """

    """
    Example :

    bishopBookExtractor = ContentExtractor("../books-data/ml-bishop.txt", 13, 19, 1, 710, 729, 739, 19)
    bishopBookExtractor.runExtraction()
    """
    def __init__(self,bookname,toc_start,toc_end,content_start,content_end,index_start,index_end,layover = 0):
        """
        Need to initialize with all the information from the book.
        :param bookname:
        :param index_start:
        :param index_end:
        :param toc_start:
        :param toc_end:
        :param content_start:
        :param content_end:
        :param layover: This entry is to add the additional layover that certain pdf files posses
        """
        self.bookname = bookname
        self.index_start = index_start
        self.index_end = index_end
        self.content_start = content_start
        self.content_end = content_end
        self.toc_start = toc_start
        self.toc_end = toc_end
        self.layover = layover

    def runExtraction(self):
        fd = open(self.bookname)
        text = fd.read()
        self.pages = text.split('\x0c')
        fd.close()

        indexEntries = self.getIndexEntries()
        bookContent = self.getContent()
        bookLineContent = self.getLineContent()
        paragraphsContent = self.getParagraphs()
        bookName = self.bookname.split('/')[-1]
        bookContentFile = "../corpus/books-content/%s"%(bookName.replace(".txt","-content.txt"))
        bookBOBIFile  = "../corpus/books-BOBI/%s"%(bookName.replace(".txt","-BOBI.txt"))
        bookParagraphContentFile = "../corpus/books-paragraphs/%s"%(bookName.replace(".txt","-paragraph.txt"))
        bookLineContentFile = "../corpus/books-linewise-content/%s"%(bookName.replace(".txt","-linewise.txt"))
        writeStringToFile(bookContentFile, "\x0c".join(bookContent))
        writeBOBIToFile(bookBOBIFile,indexEntries)
        writeParagraphsToFile(bookParagraphContentFile,paragraphsContent)
        writeStringToFile(bookLineContentFile, bookLineContent)


    def getIndexEntries(self):
        """
        This function extracts the BOBI entries from behind the index
        in the book
        :return:
        """
        indexEntries = {}
        for index in xrange(self.index_start,self.index_end+1):
            page_index = index + self.layover
            page = self.pages[page_index]
            pageEntries = page.split('\n')
            pageEntries = filter(lambda x : isEntry(x),pageEntries)
            for entry in pageEntries:
                addIndexEntries(indexEntries,entry)
        print indexEntries
        return indexEntries

    def getContent(self):
        """
        This function returns only the book content excluding TOC and Index
        :return:
        """
        content = []
        for index in xrange(self.content_start, self.content_end + 1):
            pageIndex = index + self.layover
            page = self.pages[pageIndex]
            page = cleanContentPage(page)
            content.append(page)
        return content

    def getLineContent(self):
        """
        This function keeps the content of the book segregated in lines
        :return:
        """
        content = []
        for index in xrange(self.content_start, self.content_end + 1):
            pageIndex = index + self.layover
            page = self.pages[pageIndex]
            content.append(cleanContent(page))
        content = "".join(content)
        content = content.split("\n")
        content = filter(lambda x:len(x.split()) > 1 and len(x) > 15, content)
        content = "".join(content)
        # content = " ".join(filter(lambda x:performSegmentation(x),content.split()))
        content = content.replace('.','.\n')
        return content



    def getParagraphs(self):
        paragraphs = []
        for index in xrange(self.content_start, self.content_end + 1):
            pageIndex = index + self.layover
            page = self.pages[pageIndex]
            paragraphs.extend(extractParagraphs(page))
        return paragraphs


'''
    This is just util function for some internal processing for textbook data
'''

import re
from wordsegment import load,segment
load()

def performSegmentation(word):
    flag = word.endswith('.')
    new_word = " ".join(segment(word))
    if flag:
        new_word+='.'
    return new_word

def hasPageNumbers(inpString):
    """
    Checks for numbers in a string
    :param inpString:
    :return:
    """
    return any(char.isdigit() for char in inpString)


def notEmpty(str):
    """
    Returns check flag for non empty string
    :param str:
    :return:
    """
    if(len(str) > 0):
        return True
    else:
        return False


def isASCII(str):
    return all(ord(char) < 128 for char in str)


def isEntry(str):
    """
    Function to make sure if a BOBI entry can be qualified as one.
    :param str:
    :return:
    """
    if (hasPageNumbers(str) and notEmpty(str) and len(str.split(',')) > 1 and isASCII(str)):
        return True
    else:
        return False


def addIndexEntries(indexEntries, entry):
    entryVals = entry.split(',')
    pageNums = []
    for i in entryVals[1:]:
        try:
            value = int(i)
            pageNums.append(value)
        except ValueError:
            pass

    if(len(pageNums) > 0):
        indexEntries[entryVals[0]] = pageNums
    return


def cleanContentPage(page):
    """
    This function cleans the page off equation and other UNICODE info
    and makes it free of any unneccesary waste.
    :param page:
    :return:
    """
    page = page.lower()
    page = " ".join(page.split())
    page = re.sub("- ","",page)
    page = re.sub("-"," ",page)
    page = re.sub('[^A-Za-z0-9 ]+', '', page)
    page = " ".join(filter(lambda x: not hasPageNumbers(x),page.split()))
    return page


def cleanContent(content):
    content = content.lower()
    content = re.sub("- ", "", content)
    content = re.sub("-", " ", content)
    content = re.sub(r'\x0c',"",content)
    content = re.sub('[^A-Za-z0-9\n ]+', '', content)
    content = re.sub(r'\n\n',' ',content)
    # content = re.sub(r'(\d+\.\d*)+','',content)
    return content

def filterParagraphs(paragraph):
    word_len = len(paragraph.split(' '))
    if word_len <= 10:
        return False
    return True


def extractParagraphs(page):
    paragraphs = page.split("\n\n")
    paragraphs = [cleanContent(paragraph) for paragraph in paragraphs]
    paragraphs = filter(filterParagraphs,paragraphs)
    return paragraphs


def writeStringToFile(filename,content):
    fd = open(filename,'w')
    fd.write(content)
    fd.close()


def writeBOBIToFile(filename,indexEntries):
    entries = sorted(indexEntries.keys())
    entries = [entry.lower() for entry in entries]
    fd = open(filename,'w')
    for entry in entries:
        fd.write("%s\n"%(entry))
    fd.close()


def writeParagraphsToFile(filename, paragraphs):
    fd = open(filename,'w')
    for paragraph in paragraphs:
        fd.write("%s\n"%(paragraph))
    fd.close()

"""
THE code is specific for data extraction from books. <END>
"""