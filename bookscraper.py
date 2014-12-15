#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Book Scraper for Data Structures and Algorithms with Object-Oriented Design Patterns in C++ @ http://www.brpreiss.com/books/opus4/

from bs4 import BeautifulSoup
from urllib2 import urlopen
from urllib import urlretrieve
#import urlparse
import traceback
from random import randrange

import re
import json
#from collections import defaultdict
#import logging
#from logging import DEBUG, INFO
import os
import pdb
from time import sleep

#logging.basicConfig(level=INFO)

def sections_filter(tag):
    if(tag.name == 'a'):
        if(tag.parent.name == 'li'):
            gP = tag.parent.parent
            if(gP.name == 'ul'):
                ##pdb.set_trace()
#                print(str(tag['href']) + ": " + str(gP.attrs))
                if(len(gP.attrs) > 0):
                    if("contents" in gP["class"]):
                        return True
    return False

#    return (tag.name == 'a' and
#        tag.parent.name == 'li' and
#        tag.parent.parent.name == 'ul' and
#        'contents' in tag.parent.parent['class'])


def processSubLinkText(tag):
    if(tag.name == 'a'):
        if(type(tag.contents) == list and len(tag.contents) > 1):
            # contains <t> nodes, etc
            LinkText = ""
            #print("Tag: " + str(tag) + ", contents: " + str(tag.contents) + "[" + str(len(tag.contents)) + "]")
            for item in tag.contents:
                if(type(item) == type(tag)):
                    if(item.name == "img"):
                        # img tag has to processed
                        LinkText = LinkText + str(item)
                    else:
                        LinkText = LinkText + str(item.text) #TT tag can be eliminated
                else:
                    LinkText = LinkText + str(item)
            
            LinkText = LinkText.replace('\n', '')
            return LinkText
        else:
            #Assuming plain string
            return tag.text

class BookScraper(object):
    def __init__(self, base_url, toc_page=u""):
        self.base_url = base_url
        self.downloadCache = {}
        if base_url is None:
            self.soup = self.get_page_soup_from_text(toc_page)
        else:
            self.soup = self.get_page_soup(toc_page)
    
    def processImgTags(self, htmlWithImgTags):
        tempSoup = BeautifulSoup(htmlWithImgTags)
                            
        for imgTag in tempSoup.findAll("img"):
            # detect the src node and download to images folder
            # modify the scr attrbute to refelect the downloaded image
            if(imgTag.name == 'img'):
                #Only operate on Image tags.
                # 1. Dowload the image to imageDownloadPath
                # 2. modify src to reflect the imageDownloadPath
                
                filename = imgTag["src"].split("/")[-1]
                outpath = self.imageFolderPath + "\\" + filename
                
                urlToRetrieve = ""
                
                if imgTag["src"].lower().startswith("http"):
                    urlToRetrieve = imgTag["src"]
                    #urlretrieve(imgTag["src"], outpath)
                else:
                    urlToRetrieve = self.base_url + imgTag["src"]
                    #urlretrieve(self.base_url + imgTag["src"], outpath)
                
                #if file already exists skip download
                if(outpath in self.downloadCache.keys()):
                    print "Image ", outpath, " already exists...     [SKIP], URL: ", urlToRetrieve
                    imgTag["src"] = self.imageFolderName + "\\" + filename
                    continue
                
                retryCount = 5
                print "Attempting to download img: ", urlToRetrieve, "=>" , outpath
                
                while True:
                    print "Attempt #[" , str(6 - retryCount) , "]...",
                    try:
                        urlretrieve(urlToRetrieve, outpath)
                    except (IOError, RuntimeError):
                        print "      [ERROR]"
                        traceback.print_exc()
                        retryCount = retryCount -1
                        if(retryCount <= 0):
                            print("Failed to download[" + str(11 - retryCount) + "]: " + urlToRetrieve)
                            break
                        sleep(randrange(0, 10))
                    else:
                        print "        [OK]"
                        # Now modify the original img tag to reflect the local path
                        imgTag["src"] = self.imageFolderName + "\\" + filename
                        self.downloadCache[outpath] = True
                        #if file downloaded successfully, add to cache
                        break
                        
        return str(tempSoup)
        
    def setBasePath(self, base_url):
        self.base_url = base_url
        self.image_path = "images"
    
    def setImagePath(self, imagePath):
        self.image_path = imagePath
    
    def setBookTitle(self, strTitle):
        self.bookTitle = strTitle
        
    def setAuthor(self, strAuthor):
        self.bookAuthor = strAuthor
       
    def parse_toc_brpreiss(self):
        book = {}
        self.toc = self.soup.find("ul")
                
        chap_no = 1     
        #pdb.set_trace()   
        for link in self.toc.find_all(sections_filter): # or soup.find_all(my_filter)
            # Each section <a> will be identified here.
            # the section may have 1 or more chapters, or may itself be a chapter            
            #print("[" + str(counter) + "]: " + link.get("href") + ", " + link.get("name") + ": " + link.text)
            
            book[chap_no] = {
            "chapter_title": processSubLinkText(link),
            "chapter_href": link.get("href"),
            "chapter_type": "simple",
            "sections": []
            }
            
            chaptersInSection = link.findNextSibling("ul")
            if ( chaptersInSection is None or len(chaptersInSection) == 0 ):
                # must be a simple chapter
                print("Simple chapter : " + str(link.text))
                #book[chap_no]["index"] = str(link)
                #chapterContents = self.get_page_soup(link.get("href"))
                
#                book[chap_no]["sections"].append({
#                        "href": link.get("href"),
#                        "section_title": processSubLinkText(link),
#                        "content": link.get("href")
#                            #self.get_page_soup(link.get("href")).find("body")
#                        })
            else:
                #book[chap_no]["index"] = str(link)
                chaptersInSection = chaptersInSection.findChildren("a")
                print("# chapter " + str(link.text) + " with " + str(len(chaptersInSection))+ " sections.")
                for subLink in chaptersInSection:
                    # subLink.text may contain <tt/> nodes, so process the same
                    book[chap_no]["chapter_type"] = "complex"
                    subLinkText = processSubLinkText(subLink)
                    print("\t:" + subLink.get("href") + ", " + subLink.get("name") + ": " + subLinkText)
                    book[chap_no]["sections"].append({
                        "href": subLink.get("href"),
                        "section_title": subLinkText,
                        "content": subLink.get("href")
                            #self.get_page_soup(subLink.get("href")).find("body")
                        })
            chap_no += 1
        print("Chapters = [" + str(chap_no) + "]")
        self.book = book
        print("book = " + str(len(self.book)))

    def parse_toc(self):
        book = {}
        print("TOC = " + str(self.toc))
        #    chapters = self.toc.findAll("h2")
        chapters = self.toc.findAll("li")
        print("chapters = " + str(chapters) + "[" + str(len(chapters)) + "]")
        chap_no = 0;
        for ch in chapters: # <li/> level tag, sections will be ul tag nested, <a/> will be single chapter
            #chap_no = ch.a["name"][2:4]
            chap_no = chap_no + 1
            book[chap_no] = {
            "chapter_title": ch.a.contents[1].strip(),
            "sections": []
            }
            print("chap[" + chap_no+"] = " + str(book[chap_no]))
            
            # Find links to sections of the each chapter
            sections = ch.findNextSibling("ul").findAll("a", href=re.compile("^ch"))
            
            for sec in sections:
                sec_content = self.get_page_soup(
                sec["href"]).find("div", "content")
                book[chap_no]["sections"].append({
                "href": sec["href"],
                "section_title": sec_content.h1.contents[0],
                "content": str(sec_content)
                })
        self.book = book
        print("book = " + str(self.book))

    def save_json(self, filename):
        with open(filename, "w") as fn:
            json.dump(self.book, fn, indent=2)
            
    def beautiful_soup_tag_to_unicode(self, tag):
            # If you have more than 480 level of nested tags you can hit the maximum recursion level            
            out=[]
            for mystring in tag.findAll(text=None):
                pdb.set_trace()
                mystring=mystring.strip()
                if not mystring:
                    continue
                out.append(mystring)
            pdb.set_trace()
            return u'<pre>%s</pre>' % '\n'.join(out)
    
    def get_page_soup(self, page_path):
        retryCount = 10        
        print("Attempting to download: " + self.base_url + "[" + page_path + "]")
        while True:
            print "Attempt #[" , str(11 - retryCount) , "]...",
            try:
                soup = BeautifulSoup(urlopen(self.base_url + page_path).read())
            except (IOError, RuntimeError):
                print "      [ERROR]"
                traceback.print_exc()
                retryCount = retryCount -1
                if(retryCount <= 0):
                    print("Failed to download[" + str(11 - retryCount) + "]: " + self.base_url + "[" + page_path + "]")
                    break
                sleep(randrange(0, 10))
            else:
                print "        [OK]"
                return soup
        return None
    
    def get_page_soup_from_text(self, htmlText):
        return BeautifulSoup(htmlText)
        
    def generatePathsAndFolders(self):
        self.bookFolderName = self.bookTitle + "_" + self.bookAuthor
        self.bookFolderName = self.bookFolderName.replace(" ", "_")
        self.imageFolderName = "images"
        self.imageFolderPath = self.bookFolderName + "\\" + self.imageFolderName
        
        if not os.path.exists(self.bookFolderName):
            os.makedirs(self.bookFolderName)
        
        if not os.path.exists(self.imageFolderPath):
            os.makedirs(self.imageFolderPath)
            
        # calculate all files that have been downloaded
        #print "os.getcwd() = ", os.getcwd()
        
        print "Files in ", self.bookFolderName, ":- "
        for file in os.listdir(self.bookFolderName):
            print "\t", self.bookFolderName + '\\' + str(file)
            self.downloadCache[self.bookFolderName + '\\' + str(file)] = 1
            
        print "Files in ", self.imageFolderPath, ":- "
        for file in os.listdir(self.imageFolderPath):
            print "\t", self.imageFolderPath + '\\' + str(file)
            self.downloadCache[self.imageFolderPath + '\\' + str(file)] = 1
    
    def generateIndexPage(self):
        template="""
        <html>
        <head>
        <title>{BookTitle}</title>
        </head>
        <body>
        <h2>Contents</h2>        
        {content}
        </body>
        </html>
        """

        filename = "index.html"
        filepath = self.bookFolderName + "\\" + filename
        
        #pdb.set_trace()
                        
        with open(filepath, "w") as fn:
            to_write = template.format(
            BookTitle="Data Structures and Algorithms with Object-Oriented Design Patterns in C++",            
            content="".join(self.indexPage))
            fn.write(to_write)
        print("wrote index!")

    def export_html(self):
        chapterTemplate="""
        <html>
        <head>
        <title>{ch_no}. {chapter}</title>
        </head>
        <body>
        <h1>{chapter}</h1>
        {content}
        </body>
        </html>
        """
        sectionTemplate="""
        <html>
        <head>
        <title>{chapter}</title>
        </head>
        <body>
        <h2>{chapter}</h2>
        {content}
        </body>
        </html>
        """        
        self.generatePathsAndFolders()
        
        self.indexPage = ['<ul>'];
#        maxChapterCounter = 5        
        for chapter, ch_cont in self.book.iteritems():
            #maxChapterCounter = maxChapterCounter -1
            ch_no = chapter#str(chapter).rjust(2, "0")
            #sec_to_write = ""
            filename = ch_cont["chapter_href"].split("#")[0]
            filepath = self.bookFolderName + '\\' + filename
            
            # for both simple and complex chapters first process the chapter main page, followed by sections.

            # images in ch_cont["chapter_title"] has to be handled
            ch_cont["chapter_title"] = self.processImgTags(ch_cont["chapter_title"])
            #sec["section_title"] = self.processImgTags(sec["section_title"])
            
            blocalFile = False
            if(filepath in bs.downloadCache):
                chap = BeautifulSoup(open(filepath).read())
                print "Getting local file: ", filepath, "chap = ", str(chap is not None)
                blocalFile = True
            else:                
                chap = self.get_page_soup(filename)
            
            if(chap is not None):
                if(blocalFile == False):
                    try:
                        conts = str(chap)
                    except RuntimeError as e:
                        print(str(e))
                        continue
                    except IndexError as e:
                        print(str(e))
                        continue
                    else:
                        #conts = self.beautiful_soup_tag_to_unicode(chap)
                         continue
                         
                    chapContent = re.split("<hr>", conts)#ch_cont["chapter_href"])))
                    contentToWrite = self.processImgTags(chapContent[1])
            
                    print("Writing to " + filepath)
                    with open(filepath, "w") as fn:
                        to_write = chapterTemplate.format(
                        ch_no=ch_no,
                        chapter=ch_cont["chapter_title"],                
                        content=contentToWrite)
                                        
                        fn.write(to_write)
                        print("wrote a chapter!")
                        
                self.indexPage.append('<li>')
                self.indexPage.append('<a href="' + str(filename) + '">' + str(ch_cont["chapter_title"]) + '</a>')
            
            #if(ch_cont["chapter_type"] == "simple"):
            #    ch_cont["chapter_title"] = self.processImgTags(ch_cont["chapter_title"])
            #    # images in sec["content"] has to be handled before writing
            #    sec["section_title"] = self.processImgTags(sec["section_title"])
            #    #self.get_page_soup(link.get("href")).find("body")
            #    #sec["content"] has the url. Now we need to download the text and the images
            #    sectionContent = re.split("<hr>",str(self.get_page_soup(sec["content"])))
            #    sec["content"] = self.processImgTags(sectionContent[1])
            #    sec_to_write = sec_to_write + sectionTemplate.format(content=sec["content"]) + "<br/>"
            #    
            #    self.indexPage[ch_no] = '<a href="' + str(filename) + '">' + str(ch_cont["chapter_title"]) + '</a>'
            #else:
            if(ch_cont["chapter_type"] == "complex"):
                #self.indexPage[ch_no] = '<a href="' + str(filename) + '">' + str(ch_cont["chapter_title"]) + '</a>'
                self.indexPage.append('<ul>')
                for sec in ch_cont["sections"]:
                    # Merge sections of chapter into a single page
                    self.indexPage.append('<li>')
                                    
                    # images in ch_cont["chapter_title"] has to be handled
                    #ch_cont["chapter_title"] = self.processImgTags(ch_cont["chapter_title"])
                    # images in sec["content"] has to be handled before writing
                    filename = sec["href"].split("#")[0]
                    filepath = self.bookFolderName + '\\' + filename
                    sec["section_title"] = self.processImgTags(sec["section_title"])
                    
                    blocalFile = False
                    if(filepath in bs.downloadCache):
                        secData = BeautifulSoup(open(filepath).read())
                        print "Getting local file: ", filepath, "secData = ", str(secData is not None)
                        blocalFile = True
                    else:
                        secData = self.get_page_soup(filename)
                    
                    if(secData is not None):
                        if(blocalFile == False):
                            sectionContent = re.split("<hr>",str(secData))#sec["content"])))
                            sec["content"] = self.processImgTags(sectionContent[1])
                            #sec_to_write = sectionTemplate.format(content=sec["content"]) + "<br/>"                        
                    
                            print("Writing section to :" + filepath)
                            with open(filepath, "w") as fn:
                                to_write = sectionTemplate.format(
                                chapter=sec["section_title"],
                                content=sec["content"])                        
                                fn.write(to_write)
                                print("wrote a section - chapter!")
                                
                        self.indexPage.append('<a href="' + str(filename) + '">' + str(sec["section_title"]) + '</a>')
                        self.indexPage.append('</li>')                
                self.indexPage.append('</ul>')
            self.indexPage.append('</li>')
            ## Write one html file per chapter
            #
            #print("Writing to " + filepath)
            #with open(filepath, "w") as fn:
            #    to_write = chapterTemplate.format(
            #    ch_no=ch_no,
            #    chapter=ch_cont["chapter_title"],                
            #    content=sec_to_write)
            #    
            #    fn.write(to_write)
            #    print("wrote a chapter!")
            #if( maxChapterCounter <= 0):
            #    break
        self.indexPage.append('</ul>')
        self.generateIndexPage()

#if __name__ == "__main__":
#  import sys
#
#  bs = BookScraper("http://gettingreal.37signals.com/", "toc.php")
#  if len(sys.argv) > 1 and sys.argv[1] == "export":
#    bs.parse_toc()
#    bs.export_html()


#def main():
#import sys
#    bs = BookScraper("http://gettingreal.37signals.com/", "toc.php")
htmlText = """
<ul class="contents">
	<li>
		<a name="tex2html1374" href="page1.html#SECTION000100000000000000000">Colophon</a>
	</li>
	<li>
		<a name="tex2html1375" href="page2.html#SECTION000200000000000000000">Dedication</a>
	</li>
	<li>
		<a name="tex2html1376" href="page3.html#SECTION000300000000000000000">Preface</a>
		<ul>
			<li>
				<a name="tex2html1377" href="page4.html#SECTION000310000000000000000">Goals</a>
			</li>
			<li>
				<a name="tex2html1378" href="page5.html#SECTION000320000000000000000">Approach</a>
			</li>
			<li>
				<a name="tex2html1379" href="page6.html#SECTION000330000000000000000">Outline</a>
			</li>
			<li>
				<a name="tex2html1380" href="page7.html#SECTION000340000000000000000">Suggested Course Outline</a>
			</li>
			<li>
				<a name="tex2html1381" href="page8.html#SECTION000350000000000000000">Online Course Materials</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1382" href="page10.html#SECTION002000000000000000000">Introduction</a>
		<ul>
			<li>
				<a name="tex2html1383" href="page11.html#SECTION002100000000000000000">What This Book Is About</a>
			</li>
			<li>
				<a name="tex2html1384" href="page12.html#SECTION002200000000000000000">Object-Oriented Design</a>
				<ul>
					<li>
						<a name="tex2html1385" href="page13.html#SECTION002201000000000000000">Abstraction</a>
					</li>
					<li>
						<a name="tex2html1386" href="page14.html#SECTION002202000000000000000">Encapsulation</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1387" href="page15.html#SECTION002300000000000000000">Object Hierarchies and Design Patterns</a>
				<ul>
					<li>
						<a name="tex2html1388" href="page16.html#SECTION002301000000000000000">Containers</a>
					</li>
					<li>
						<a name="tex2html1389" href="page17.html#SECTION002302000000000000000">Iterators</a>
					</li>
					<li>
						<a name="tex2html1390" href="page18.html#SECTION002303000000000000000">Visitors</a>
					</li>
					<li>
						<a name="tex2html1391" href="page19.html#SECTION002304000000000000000">Adapters</a>
					</li>
					<li>
						<a name="tex2html1392" href="page20.html#SECTION002305000000000000000">Singletons</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1393" href="page21.html#SECTION002400000000000000000">The Features of C++ You Need to Know</a>
				<ul>
					<li>
						<a name="tex2html1394" href="page22.html#SECTION002401000000000000000">Variables</a>
					</li>
					<li>
						<a name="tex2html1395" href="page23.html#SECTION002402000000000000000">Parameter Passing</a>
					</li>
					<li>
						<a name="tex2html1396" href="page24.html#SECTION002403000000000000000">Pointers</a>
					</li>
					<li>
						<a name="tex2html1397" href="page25.html#SECTION002404000000000000000">Classes and Objects</a>
					</li>
					<li>
						<a name="tex2html1398" href="page26.html#SECTION002405000000000000000">Inheritance</a>
					</li>
					<li>
						<a name="tex2html1399" href="page27.html#SECTION002406000000000000000">Other Features</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1400" href="page28.html#SECTION002500000000000000000">How This Book Is Organized</a>
				<ul>
					<li>
						<a name="tex2html1401" href="page29.html#SECTION002501000000000000000">Models and Asymptotic Analysis</a>
					</li>
					<li>
						<a name="tex2html1402" href="page30.html#SECTION002502000000000000000">Foundational Data Structures</a>
					</li>
					<li>
						<a name="tex2html1403" href="page31.html#SECTION002503000000000000000">Abstract Data Types and the Class Hierarchy</a>
					</li>
					<li>
						<a name="tex2html1404" href="page32.html#SECTION002504000000000000000">Data Structures</a>
					</li>
					<li>
						<a name="tex2html1405" href="page33.html#SECTION002505000000000000000">Algorithms</a>
					</li>
				</ul>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1406" href="page34.html#SECTION003000000000000000000">Algorithm Analysis</a>
		<ul>
			<li>
				<a name="tex2html1407" href="page35.html#SECTION003100000000000000000">A Detailed Model of the Computer</a>
				<ul>
					<li>
						<a name="tex2html1408" href="page36.html#SECTION003110000000000000000">The Basic Axioms</a>
					</li>
					<li>
						<a name="tex2html1409" href="page37.html#SECTION003120000000000000000">A Simple Example-Arithmetic Series Summation</a>
					</li>
					<li>
						<a name="tex2html1410" href="page38.html#SECTION003130000000000000000">Array Subscripting Operations</a>
					</li>
					<li>
						<a name="tex2html1411" href="page39.html#SECTION003140000000000000000">Another Example-Horner's Rule</a>
					</li>
					<li>
						<a name="tex2html1412" href="page40.html#SECTION003150000000000000000">Analyzing Recursive Functions</a>
						<ul>
							<li>
								<a name="tex2html1413" href="page41.html#SECTION003151000000000000000">Solving Recurrence Relations-Repeated Substitution</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1414" href="page42.html#SECTION003160000000000000000">Yet Another Example-Finding the Largest Element of an Array</a>
					</li>
					<li>
						<a name="tex2html1415" href="page43.html#SECTION003170000000000000000">Average Running Times</a>
					</li>
					<li>
						<a name="tex2html1416" href="page44.html#SECTION003180000000000000000">About Harmonic Numbers</a>
					</li>
					<li>
						<a name="tex2html1417" href="page45.html#SECTION003190000000000000000">Best-Case and Worst-Case Running Times</a>
					</li>
					<li>
						<a name="tex2html1418" href="page46.html#SECTION0031100000000000000000">The Last Axiom</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1419" href="page47.html#SECTION003200000000000000000">A Simplified Model of the Computer</a>
				<ul>
					<li>
						<a name="tex2html1420" href="page48.html#SECTION003210000000000000000">An Example-Geometric Series Summation</a>
					</li>
					<li>
						<a name="tex2html1421" href="page49.html#SECTION003220000000000000000">About Arithmetic Series Summation</a>
					</li>
					<li>
						<a name="tex2html1422" href="page50.html#SECTION003230000000000000000">Example-Geometric Series Summation Again</a>
					</li>
					<li>
						<a name="tex2html1423" href="page51.html#SECTION003240000000000000000">About Geometric Series Summation</a>
					</li>
					<li>
						<a name="tex2html1424" href="page52.html#SECTION003250000000000000000">Example-Computing Powers</a>
					</li>
					<li>
						<a name="tex2html1425" href="page53.html#SECTION003260000000000000000">Example-Geometric Series Summation Yet Again</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1426" href="page54.html#SECTION003300000000000000000">Exercises</a>
			</li>
			<li>
				<a name="tex2html1427" href="page55.html#SECTION003400000000000000000">Projects</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1428" href="page56.html#SECTION004000000000000000000">Asymptotic Notation</a>
		<ul>
			<li>
				<a name="tex2html1429" href="page57.html#SECTION004100000000000000000">An Asymptotic Upper Bound-Big Oh</a>
				<ul>
					<li>
						<a name="tex2html1430" href="page58.html#SECTION004110000000000000000">A Simple Example</a>
					</li>
					<li>
						<a name="tex2html1431" href="page59.html#SECTION004120000000000000000">Big Oh Fallacies and Pitfalls</a>
					</li>
					<li>
						<a name="tex2html1432" href="page60.html#SECTION004130000000000000000">Properties of Big Oh</a>
					</li>
					<li>
						<a name="tex2html1433" href="page61.html#SECTION004140000000000000000">About Polynomials</a>
					</li>
					<li>
						<a name="tex2html1434" href="page62.html#SECTION004150000000000000000">About Logarithms</a>
					</li>
					<li>
						<a name="tex2html1435" href="page63.html#SECTION004160000000000000000">Tight Big Oh Bounds</a>
					</li>
					<li>
						<a name="tex2html1436" href="page64.html#SECTION004170000000000000000">More Big Oh Fallacies and Pitfalls</a>
					</li>
					<li>
						<a name="tex2html1437" href="page65.html#SECTION004180000000000000000">Conventions for Writing Big Oh Expressions</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1438" href="page66.html#SECTION004200000000000000000">An Asymptotic Lower Bound-Omega</a>
				<ul>
					<li>
						<a name="tex2html1439" href="page67.html#SECTION004210000000000000000">A Simple Example</a>
					</li>
					<li>
						<a name="tex2html1440" href="page68.html#SECTION004220000000000000000">About Polynomials Again</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1441" href="page69.html#SECTION004300000000000000000">More Notation-Theta and Little Oh</a>
			</li>
			<li>
				<a name="tex2html1442" href="page70.html#SECTION004400000000000000000">Asymptotic Analysis of Algorithms</a>
				<ul>
					<li>
						<a name="tex2html1443" href="page71.html#SECTION004410000000000000000">Rules For Big Oh Analysis of Running Time</a>
					</li>
					<li>
						<a name="tex2html1444" href="page72.html#SECTION004420000000000000000">Example-Prefix Sums</a>
					</li>
					<li>
						<a name="tex2html1445" href="page73.html#SECTION004430000000000000000">Example-Fibonacci Numbers</a>
					</li>
					<li>
						<a name="tex2html1446" href="page74.html#SECTION004440000000000000000">Example-Bucket Sort</a>
					</li>
					<li>
						<a name="tex2html1447" href="page75.html#SECTION004450000000000000000">Reality Check</a>
					</li>
					<li>
						<a name="tex2html1448" href="page76.html#SECTION004460000000000000000">Checking Your Analysis</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1449" href="page77.html#SECTION004500000000000000000">Exercises</a>
			</li>
			<li>
				<a name="tex2html1450" href="page78.html#SECTION004600000000000000000">Projects</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1451" href="page79.html#SECTION005000000000000000000">Foundational Data Structures</a>
		<ul>
			<li>
				<a name="tex2html1452" href="page80.html#SECTION005100000000000000000">Dynamic Arrays</a>
				<ul>
					<li>
						<a name="tex2html1453" href="page81.html#SECTION005110000000000000000">Default Constructor</a>
					</li>
					<li>
						<a name="tex2html1454" href="page82.html#SECTION005120000000000000000">Array Constructor</a>
					</li>
					<li>
						<a name="tex2html1455" href="page83.html#SECTION005130000000000000000">Copy Constructor</a>
					</li>
					<li>
						<a name="tex2html1456" href="page84.html#SECTION005140000000000000000">Destructor</a>
					</li>
					<li>
						<a name="tex2html1457" href="page85.html#SECTION005150000000000000000">Array Member Functions</a>
					</li>
					<li>
						<a name="tex2html1458" href="page86.html#SECTION005160000000000000000">Array Subscripting Operator</a>
					</li>
					<li>
						<a name="tex2html1459" href="page87.html#SECTION005170000000000000000">Resizing an Array</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1460" href="page88.html#SECTION005200000000000000000">Singly-Linked Lists</a>
				<ul>
					<li>
						<a name="tex2html1461" href="page89.html#SECTION005210000000000000000">An Implementation</a>
					</li>
					<li>
						<a name="tex2html1462" href="page90.html#SECTION005220000000000000000">List Elements</a>
					</li>
					<li>
						<a name="tex2html1463" href="page91.html#SECTION005230000000000000000">Default Constructor</a>
					</li>
					<li>
						<a name="tex2html1464" href="page92.html#SECTION005240000000000000000">Destructor and <tt>Purge</tt> Member Function</a>
					</li>
					<li>
						<a name="tex2html1465" href="page93.html#SECTION005250000000000000000">Accessors</a>
					</li>
					<li>
						<a name="tex2html1466" href="page94.html#SECTION005260000000000000000">
							<tt>First</tt> and <tt>Last</tt> Functions</a>
					</li>
					<li>
						<a name="tex2html1467" href="page95.html#SECTION005270000000000000000">
							<tt>Prepend</tt>
						</a>
					</li>
					<li>
						<a name="tex2html1468" href="page96.html#SECTION005280000000000000000">
							<tt>Append</tt>
						</a>
					</li>
					<li>
						<a name="tex2html1469" href="page97.html#SECTION005290000000000000000">Copy Constructor and Assignment Operator</a>
					</li>
					<li>
						<a name="tex2html1470" href="page98.html#SECTION0052100000000000000000">
							<tt>Extract</tt>
						</a>
					</li>
					<li>
						<a name="tex2html1471" href="page99.html#SECTION0052110000000000000000">
							<tt>InsertAfter</tt> and <tt>InsertBefore</tt>
						</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1472" href="page100.html#SECTION005300000000000000000">Multi-Dimensional Arrays</a>
				<ul>
					<li>
						<a name="tex2html1473" href="page101.html#SECTION005310000000000000000">Array Subscript Calculations</a>
					</li>
					<li>
						<a name="tex2html1474" href="page102.html#SECTION005320000000000000000">Two-Dimensional Array Implementation</a>
					</li>
					<li>
						<a name="tex2html1475" href="page103.html#SECTION005330000000000000000">Multi-Dimensional Subscripting in C++</a>
					</li>
					<li>
						<a name="tex2html1476" href="page104.html#SECTION005340000000000000000">Canonical Matrix Multiplication</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1477" href="page105.html#SECTION005400000000000000000">Exercises</a>
			</li>
			<li>
				<a name="tex2html1478" href="page106.html#SECTION005500000000000000000">Projects</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1479" href="page107.html#SECTION006000000000000000000">Data Types and Abstraction</a>
		<ul>
			<li>
				<a name="tex2html1480" href="page108.html#SECTION006100000000000000000">Abstract Data Types</a>
			</li>
			<li>
				<a name="tex2html1481" href="page109.html#SECTION006200000000000000000">Design Patterns</a>
				<ul>
					<li>
						<a name="tex2html1482" href="page110.html#SECTION006210000000000000000">Class Hierarchy</a>
					</li>
					<li>
						<a name="tex2html1483" href="page111.html#SECTION006220000000000000000">Objects</a>
						<ul>
							<li>
								<a name="tex2html1484" href="page112.html#SECTION006221000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1485" href="page113.html#SECTION006230000000000000000">The <tt>NullObject</tt> Singleton Class</a>
						<ul>
							<li>
								<a name="tex2html1486" href="page114.html#SECTION006231000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1487" href="page115.html#SECTION006240000000000000000">Object Wrappers for the Built-In Types</a>
						<ul>
							<li>
								<a name="tex2html1488" href="page116.html#SECTION006241000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1489" href="page117.html#SECTION006250000000000000000">Containers</a>
					</li>
					<li>
						<a name="tex2html1490" href="page118.html#SECTION006260000000000000000">Visitors</a>
						<ul>
							<li>
								<a name="tex2html1491" href="page119.html#SECTION006261000000000000000">The <tt>IsDone</tt> Member Function</a>
							</li>
							<li>
								<a name="tex2html1492" href="page120.html#SECTION006262000000000000000">
									<tt>Container</tt> Class Default <tt>Put</tt> Member Function</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1493" href="page121.html#SECTION006270000000000000000">Iterators</a>
					</li>
					<li>
						<a name="tex2html1494" href="page122.html#SECTION006280000000000000000">The <tt>NullIterator</tt> Class</a>
					</li>
					<li>
						<a name="tex2html1495" href="page123.html#SECTION006290000000000000000">Direct vs. Indirect Containment</a>
					</li>
					<li>
						<a name="tex2html1496" href="page124.html#SECTION0062100000000000000000">Ownership of Contained Objects</a>
					</li>
					<li>
						<a name="tex2html1497" href="page125.html#SECTION0062110000000000000000">Associations</a>
						<ul>
							<li>
								<a name="tex2html1498" href="page126.html#SECTION0062111000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1499" href="page127.html#SECTION0062120000000000000000">Searchable Containers</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1500" href="page128.html#SECTION006300000000000000000">Exercises</a>
			</li>
			<li>
				<a name="tex2html1501" href="page129.html#SECTION006400000000000000000">Projects</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1502" href="page130.html#SECTION007000000000000000000">Stacks, Queues and Deques</a>
		<ul>
			<li>
				<a name="tex2html1503" href="page131.html#SECTION007100000000000000000">Stacks</a>
				<ul>
					<li>
						<a name="tex2html1504" href="page132.html#SECTION007110000000000000000">Array Implementation</a>
						<ul>
							<li>
								<a name="tex2html1505" href="page133.html#SECTION007111000000000000000">Member Variables</a>
							</li>
							<li>
								<a name="tex2html1506" href="page134.html#SECTION007112000000000000000">Constructor and Destructor</a>
							</li>
							<li>
								<a name="tex2html1507" href="page135.html#SECTION007113000000000000000">
									<tt>Push</tt>, <tt>Pop</tt>, and <tt>Top</tt> Member Functions</a>
							</li>
							<li>
								<a name="tex2html1508" href="page136.html#SECTION007114000000000000000">The <tt>Accept</tt> Member Function</a>
							</li>
							<li>
								<a name="tex2html1509" href="page137.html#SECTION007115000000000000000">Iterator</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1510" href="page138.html#SECTION007120000000000000000">Linked List Implementation</a>
						<ul>
							<li>
								<a name="tex2html1511" href="page139.html#SECTION007121000000000000000">Member Variables</a>
							</li>
							<li>
								<a name="tex2html1512" href="page140.html#SECTION007122000000000000000">Constructor and Destructor</a>
							</li>
							<li>
								<a name="tex2html1513" href="page141.html#SECTION007123000000000000000">
									<tt>Push</tt>, <tt>Pop</tt>, and <tt>Top</tt> Member Functions</a>
							</li>
							<li>
								<a name="tex2html1514" href="page142.html#SECTION007124000000000000000">The <tt>Accept</tt> Member Function</a>
							</li>
							<li>
								<a name="tex2html1515" href="page143.html#SECTION007125000000000000000">Iterator</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1516" href="page144.html#SECTION007130000000000000000">Applications</a>
						<ul>
							<li>
								<a name="tex2html1517" href="page145.html#SECTION007131000000000000000">Evaluating Postfix Expressions</a>
							</li>
							<li>
								<a name="tex2html1518" href="page146.html#SECTION007132000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1519" href="page147.html#SECTION007200000000000000000">Queues</a>
				<ul>
					<li>
						<a name="tex2html1520" href="page148.html#SECTION007210000000000000000">Array Implementation</a>
						<ul>
							<li>
								<a name="tex2html1521" href="page149.html#SECTION007211000000000000000">Member Variables</a>
							</li>
							<li>
								<a name="tex2html1522" href="page150.html#SECTION007212000000000000000">Constructor and Destructor</a>
							</li>
							<li>
								<a name="tex2html1523" href="page151.html#SECTION007213000000000000000">
									<tt>Head</tt>, <tt>Enqueue</tt>, and <tt>Dequeue</tt> Member Functions</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1524" href="page152.html#SECTION007220000000000000000">Linked List Implementation</a>
						<ul>
							<li>
								<a name="tex2html1525" href="page153.html#SECTION007221000000000000000">Member Variables</a>
							</li>
							<li>
								<a name="tex2html1526" href="page154.html#SECTION007222000000000000000">Constructor and Destructor</a>
							</li>
							<li>
								<a name="tex2html1527" href="page155.html#SECTION007223000000000000000">
									<tt>Head</tt>, <tt>Enqueue</tt> and <tt>Dequeue</tt> Member Functions</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1528" href="page156.html#SECTION007230000000000000000">Applications</a>
						<ul>
							<li>
								<a name="tex2html1529" href="page157.html#SECTION007231000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1530" href="page158.html#SECTION007300000000000000000">Deques</a>
				<ul>
					<li>
						<a name="tex2html1531" href="page159.html#SECTION007310000000000000000">Array Implementation</a>
						<ul>
							<li>
								<a name="tex2html1532" href="page160.html#SECTION007311000000000000000">
									<tt>Tail</tt>, <tt>EnqueueHead</tt>,
    and <tt>DequeueTail</tt> Member Functions</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1533" href="page161.html#SECTION007320000000000000000">Linked List Implementation</a>
						<ul>
							<li>
								<a name="tex2html1534" href="page162.html#SECTION007321000000000000000">
									<tt>Tail</tt>, <tt>EnqueueHead</tt>,
    and <tt>DequeueTail</tt> Member Functions</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1535" href="page163.html#SECTION007330000000000000000">Doubly-Linked and Circular Lists</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1536" href="page164.html#SECTION007400000000000000000">Exercises</a>
			</li>
			<li>
				<a name="tex2html1537" href="page165.html#SECTION007500000000000000000">Projects</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1538" href="page166.html#SECTION008000000000000000000">Ordered Lists and Sorted Lists</a>
		<ul>
			<li>
				<a name="tex2html1539" href="page167.html#SECTION008100000000000000000">Ordered Lists</a>
				<ul>
					<li>
						<a name="tex2html1540" href="page168.html#SECTION008110000000000000000">Array Implementation</a>
						<ul>
							<li>
								<a name="tex2html1541" href="page169.html#SECTION008111000000000000000">Member Variables</a>
							</li>
							<li>
								<a name="tex2html1542" href="page170.html#SECTION008112000000000000000">Inserting and Accessing Items in a List</a>
							</li>
							<li>
								<a name="tex2html1543" href="page171.html#SECTION008113000000000000000">Finding Items in a List</a>
							</li>
							<li>
								<a name="tex2html1544" href="page172.html#SECTION008114000000000000000">Removing Items from a List</a>
							</li>
							<li>
								<a name="tex2html1545" href="page173.html#SECTION008115000000000000000">Positions of Items in a List</a>
							</li>
							<li>
								<a name="tex2html1546" href="page174.html#SECTION008116000000000000000">Finding the Position of an Item and Accessing by Position</a>
							</li>
							<li>
								<a name="tex2html1547" href="page175.html#SECTION008117000000000000000">Inserting an Item at an Arbitrary Position</a>
							</li>
							<li>
								<a name="tex2html1548" href="page176.html#SECTION008118000000000000000">Removing Arbitrary Items by Position</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1549" href="page177.html#SECTION008120000000000000000">Linked List Implementation</a>
						<ul>
							<li>
								<a name="tex2html1550" href="page178.html#SECTION008121000000000000000">Member Variables</a>
							</li>
							<li>
								<a name="tex2html1551" href="page179.html#SECTION008122000000000000000">Inserting and Accessing Items in a List</a>
							</li>
							<li>
								<a name="tex2html1552" href="page180.html#SECTION008123000000000000000">Finding Items in a List</a>
							</li>
							<li>
								<a name="tex2html1553" href="page181.html#SECTION008124000000000000000">Removing Items from a List</a>
							</li>
							<li>
								<a name="tex2html1554" href="page182.html#SECTION008125000000000000000">Positions of Items in a List</a>
							</li>
							<li>
								<a name="tex2html1555" href="page183.html#SECTION008126000000000000000">Finding the Position of an Item and Accessing by Position</a>
							</li>
							<li>
								<a name="tex2html1556" href="page184.html#SECTION008127000000000000000">Inserting an Item at an Arbitrary Position</a>
							</li>
							<li>
								<a name="tex2html1557" href="page185.html#SECTION008128000000000000000">Removing Arbitrary Items by Position</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1558" href="page186.html#SECTION008130000000000000000">Performance Comparison:
<tt>ListAsArray</tt> vs. <tt>ListAsLinkedList</tt>
						</a>
					</li>
					<li>
						<a name="tex2html1559" href="page187.html#SECTION008140000000000000000">Applications</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1560" href="page188.html#SECTION008200000000000000000">Sorted Lists</a>
				<ul>
					<li>
						<a name="tex2html1561" href="page189.html#SECTION008210000000000000000">Array Implementation</a>
						<ul>
							<li>
								<a name="tex2html1562" href="page190.html#SECTION008211000000000000000">Inserting Items in a Sorted List</a>
							</li>
							<li>
								<a name="tex2html1563" href="page191.html#SECTION008212000000000000000">Locating Items in an Array-Binary Search</a>
							</li>
							<li>
								<a name="tex2html1564" href="page192.html#SECTION008213000000000000000">Finding Items in a Sorted List</a>
							</li>
							<li>
								<a name="tex2html1565" href="page193.html#SECTION008214000000000000000">Removing Items from a List</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1566" href="page194.html#SECTION008220000000000000000">Linked List Implementation</a>
						<ul>
							<li>
								<a name="tex2html1567" href="page195.html#SECTION008221000000000000000">Inserting Items in a Sorted List</a>
							</li>
							<li>
								<a name="tex2html1568" href="page196.html#SECTION008222000000000000000">Other Operations on Sorted Lists</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1569" href="page197.html#SECTION008230000000000000000">Performance Comparison:
<tt>SortedListAsArray</tt> vs. <tt>SortedListAsList</tt>
						</a>
					</li>
					<li>
						<a name="tex2html1570" href="page198.html#SECTION008240000000000000000">Applications</a>
						<ul>
							<li>
								<a name="tex2html1571" href="page199.html#SECTION008241000000000000000">Implementation</a>
							</li>
							<li>
								<a name="tex2html1572" href="page200.html#SECTION008242000000000000000">Analysis</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1573" href="page201.html#SECTION008300000000000000000">Exercises</a>
			</li>
			<li>
				<a name="tex2html1574" href="page202.html#SECTION008400000000000000000">Projects</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1575" href="page203.html#SECTION009000000000000000000">Hashing, Hash Tables and Scatter Tables</a>
		<ul>
			<li>
				<a name="tex2html1576" href="page204.html#SECTION009100000000000000000">Hashing-The Basic Idea</a>
				<ul>
					<li>
						<a name="tex2html1577" href="page205.html#SECTION009100100000000000000">Example</a>
					</li>
					<li>
						<a name="tex2html1578" href="page206.html#SECTION009110000000000000000">Keys and Hash Functions</a>
						<ul>
							<li>
								<a name="tex2html1579" href="page207.html#SECTION009111000000000000000">Avoiding Collisions</a>
							</li>
							<li>
								<a name="tex2html1580" href="page208.html#SECTION009112000000000000000">Spreading Keys Evenly</a>
							</li>
							<li>
								<a name="tex2html1581" href="page209.html#SECTION009113000000000000000">Ease of Computation</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1582" href="page210.html#SECTION009200000000000000000">Hashing Methods</a>
				<ul>
					<li>
						<a name="tex2html1583" href="page211.html#SECTION009210000000000000000">Division Method</a>
					</li>
					<li>
						<a name="tex2html1584" href="page212.html#SECTION009220000000000000000">Middle Square Method</a>
					</li>
					<li>
						<a name="tex2html1585" href="page213.html#SECTION009230000000000000000">Multiplication Method</a>
					</li>
					<li>
						<a name="tex2html1586" href="page214.html#SECTION009240000000000000000">Fibonacci Hashing</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1587" href="page215.html#SECTION009300000000000000000">Hash Function Implementations</a>
				<ul>
					<li>
						<a name="tex2html1588" href="page216.html#SECTION009310000000000000000">Integral Keys</a>
					</li>
					<li>
						<a name="tex2html1589" href="page217.html#SECTION009320000000000000000">Floating-Point Keys</a>
					</li>
					<li>
						<a name="tex2html1590" href="page218.html#SECTION009330000000000000000">Character String Keys</a>
					</li>
					<li>
						<a name="tex2html1591" href="page219.html#SECTION009340000000000000000">Hashing <tt>Object</tt>s</a>
					</li>
					<li>
						<a name="tex2html1592" href="page220.html#SECTION009350000000000000000">Hashing <tt>Container</tt>s</a>
					</li>
					<li>
						<a name="tex2html1593" href="page221.html#SECTION009360000000000000000">Using <tt>Association</tt>s</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1594" href="page222.html#SECTION009400000000000000000">Hash Tables</a>
				<ul>
					<li>
						<a name="tex2html1595" href="page223.html#SECTION009410000000000000000">Separate Chaining</a>
						<ul>
							<li>
								<a name="tex2html1596" href="page224.html#SECTION009411000000000000000">Implementation</a>
							</li>
							<li>
								<a name="tex2html1597" href="page225.html#SECTION009412000000000000000">Constructor and Destructor</a>
							</li>
							<li>
								<a name="tex2html1598" href="page226.html#SECTION009413000000000000000">Inserting and Removing Items</a>
							</li>
							<li>
								<a name="tex2html1599" href="page227.html#SECTION009414000000000000000">Finding an Item</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1600" href="page228.html#SECTION009420000000000000000">Average Case Analysis</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1601" href="page229.html#SECTION009500000000000000000">Scatter Tables</a>
				<ul>
					<li>
						<a name="tex2html1602" href="page230.html#SECTION009510000000000000000">Chained Scatter Table</a>
						<ul>
							<li>
								<a name="tex2html1603" href="page231.html#SECTION009511000000000000000">Implementation</a>
							</li>
							<li>
								<a name="tex2html1604" href="page232.html#SECTION009512000000000000000">Constructors and Destructor</a>
							</li>
							<li>
								<a name="tex2html1605" href="page233.html#SECTION009513000000000000000">Inserting and Finding an Item</a>
							</li>
							<li>
								<a name="tex2html1606" href="page234.html#SECTION009514000000000000000">Removing Items</a>
							</li>
							<li>
								<a name="tex2html1607" href="page235.html#SECTION009515000000000000000">Worst-Case Running Time</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1608" href="page236.html#SECTION009520000000000000000">Average Case Analysis</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1609" href="page237.html#SECTION009600000000000000000">Scatter Table using Open Addressing</a>
				<ul>
					<li>
						<a name="tex2html1610" href="page238.html#SECTION009610000000000000000">Linear Probing</a>
					</li>
					<li>
						<a name="tex2html1611" href="page239.html#SECTION009620000000000000000">Quadratic Probing</a>
					</li>
					<li>
						<a name="tex2html1612" href="page240.html#SECTION009630000000000000000">Double Hashing</a>
					</li>
					<li>
						<a name="tex2html1613" href="page241.html#SECTION009640000000000000000">Implementation</a>
						<ul>
							<li>
								<a name="tex2html1614" href="page242.html#SECTION009641000000000000000">Constructors and Destructor</a>
							</li>
							<li>
								<a name="tex2html1615" href="page243.html#SECTION009642000000000000000">Inserting Items</a>
							</li>
							<li>
								<a name="tex2html1616" href="page244.html#SECTION009643000000000000000">Finding Items</a>
							</li>
							<li>
								<a name="tex2html1617" href="page245.html#SECTION009644000000000000000">Removing Items</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1618" href="page246.html#SECTION009650000000000000000">Average Case Analysis</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1619" href="page247.html#SECTION009700000000000000000">Applications</a>
			</li>
			<li>
				<a name="tex2html1620" href="page248.html#SECTION009800000000000000000">Exercises</a>
			</li>
			<li>
				<a name="tex2html1621" href="page249.html#SECTION009900000000000000000">Projects</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1622" href="page250.html#SECTION0010000000000000000000">Trees</a>
		<ul>
			<li>
				<a name="tex2html1623" href="page251.html#SECTION0010100000000000000000">Basics</a>
				<ul>
					<li>
						<a name="tex2html1624" href="page252.html#SECTION0010101000000000000000">Terminology</a>
					</li>
					<li>
						<a name="tex2html1625" href="page253.html#SECTION0010102000000000000000">More Terminology</a>
					</li>
					<li>
						<a name="tex2html1626" href="page254.html#SECTION0010103000000000000000">Alternate Representations for Trees</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1627" href="page255.html#SECTION0010200000000000000000">
					<i>N</i>-ary Trees</a>
			</li>
			<li>
				<a name="tex2html1628" href="page256.html#SECTION0010300000000000000000">Binary Trees</a>
			</li>
			<li>
				<a name="tex2html1629" href="page257.html#SECTION0010400000000000000000">Tree Traversals</a>
				<ul>
					<li>
						<a name="tex2html1630" href="page258.html#SECTION0010401000000000000000">Preorder Traversal</a>
					</li>
					<li>
						<a name="tex2html1631" href="page259.html#SECTION0010402000000000000000">Postorder Traversal</a>
					</li>
					<li>
						<a name="tex2html1632" href="page260.html#SECTION0010403000000000000000">Inorder Traversal</a>
					</li>
					<li>
						<a name="tex2html1633" href="page261.html#SECTION0010404000000000000000">Breadth-First Traversal</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1634" href="page262.html#SECTION0010500000000000000000">Expression Trees</a>
				<ul>
					<li>
						<a name="tex2html1635" href="page263.html#SECTION0010501000000000000000">Infix Notation</a>
					</li>
					<li>
						<a name="tex2html1636" href="page264.html#SECTION0010502000000000000000">Prefix Notation</a>
					</li>
					<li>
						<a name="tex2html1637" href="page265.html#SECTION0010503000000000000000">Postfix Notation</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1638" href="page266.html#SECTION0010600000000000000000">Implementing Trees</a>
				<ul>
					<li>
						<a name="tex2html1639" href="page267.html#SECTION0010610000000000000000">Tree Traversals</a>
						<ul>
							<li>
								<a name="tex2html1640" href="page268.html#SECTION0010611000000000000000">Depth-First Traversal</a>
							</li>
							<li>
								<a name="tex2html1641" href="page269.html#SECTION0010612000000000000000">Preorder, Inorder and Postorder Traversals</a>
							</li>
							<li>
								<a name="tex2html1642" href="page270.html#SECTION0010613000000000000000">Breadth-First Traversal</a>
							</li>
							<li>
								<a name="tex2html1643" href="page271.html#SECTION0010614000000000000000">
									<tt>Accept</tt> Member Function</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1644" href="page272.html#SECTION0010620000000000000000">Tree Iterators</a>
						<ul>
							<li>
								<a name="tex2html1645" href="page273.html#SECTION0010621000000000000000">Member Variables</a>
							</li>
							<li>
								<a name="tex2html1646" href="page274.html#SECTION0010622000000000000000">Constructor and <tt>Reset</tt> Member Function</a>
							</li>
							<li>
								<a name="tex2html1647" href="page275.html#SECTION0010623000000000000000">Operator Member Functions</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1648" href="page276.html#SECTION0010630000000000000000">General Trees</a>
						<ul>
							<li>
								<a name="tex2html1649" href="page277.html#SECTION0010631000000000000000">Member Variables</a>
							</li>
							<li>
								<a name="tex2html1650" href="page278.html#SECTION0010632000000000000000">Member Functions</a>
							</li>
							<li>
								<a name="tex2html1651" href="page279.html#SECTION0010633000000000000000">Constructor, Destructor, and <tt>Purge</tt> Member Function</a>
							</li>
							<li>
								<a name="tex2html1652" href="page280.html#SECTION0010634000000000000000">
									<tt>Key</tt> and <tt>Subtree</tt> Member Functions</a>
							</li>
							<li>
								<a name="tex2html1653" href="page281.html#SECTION0010635000000000000000">
									<tt>AttachSubtree</tt> and <tt>DetachSubtree</tt> Member Functions</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1654" href="page282.html#SECTION0010640000000000000000">
							<i>N</i>-ary Trees</a>
						<ul>
							<li>
								<a name="tex2html1655" href="page283.html#SECTION0010641000000000000000">Member Variables</a>
							</li>
							<li>
								<a name="tex2html1656" href="page284.html#SECTION0010642000000000000000">Member Functions</a>
							</li>
							<li>
								<a name="tex2html1657" href="page285.html#SECTION0010643000000000000000">Constructors</a>
							</li>
							<li>
								<a name="tex2html1658" href="page286.html#SECTION0010644000000000000000">
									<tt>IsEmpty</tt> Member Function</a>
							</li>
							<li>
								<a name="tex2html1659" href="page287.html#SECTION0010645000000000000000">
									<tt>Key</tt>, <tt>AttachKey</tt> and <tt>DetachKey</tt>
Member Functions</a>
							</li>
							<li>
								<a name="tex2html1660" href="page288.html#SECTION0010646000000000000000">
									<tt>Subtree</tt>, <tt>AttachSubtree</tt> and <tt>DetachSubtree</tt>
Member Functions</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1661" href="page289.html#SECTION0010650000000000000000">Binary Trees</a>
						<ul>
							<li>
								<a name="tex2html1662" href="page290.html#SECTION0010651000000000000000">Member Variables</a>
							</li>
							<li>
								<a name="tex2html1663" href="page291.html#SECTION0010652000000000000000">Constructors</a>
							</li>
							<li>
								<a name="tex2html1664" href="page292.html#SECTION0010653000000000000000">Destructor and <tt>Purge</tt> Member Functions</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1665" href="page293.html#SECTION0010660000000000000000">Binary Tree Traversals</a>
					</li>
					<li>
						<a name="tex2html1666" href="page294.html#SECTION0010670000000000000000">Comparing Trees</a>
					</li>
					<li>
						<a name="tex2html1667" href="page295.html#SECTION0010680000000000000000">Applications</a>
						<ul>
							<li>
								<a name="tex2html1668" href="page296.html#SECTION0010681000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1669" href="page297.html#SECTION0010700000000000000000">Exercises</a>
			</li>
			<li>
				<a name="tex2html1670" href="page298.html#SECTION0010800000000000000000">Projects</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1671" href="page299.html#SECTION0011000000000000000000">Search Trees</a>
		<ul>
			<li>
				<a name="tex2html1672" href="page300.html#SECTION0011100000000000000000">Basics</a>
				<ul>
					<li>
						<a name="tex2html1673" href="page301.html#SECTION0011110000000000000000">
							<i>M</i>-Way Search Trees</a>
					</li>
					<li>
						<a name="tex2html1674" href="page302.html#SECTION0011120000000000000000">Binary Search Trees</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1675" href="page303.html#SECTION0011200000000000000000">Searching a Search Tree</a>
				<ul>
					<li>
						<a name="tex2html1676" href="page304.html#SECTION0011201000000000000000">Searching an <i>M</i>-way Tree</a>
					</li>
					<li>
						<a name="tex2html1677" href="page305.html#SECTION0011202000000000000000">Searching a Binary Tree</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1678" href="page306.html#SECTION0011300000000000000000">Average Case Analysis</a>
				<ul>
					<li>
						<a name="tex2html1679" href="page307.html#SECTION0011310000000000000000">Successful Search</a>
					</li>
					<li>
						<a name="tex2html1680" href="page308.html#SECTION0011320000000000000000">Solving The Recurrence-Telescoping</a>
					</li>
					<li>
						<a name="tex2html1681" href="page309.html#SECTION0011330000000000000000">Unsuccessful Search</a>
					</li>
					<li>
						<a name="tex2html1682" href="page310.html#SECTION0011340000000000000000">Traversing a Search Tree</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1683" href="page311.html#SECTION0011400000000000000000">Implementing Search Trees</a>
				<ul>
					<li>
						<a name="tex2html1684" href="page312.html#SECTION0011410000000000000000">Binary Search Trees</a>
						<ul>
							<li>
								<a name="tex2html1685" href="page313.html#SECTION0011411000000000000000">Member Variables</a>
							</li>
							<li>
								<a name="tex2html1686" href="page314.html#SECTION0011412000000000000000">
									<tt>Find</tt> Member Function</a>
							</li>
							<li>
								<a name="tex2html1687" href="page315.html#SECTION0011413000000000000000">
									<tt>FindMin</tt> Member Function</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1688" href="page316.html#SECTION0011420000000000000000">Inserting Items in a Binary Search Tree</a>
						<ul>
							<li>
								<a name="tex2html1689" href="page317.html#SECTION0011421000000000000000">
									<tt>Insert</tt> and <tt>AttachKey</tt> Member Functions</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1690" href="page318.html#SECTION0011430000000000000000">Removing Items from a Binary Search Tree</a>
						<ul>
							<li>
								<a name="tex2html1691" href="page319.html#SECTION0011431000000000000000">
									<tt>Withdraw</tt> and <tt>DetachKey</tt> Member Functions</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1692" href="page320.html#SECTION0011500000000000000000">AVL Search Trees</a>
				<ul>
					<li>
						<a name="tex2html1693" href="page321.html#SECTION0011510000000000000000">Implementing AVL Trees</a>
						<ul>
							<li>
								<a name="tex2html1694" href="page322.html#SECTION0011511000000000000000">Constructor</a>
							</li>
							<li>
								<a name="tex2html1695" href="page323.html#SECTION0011512000000000000000">
									<tt>Height</tt>,
<tt>AdjustHeight</tt> and <tt>BalanceFactor</tt> Member Functions</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1696" href="page324.html#SECTION0011520000000000000000">Inserting Items into an AVL Tree</a>
						<ul>
							<li>
								<a name="tex2html1697" href="page325.html#SECTION0011521000000000000000">Balancing AVL Trees</a>
							</li>
							<li>
								<a name="tex2html1698" href="page326.html#SECTION0011522000000000000000">Single Rotations</a>
							</li>
							<li>
								<a name="tex2html1699" href="page327.html#SECTION0011523000000000000000">Double Rotations</a>
							</li>
							<li>
								<a name="tex2html1700" href="page328.html#SECTION0011524000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1701" href="page329.html#SECTION0011530000000000000000">Removing Items from an AVL Tree</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1702" href="page330.html#SECTION0011600000000000000000">
					<i>M</i>-Way Search Trees</a>
				<ul>
					<li>
						<a name="tex2html1703" href="page331.html#SECTION0011610000000000000000">Implementing <i>M</i>-Way Search Trees</a>
						<ul>
							<li>
								<a name="tex2html1704" href="page332.html#SECTION0011611000000000000000">Implementation</a>
							</li>
							<li>
								<a name="tex2html1705" href="page333.html#SECTION0011612000000000000000">Member Functions</a>
							</li>
							<li>
								<a name="tex2html1706" href="page334.html#SECTION0011613000000000000000">Inorder Traversal</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1707" href="page335.html#SECTION0011620000000000000000">Finding Items in an <i>M</i>-Way Search Tree</a>
						<ul>
							<li>
								<a name="tex2html1708" href="page336.html#SECTION0011621000000000000000">Linear Search</a>
							</li>
							<li>
								<a name="tex2html1709" href="page337.html#SECTION0011622000000000000000">Binary Search</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1710" href="page338.html#SECTION0011630000000000000000">Inserting Items into an <i>M</i>-Way Search Tree</a>
					</li>
					<li>
						<a name="tex2html1711" href="page339.html#SECTION0011640000000000000000">Removing Items from an <i>M</i>-Way Search Tree</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1712" href="page340.html#SECTION0011700000000000000000">B-Trees</a>
				<ul>
					<li>
						<a name="tex2html1713" href="page341.html#SECTION0011710000000000000000">Implementing B-Trees</a>
						<ul>
							<li>
								<a name="tex2html1714" href="page342.html#SECTION0011711000000000000000">Member Variables</a>
							</li>
							<li>
								<a name="tex2html1715" href="page343.html#SECTION0011712000000000000000">Constructors</a>
							</li>
							<li>
								<a name="tex2html1716" href="page344.html#SECTION0011713000000000000000">Private Member Functions</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1717" href="page345.html#SECTION0011720000000000000000">Inserting Items into a B-Tree</a>
						<ul>
							<li>
								<a name="tex2html1718" href="page346.html#SECTION0011721000000000000000">Implementation</a>
							</li>
							<li>
								<a name="tex2html1719" href="page347.html#SECTION0011722000000000000000">Running Time Analysis</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1720" href="page348.html#SECTION0011730000000000000000">Removing Items from a B-Tree</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1721" href="page349.html#SECTION0011800000000000000000">Applications</a>
			</li>
			<li>
				<a name="tex2html1722" href="page350.html#SECTION0011900000000000000000">Exercises</a>
			</li>
			<li>
				<a name="tex2html1723" href="page351.html#SECTION00111000000000000000000">Projects</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1724" href="page352.html#SECTION0012000000000000000000">Heaps and Priority Queues</a>
		<ul>
			<li>
				<a name="tex2html1725" href="page353.html#SECTION0012100000000000000000">Basics</a>
			</li>
			<li>
				<a name="tex2html1726" href="page354.html#SECTION0012200000000000000000">Binary Heaps</a>
				<ul>
					<li>
						<a name="tex2html1727" href="page355.html#SECTION0012210000000000000000">Complete Trees</a>
						<ul>
							<li>
								<a name="tex2html1728" href="page356.html#SECTION0012211000000000000000">Complete <i>N</i>-ary Trees</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1729" href="page357.html#SECTION0012220000000000000000">Implementation</a>
						<ul>
							<li>
								<a name="tex2html1730" href="page358.html#SECTION0012221000000000000000">Member Variables</a>
							</li>
							<li>
								<a name="tex2html1731" href="page359.html#SECTION0012222000000000000000">Constructor, Destructor and <tt>Purge</tt> Member Functions</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1732" href="page360.html#SECTION0012230000000000000000">Putting Items into a Binary Heap</a>
					</li>
					<li>
						<a name="tex2html1733" href="page361.html#SECTION0012240000000000000000">Removing Items from a Binary Heap</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1734" href="page362.html#SECTION0012300000000000000000">Leftist Heaps</a>
				<ul>
					<li>
						<a name="tex2html1735" href="page363.html#SECTION0012310000000000000000">Leftist Trees</a>
					</li>
					<li>
						<a name="tex2html1736" href="page364.html#SECTION0012320000000000000000">Implementation</a>
						<ul>
							<li>
								<a name="tex2html1737" href="page365.html#SECTION0012321000000000000000">Member Variables</a>
							</li>
							<li>
								<a name="tex2html1738" href="page366.html#SECTION0012322000000000000000">
									<tt>SwapContents</tt> Member Function</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1739" href="page367.html#SECTION0012330000000000000000">Merging Leftist Heaps</a>
					</li>
					<li>
						<a name="tex2html1740" href="page368.html#SECTION0012340000000000000000">Putting Items into a Leftist Heap</a>
					</li>
					<li>
						<a name="tex2html1741" href="page369.html#SECTION0012350000000000000000">Removing Items from a Leftist Heap</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1742" href="page370.html#SECTION0012400000000000000000">Binomial Queues</a>
				<ul>
					<li>
						<a name="tex2html1743" href="page371.html#SECTION0012410000000000000000">Binomial Trees</a>
					</li>
					<li>
						<a name="tex2html1744" href="page372.html#SECTION0012420000000000000000">Binomial Queues</a>
					</li>
					<li>
						<a name="tex2html1745" href="page373.html#SECTION0012430000000000000000">Implementation</a>
						<ul>
							<li>
								<a name="tex2html1746" href="page374.html#SECTION0012431000000000000000">Heap-Ordered Binomial Trees</a>
							</li>
							<li>
								<a name="tex2html1747" href="page375.html#SECTION0012432000000000000000">Binomial Queues</a>
							</li>
							<li>
								<a name="tex2html1748" href="page376.html#SECTION0012433000000000000000">Member Variables</a>
							</li>
							<li>
								<a name="tex2html1749" href="page377.html#SECTION0012434000000000000000">
									<tt>AddTree</tt> and <tt>RemoveTree</tt>
								</a>
							</li>
							<li>
								<a name="tex2html1750" href="page378.html#SECTION0012435000000000000000">
									<tt>FindMinTree</tt> and <tt>FindMin</tt> Member Functions</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1751" href="page379.html#SECTION0012440000000000000000">Merging Binomial Queues</a>
					</li>
					<li>
						<a name="tex2html1752" href="page380.html#SECTION0012450000000000000000">Putting Items into a Binomial Queue</a>
					</li>
					<li>
						<a name="tex2html1753" href="page381.html#SECTION0012460000000000000000">Removing an Item from a Binomial Queue</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1754" href="page382.html#SECTION0012500000000000000000">Applications</a>
				<ul>
					<li>
						<a name="tex2html1755" href="page383.html#SECTION0012510000000000000000">Discrete Event Simulation</a>
					</li>
					<li>
						<a name="tex2html1756" href="page384.html#SECTION0012520000000000000000">Implementation</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1757" href="page385.html#SECTION0012600000000000000000">Exercises</a>
			</li>
			<li>
				<a name="tex2html1758" href="page386.html#SECTION0012700000000000000000">Projects</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1759" href="page387.html#SECTION0013000000000000000000">Sets, Multisets and Partitions</a>
		<ul>
			<li>
				<a name="tex2html1760" href="page388.html#SECTION0013100000000000000000">Basics</a>
				<ul>
					<li>
						<a name="tex2html1761" href="page389.html#SECTION0013110000000000000000">Implementing Sets</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1762" href="page390.html#SECTION0013200000000000000000">Array and Bit-Vector Sets</a>
				<ul>
					<li>
						<a name="tex2html1763" href="page391.html#SECTION0013201000000000000000">Basic Operations</a>
					</li>
					<li>
						<a name="tex2html1764" href="page392.html#SECTION0013202000000000000000">Union, Intersection and Difference</a>
					</li>
					<li>
						<a name="tex2html1765" href="page393.html#SECTION0013203000000000000000">Comparing Sets</a>
					</li>
					<li>
						<a name="tex2html1766" href="page394.html#SECTION0013210000000000000000">Bit-Vector Sets</a>
						<ul>
							<li>
								<a name="tex2html1767" href="page395.html#SECTION0013211000000000000000">Basic Operations</a>
							</li>
							<li>
								<a name="tex2html1768" href="page396.html#SECTION0013212000000000000000">Union, Intersection and Difference</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1769" href="page397.html#SECTION0013300000000000000000">Multisets</a>
				<ul>
					<li>
						<a name="tex2html1770" href="page398.html#SECTION0013310000000000000000">Array Implementation</a>
						<ul>
							<li>
								<a name="tex2html1771" href="page399.html#SECTION0013311000000000000000">Basic Operations</a>
							</li>
							<li>
								<a name="tex2html1772" href="page400.html#SECTION0013312000000000000000">Union, Intersection and Difference</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1773" href="page401.html#SECTION0013320000000000000000">Linked List Implementation</a>
						<ul>
							<li>
								<a name="tex2html1774" href="page402.html#SECTION0013321000000000000000">Union</a>
							</li>
							<li>
								<a name="tex2html1775" href="page403.html#SECTION0013322000000000000000">Intersection</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1776" href="page404.html#SECTION0013400000000000000000">Partitions</a>
				<ul>
					<li>
						<a name="tex2html1777" href="page405.html#SECTION0013401000000000000000">Representing Partitions</a>
					</li>
					<li>
						<a name="tex2html1778" href="page406.html#SECTION0013410000000000000000">Implementing a Partition using a Forest</a>
						<ul>
							<li>
								<a name="tex2html1779" href="page407.html#SECTION0013411000000000000000">Implementation</a>
							</li>
							<li>
								<a name="tex2html1780" href="page408.html#SECTION0013412000000000000000">Constructors and Destructor</a>
							</li>
							<li>
								<a name="tex2html1781" href="page409.html#SECTION0013413000000000000000">
									<tt>Find</tt> and <tt>Join</tt> Member Functions</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1782" href="page410.html#SECTION0013420000000000000000">Collapsing Find</a>
					</li>
					<li>
						<a name="tex2html1783" href="page411.html#SECTION0013430000000000000000">Union by Size</a>
					</li>
					<li>
						<a name="tex2html1784" href="page412.html#SECTION0013440000000000000000">Union by Height or Rank</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1785" href="page413.html#SECTION0013500000000000000000">Applications</a>
			</li>
			<li>
				<a name="tex2html1786" href="page414.html#SECTION0013600000000000000000">Exercises</a>
			</li>
			<li>
				<a name="tex2html1787" href="page415.html#SECTION0013700000000000000000">Projects</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1788" href="page416.html#SECTION0014000000000000000000">Dynamic Storage Allocation: The Other Kind of Heap</a>
		<ul>
			<li>
				<a name="tex2html1789" href="page417.html#SECTION0014100000000000000000">Basics</a>
				<ul>
					<li>
						<a name="tex2html1790" href="page418.html#SECTION0014110000000000000000">C++ Magic</a>
						<ul>
							<li>
								<a name="tex2html1791" href="page419.html#SECTION0014111000000000000000">Working with Multiple Storage Pools</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1792" href="page420.html#SECTION0014120000000000000000">The Heap</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1793" href="page421.html#SECTION0014200000000000000000">Singly Linked Free Storage</a>
				<ul>
					<li>
						<a name="tex2html1794" href="page422.html#SECTION0014210000000000000000">Implementation</a>
						<ul>
							<li>
								<a name="tex2html1795" href="page423.html#SECTION0014211000000000000000">Constructor and Destructor</a>
							</li>
							<li>
								<a name="tex2html1796" href="page424.html#SECTION0014212000000000000000">Acquiring an Area</a>
							</li>
							<li>
								<a name="tex2html1797" href="page425.html#SECTION0014213000000000000000">Releasing an Area</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1798" href="page426.html#SECTION0014300000000000000000">Doubly Linked Free Storage</a>
				<ul>
					<li>
						<a name="tex2html1799" href="page427.html#SECTION0014310000000000000000">Implementation</a>
						<ul>
							<li>
								<a name="tex2html1800" href="page428.html#SECTION0014311000000000000000">Constructor and Destructor</a>
							</li>
							<li>
								<a name="tex2html1801" href="page429.html#SECTION0014312000000000000000">Releasing an Area</a>
							</li>
							<li>
								<a name="tex2html1802" href="page430.html#SECTION0014313000000000000000">Acquiring an Area</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1803" href="page431.html#SECTION0014400000000000000000">Buddy System for Storage Management</a>
				<ul>
					<li>
						<a name="tex2html1804" href="page432.html#SECTION0014410000000000000000">Implementation</a>
						<ul>
							<li>
								<a name="tex2html1805" href="page433.html#SECTION0014411000000000000000">Constructor and Destructor</a>
							</li>
							<li>
								<a name="tex2html1806" href="page434.html#SECTION0014412000000000000000">Acquiring an Area</a>
							</li>
							<li>
								<a name="tex2html1807" href="page435.html#SECTION0014413000000000000000">Releasing an Area</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1808" href="page436.html#SECTION0014500000000000000000">Applications</a>
				<ul>
					<li>
						<a name="tex2html1809" href="page437.html#SECTION0014510000000000000000">Implementation</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1810" href="page438.html#SECTION0014600000000000000000">Exercises</a>
			</li>
			<li>
				<a name="tex2html1811" href="page439.html#SECTION0014700000000000000000">Projects</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1812" href="page440.html#SECTION0015000000000000000000">Algorithmic Patterns and Problem Solvers</a>
		<ul>
			<li>
				<a name="tex2html1813" href="page441.html#SECTION0015100000000000000000">Brute-Force and Greedy Algorithms</a>
				<ul>
					<li>
						<a name="tex2html1814" href="page442.html#SECTION0015110000000000000000">Example-Counting Change</a>
						<ul>
							<li>
								<a name="tex2html1815" href="page443.html#SECTION0015111000000000000000">Brute-Force Algorithm</a>
							</li>
							<li>
								<a name="tex2html1816" href="page444.html#SECTION0015112000000000000000">Greedy Algorithm</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1817" href="page445.html#SECTION0015120000000000000000">Example-0/1 Knapsack Problem</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1818" href="page446.html#SECTION0015200000000000000000">Backtracking Algorithms</a>
				<ul>
					<li>
						<a name="tex2html1819" href="page447.html#SECTION0015210000000000000000">Example-Balancing Scales</a>
					</li>
					<li>
						<a name="tex2html1820" href="page448.html#SECTION0015220000000000000000">Representing the Solution Space</a>
					</li>
					<li>
						<a name="tex2html1821" href="page449.html#SECTION0015230000000000000000">Abstract Backtracking Solvers</a>
						<ul>
							<li>
								<a name="tex2html1822" href="page450.html#SECTION0015231000000000000000">Depth-First Solver</a>
							</li>
							<li>
								<a name="tex2html1823" href="page451.html#SECTION0015232000000000000000">Breadth-First Solver</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1824" href="page452.html#SECTION0015240000000000000000">Branch-and-Bound Solvers</a>
						<ul>
							<li>
								<a name="tex2html1825" href="page453.html#SECTION0015241000000000000000">Depth-First, Branch-and-Bound Solver</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1826" href="page454.html#SECTION0015250000000000000000">Example-0/1 Knapsack Problem Again</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1827" href="page455.html#SECTION0015300000000000000000">Top-Down Algorithms: Divide-and-Conquer</a>
				<ul>
					<li>
						<a name="tex2html1828" href="page456.html#SECTION0015310000000000000000">Example-Binary Search</a>
					</li>
					<li>
						<a name="tex2html1829" href="page457.html#SECTION0015320000000000000000">Example-Computing Fibonacci Numbers</a>
					</li>
					<li>
						<a name="tex2html1830" href="page458.html#SECTION0015330000000000000000">Example-Merge Sorting</a>
					</li>
					<li>
						<a name="tex2html1831" href="page459.html#SECTION0015340000000000000000">Running Time of Divide-and-Conquer Algorithms</a>
						<ul>
							<li>
								<a name="tex2html1832" href="page460.html#SECTION0015340100000000000000">Case 1 ( <img alt="tex2html_wrap_inline68825" src="img1902.gif" height="27" width="42" align="MIDDLE"/>)</a>
							</li>
							<li>
								<a name="tex2html1833" href="page461.html#SECTION0015340200000000000000">Case 2 ( <img alt="tex2html_wrap_inline68839" src="img1908.gif" height="13" width="42" align="BOTTOM"/>)</a>
							</li>
							<li>
								<a name="tex2html1834" href="page462.html#SECTION0015340300000000000000">Case 3 ( <img alt="tex2html_wrap_inline68849" src="img1911.gif" height="27" width="43" align="MIDDLE"/>)</a>
							</li>
							<li>
								<a name="tex2html1835" href="page463.html#SECTION0015340400000000000000">Summary</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1836" href="page464.html#SECTION0015350000000000000000">Example-Matrix Multiplication</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1837" href="page465.html#SECTION0015400000000000000000">Bottom-Up Algorithms: Dynamic<br/> Programming</a>
				<ul>
					<li>
						<a name="tex2html1838" href="page466.html#SECTION0015410000000000000000">Example-Generalized Fibonacci Numbers</a>
					</li>
					<li>
						<a name="tex2html1839" href="page467.html#SECTION0015420000000000000000">Example-Computing Binomial Coefficients</a>
					</li>
					<li>
						<a name="tex2html1840" href="page468.html#SECTION0015430000000000000000">Application: Typesetting Problem</a>
						<ul>
							<li>
								<a name="tex2html1841" href="page469.html#SECTION0015431000000000000000">Example</a>
							</li>
							<li>
								<a name="tex2html1842" href="page470.html#SECTION0015432000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1843" href="page471.html#SECTION0015500000000000000000">Randomized Algorithms</a>
				<ul>
					<li>
						<a name="tex2html1844" href="page472.html#SECTION0015510000000000000000">Generating Random Numbers</a>
						<ul>
							<li>
								<a name="tex2html1845" href="page473.html#SECTION0015511000000000000000">The Minimal Standard Random Number Generator</a>
							</li>
							<li>
								<a name="tex2html1846" href="page474.html#SECTION0015512000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1847" href="page475.html#SECTION0015520000000000000000">Random Variables</a>
						<ul>
							<li>
								<a name="tex2html1848" href="page476.html#SECTION0015521000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1849" href="page477.html#SECTION0015530000000000000000">Monte Carlo Methods</a>
						<ul>
							<li>
								<a name="tex2html1850" href="page478.html#SECTION0015531000000000000000">Example-Computing  <img alt="tex2html_wrap_inline69477" src="img2047.gif" height="7" width="9" align="BOTTOM"/>
								</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1851" href="page479.html#SECTION0015540000000000000000">Simulated Annealing</a>
						<ul>
							<li>
								<a name="tex2html1852" href="page480.html#SECTION0015541000000000000000">Example-Balancing Scales</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1853" href="page481.html#SECTION0015600000000000000000">Exercises</a>
			</li>
			<li>
				<a name="tex2html1854" href="page482.html#SECTION0015700000000000000000">Projects</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1855" href="page483.html#SECTION0016000000000000000000">Sorting Algorithms and Sorters</a>
		<ul>
			<li>
				<a name="tex2html1856" href="page484.html#SECTION0016100000000000000000">Basics</a>
			</li>
			<li>
				<a name="tex2html1857" href="page485.html#SECTION0016200000000000000000">Sorting and Sorters</a>
				<ul>
					<li>
						<a name="tex2html1858" href="page486.html#SECTION0016201000000000000000">Sorter Class Hierarchy</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1859" href="page487.html#SECTION0016300000000000000000">Insertion Sorting</a>
				<ul>
					<li>
						<a name="tex2html1860" href="page488.html#SECTION0016310000000000000000">Straight Insertion Sort</a>
						<ul>
							<li>
								<a name="tex2html1861" href="page489.html#SECTION0016311000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1862" href="page490.html#SECTION0016320000000000000000">Average Running Time</a>
					</li>
					<li>
						<a name="tex2html1863" href="page491.html#SECTION0016330000000000000000">Binary Insertion Sort</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1864" href="page492.html#SECTION0016400000000000000000">Exchange Sorting</a>
				<ul>
					<li>
						<a name="tex2html1865" href="page493.html#SECTION0016410000000000000000">Bubble Sort</a>
					</li>
					<li>
						<a name="tex2html1866" href="page494.html#SECTION0016420000000000000000">Quicksort</a>
						<ul>
							<li>
								<a name="tex2html1867" href="page495.html#SECTION0016421000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1868" href="page496.html#SECTION0016430000000000000000">Running Time Analysis</a>
						<ul>
							<li>
								<a name="tex2html1869" href="page497.html#SECTION0016431000000000000000">Worst-Case Running Time</a>
							</li>
							<li>
								<a name="tex2html1870" href="page498.html#SECTION0016432000000000000000">Best-Case Running Time</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1871" href="page499.html#SECTION0016440000000000000000">Average Running Time</a>
					</li>
					<li>
						<a name="tex2html1872" href="page500.html#SECTION0016450000000000000000">Selecting the Pivot</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1873" href="page501.html#SECTION0016500000000000000000">Selection Sorting</a>
				<ul>
					<li>
						<a name="tex2html1874" href="page502.html#SECTION0016510000000000000000">Straight Selection Sorting</a>
						<ul>
							<li>
								<a name="tex2html1875" href="page503.html#SECTION0016511000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1876" href="page504.html#SECTION0016520000000000000000">Sorting with a Heap</a>
						<ul>
							<li>
								<a name="tex2html1877" href="page505.html#SECTION0016521000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1878" href="page506.html#SECTION0016530000000000000000">Building the Heap</a>
						<ul>
							<li>
								<a name="tex2html1879" href="page507.html#SECTION0016531000000000000000">Running Time Analysis</a>
							</li>
							<li>
								<a name="tex2html1880" href="page508.html#SECTION0016532000000000000000">The Sorting Phase</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1881" href="page509.html#SECTION0016600000000000000000">Merge Sorting</a>
				<ul>
					<li>
						<a name="tex2html1882" href="page510.html#SECTION0016601000000000000000">Implementation</a>
					</li>
					<li>
						<a name="tex2html1883" href="page511.html#SECTION0016602000000000000000">Merging</a>
					</li>
					<li>
						<a name="tex2html1884" href="page512.html#SECTION0016603000000000000000">Two-Way Merge Sorting</a>
					</li>
					<li>
						<a name="tex2html1885" href="page513.html#SECTION0016604000000000000000">Running Time Analysis</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1886" href="page514.html#SECTION0016700000000000000000">A Lower Bound on Sorting</a>
			</li>
			<li>
				<a name="tex2html1887" href="page515.html#SECTION0016800000000000000000">Distribution Sorting</a>
				<ul>
					<li>
						<a name="tex2html1888" href="page516.html#SECTION0016810000000000000000">Bucket Sort</a>
						<ul>
							<li>
								<a name="tex2html1889" href="page517.html#SECTION0016811000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1890" href="page518.html#SECTION0016820000000000000000">Radix Sort</a>
						<ul>
							<li>
								<a name="tex2html1891" href="page519.html#SECTION0016821000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1892" href="page520.html#SECTION0016900000000000000000">Performance Data</a>
			</li>
			<li>
				<a name="tex2html1893" href="page521.html#SECTION00161000000000000000000">Exercises</a>
			</li>
			<li>
				<a name="tex2html1894" href="page522.html#SECTION00161100000000000000000">Projects</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1895" href="page523.html#SECTION0017000000000000000000">Graphs  and Graph Algorithms</a>
		<ul>
			<li>
				<a name="tex2html1896" href="page524.html#SECTION0017100000000000000000">Basics</a>
				<ul>
					<li>
						<a name="tex2html1897" href="page525.html#SECTION0017101000000000000000">Directed Graphs</a>
					</li>
					<li>
						<a name="tex2html1898" href="page526.html#SECTION0017102000000000000000">Terminology</a>
					</li>
					<li>
						<a name="tex2html1899" href="page527.html#SECTION0017103000000000000000">More Terminology</a>
					</li>
					<li>
						<a name="tex2html1900" href="page528.html#SECTION0017104000000000000000">Directed Acyclic Graphs</a>
					</li>
					<li>
						<a name="tex2html1901" href="page529.html#SECTION0017105000000000000000">Undirected Graphs</a>
					</li>
					<li>
						<a name="tex2html1902" href="page530.html#SECTION0017106000000000000000">Terminology</a>
					</li>
					<li>
						<a name="tex2html1903" href="page531.html#SECTION0017107000000000000000">Labeled Graphs</a>
					</li>
					<li>
						<a name="tex2html1904" href="page532.html#SECTION0017110000000000000000">Representing Graphs</a>
						<ul>
							<li>
								<a name="tex2html1905" href="page533.html#SECTION0017111000000000000000">Adjacency Matrices</a>
							</li>
							<li>
								<a name="tex2html1906" href="page534.html#SECTION0017112000000000000000">Sparse vs. Dense Graphs</a>
							</li>
							<li>
								<a name="tex2html1907" href="page535.html#SECTION0017113000000000000000">Adjacency Lists</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1908" href="page536.html#SECTION0017200000000000000000">Implementing Graphs</a>
				<ul>
					<li>
						<a name="tex2html1909" href="page537.html#SECTION0017210000000000000000">Implementing Vertices</a>
					</li>
					<li>
						<a name="tex2html1910" href="page538.html#SECTION0017220000000000000000">Implementing Edges</a>
					</li>
					<li>
						<a name="tex2html1911" href="page539.html#SECTION0017230000000000000000">Abstract Graphs and Digraphs</a>
						<ul>
							<li>
								<a name="tex2html1912" href="page540.html#SECTION0017231000000000000000">Accessors and Mutators</a>
							</li>
							<li>
								<a name="tex2html1913" href="page541.html#SECTION0017232000000000000000">Iterators</a>
							</li>
							<li>
								<a name="tex2html1914" href="page542.html#SECTION0017233000000000000000">Graph Traversals</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1915" href="page543.html#SECTION0017240000000000000000">Implementing Undirected Graphs</a>
						<ul>
							<li>
								<a name="tex2html1916" href="page544.html#SECTION0017241000000000000000">Using Adjacency Matrices</a>
							</li>
							<li>
								<a name="tex2html1917" href="page545.html#SECTION0017242000000000000000">Using Adjacency Lists</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1918" href="page546.html#SECTION0017250000000000000000">Edge-Weighted and Vertex-Weighted Graphs</a>
					</li>
					<li>
						<a name="tex2html1919" href="page547.html#SECTION0017260000000000000000">Comparison of Graph Representations</a>
						<ul>
							<li>
								<a name="tex2html1920" href="page548.html#SECTION0017261000000000000000">Space Comparison</a>
							</li>
							<li>
								<a name="tex2html1921" href="page549.html#SECTION0017262000000000000000">Time Comparison</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1922" href="page550.html#SECTION0017300000000000000000">Graph Traversals</a>
				<ul>
					<li>
						<a name="tex2html1923" href="page551.html#SECTION0017310000000000000000">Depth-First Traversal</a>
						<ul>
							<li>
								<a name="tex2html1924" href="page552.html#SECTION0017311000000000000000">Implementation</a>
							</li>
							<li>
								<a name="tex2html1925" href="page553.html#SECTION0017312000000000000000">Running Time Analysis</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1926" href="page554.html#SECTION0017320000000000000000">Breadth-First Traversal</a>
						<ul>
							<li>
								<a name="tex2html1927" href="page555.html#SECTION0017321000000000000000">Implementation</a>
							</li>
							<li>
								<a name="tex2html1928" href="page556.html#SECTION0017322000000000000000">Running Time Analysis</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1929" href="page557.html#SECTION0017330000000000000000">Topological Sort</a>
						<ul>
							<li>
								<a name="tex2html1930" href="page558.html#SECTION0017331000000000000000">Implementation</a>
							</li>
							<li>
								<a name="tex2html1931" href="page559.html#SECTION0017332000000000000000">Running Time Analysis</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1932" href="page560.html#SECTION0017340000000000000000">Graph Traversal Applications:<br/> Testing for Cycles and Connectedness</a>
						<ul>
							<li>
								<a name="tex2html1933" href="page561.html#SECTION0017341000000000000000">Connectedness of an Undirected Graph</a>
							</li>
							<li>
								<a name="tex2html1934" href="page562.html#SECTION0017342000000000000000">Connectedness of a Directed Graph</a>
							</li>
							<li>
								<a name="tex2html1935" href="page563.html#SECTION0017343000000000000000">Testing for Cycles in a Directed Graph</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1936" href="page564.html#SECTION0017400000000000000000">Shortest-Path Algorithms</a>
				<ul>
					<li>
						<a name="tex2html1937" href="page565.html#SECTION0017410000000000000000">Single-Source Shortest Path</a>
						<ul>
							<li>
								<a name="tex2html1938" href="page566.html#SECTION0017411000000000000000">Dijkstra's Algorithm</a>
							</li>
							<li>
								<a name="tex2html1939" href="page567.html#SECTION0017412000000000000000">Data Structures for Dijkstra's Algorithm</a>
							</li>
							<li>
								<a name="tex2html1940" href="page568.html#SECTION0017413000000000000000">Implementation</a>
							</li>
							<li>
								<a name="tex2html1941" href="page569.html#SECTION0017414000000000000000">Running Time Analysis</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1942" href="page570.html#SECTION0017420000000000000000">All-Pairs Source Shortest Path</a>
						<ul>
							<li>
								<a name="tex2html1943" href="page571.html#SECTION0017421000000000000000">Floyd's Algorithm</a>
							</li>
							<li>
								<a name="tex2html1944" href="page572.html#SECTION0017422000000000000000">Implementation</a>
							</li>
							<li>
								<a name="tex2html1945" href="page573.html#SECTION0017423000000000000000">Running Time Analysis</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1946" href="page574.html#SECTION0017500000000000000000">Minimum-Cost Spanning Trees</a>
				<ul>
					<li>
						<a name="tex2html1947" href="page575.html#SECTION0017501000000000000000">Constructing Spanning Trees</a>
					</li>
					<li>
						<a name="tex2html1948" href="page576.html#SECTION0017502000000000000000">Minimum-Cost Spanning Trees</a>
					</li>
					<li>
						<a name="tex2html1949" href="page577.html#SECTION0017510000000000000000">Prim's Algorithm</a>
						<ul>
							<li>
								<a name="tex2html1950" href="page578.html#SECTION0017511000000000000000">Implementation</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1951" href="page579.html#SECTION0017520000000000000000">Kruskal's Algorithm</a>
						<ul>
							<li>
								<a name="tex2html1952" href="page580.html#SECTION0017521000000000000000">Implementation</a>
							</li>
							<li>
								<a name="tex2html1953" href="page581.html#SECTION0017522000000000000000">Running Time Analysis</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1954" href="page582.html#SECTION0017600000000000000000">Application: Critical Path Analysis</a>
				<ul>
					<li>
						<a name="tex2html1955" href="page583.html#SECTION0017601000000000000000">Implementation</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1956" href="page584.html#SECTION0017700000000000000000">Exercises</a>
			</li>
			<li>
				<a name="tex2html1957" href="page585.html#SECTION0017800000000000000000">Projects</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1958" href="page586.html#SECTION0018000000000000000000">C++ and Object-Oriented Programming</a>
		<ul>
			<li>
				<a name="tex2html1959" href="page587.html#SECTION0018100000000000000000">Variables, Pointers and References</a>
				<ul>
					<li>
						<a name="tex2html1960" href="page588.html#SECTION0018110000000000000000">Pointers Are Variables</a>
						<ul>
							<li>
								<a name="tex2html1961" href="page589.html#SECTION0018111000000000000000">Dereferencing Pointers</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1962" href="page590.html#SECTION0018120000000000000000">References are Not Variables</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1963" href="page591.html#SECTION0018200000000000000000">Parameter Passing</a>
				<ul>
					<li>
						<a name="tex2html1964" href="page592.html#SECTION0018210000000000000000">Pass By Value</a>
					</li>
					<li>
						<a name="tex2html1965" href="page593.html#SECTION0018220000000000000000">Pass By Reference</a>
						<ul>
							<li>
								<a name="tex2html1966" href="page594.html#SECTION0018221000000000000000">The Trade-off</a>
							</li>
							<li>
								<a name="tex2html1967" href="page595.html#SECTION0018222000000000000000">Constant Parameters</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1968" href="page596.html#SECTION0018300000000000000000">Objects and Classes</a>
				<ul>
					<li>
						<a name="tex2html1969" href="page597.html#SECTION0018310000000000000000">Member Variables and Member Functions</a>
					</li>
					<li>
						<a name="tex2html1970" href="page598.html#SECTION0018320000000000000000">Constructors and Destructors</a>
						<ul>
							<li>
								<a name="tex2html1971" href="page599.html#SECTION0018321000000000000000">Default Constructor</a>
							</li>
							<li>
								<a name="tex2html1972" href="page600.html#SECTION0018322000000000000000">Copy Constructor</a>
							</li>
							<li>
								<a name="tex2html1973" href="page601.html#SECTION0018323000000000000000">The Copy Constructor, Parameter Passing
and Function Return Values</a>
							</li>
							<li>
								<a name="tex2html1974" href="page602.html#SECTION0018324000000000000000">Destructors</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1975" href="page603.html#SECTION0018330000000000000000">Accessors and Mutators</a>
						<ul>
							<li>
								<a name="tex2html1976" href="page604.html#SECTION0018331000000000000000">Mutators</a>
							</li>
							<li>
								<a name="tex2html1977" href="page605.html#SECTION0018332000000000000000">Member Access Control</a>
							</li>
						</ul>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1978" href="page606.html#SECTION0018400000000000000000">Inheritance and Polymorphism</a>
				<ul>
					<li>
						<a name="tex2html1979" href="page607.html#SECTION0018410000000000000000">Derivation and Inheritance</a>
						<ul>
							<li>
								<a name="tex2html1980" href="page608.html#SECTION0018411000000000000000">Derivation and Access Control</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1981" href="page609.html#SECTION0018420000000000000000">Polymorphism</a>
						<ul>
							<li>
								<a name="tex2html1982" href="page610.html#SECTION0018421000000000000000">Virtual Member Functions</a>
							</li>
							<li>
								<a name="tex2html1983" href="page611.html#SECTION0018422000000000000000">Abstract Classes and Concrete Classes</a>
							</li>
							<li>
								<a name="tex2html1984" href="page612.html#SECTION0018423000000000000000">Algorithmic Abstraction</a>
							</li>
						</ul>
					</li>
					<li>
						<a name="tex2html1985" href="page613.html#SECTION0018430000000000000000">Multiple Inheritance</a>
					</li>
					<li>
						<a name="tex2html1986" href="page614.html#SECTION0018440000000000000000">Run-Time Type Information and Casts</a>
					</li>
				</ul>
			</li>
			<li>
				<a name="tex2html1987" href="page615.html#SECTION0018500000000000000000">Templates</a>
			</li>
			<li>
				<a name="tex2html1988" href="page616.html#SECTION0018600000000000000000">Exceptions</a>
			</li>
		</ul>
	</li>
	<li>
		<a name="tex2html1989" href="page617.html#SECTION0019000000000000000000">Class Hierarchy Diagrams</a>
	</li>
	<li>
		<a name="tex2html1990" href="page618.html#SECTION0020000000000000000000">Character Codes</a>
	</li>
	<li>
		<a name="tex2html1991" href="page619.html#SECTION0021000000000000000000">References</a>
	</li>
	<li>
		<a name="tex2html1992" href="page620.html#SECTION0022000000000000000000">Index</a>
	</li>
</ul>
"""

bs = BookScraper(None, htmlText)
bs.setBasePath("http://www.brpreiss.com/books/opus4/html/")
bs.setBookTitle("Data Structures and Algorithms with Object-Oriented Design Patterns in C++")
bs.setAuthor("Bruno R. Preiss")
print("BookScraper object = " + str(bs))
#    print "BookScraper object = ", BookScraper
    ###  if len(sys.argv) > 1 and sys.argv[1] == "export":
bs.parse_toc_brpreiss()
bs.generatePathsAndFolders()
#pdb.set_trace()
bs.export_html()
#pdb.set_trace()
