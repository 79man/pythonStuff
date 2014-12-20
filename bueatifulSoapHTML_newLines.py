from bs4.dammit import EntitySubstitution
def uppercase_and_substitute_html_entities(string):
    #string = string.encode('utf-8')
    HTMFormatted = EntitySubstitution.substitute_html(string)
    HTMFormatted = HTMFormatted.replace('\n', '')
    #print "str = [", string , "] HTMFormatted = [", HTMFormatted, "]"
    return HTMFormatted

soupy = BeautifulSoup(htmlText)

sec, footer = soupy.findAll("hr")
if(footer is not None):    
#    print "str(footer) = ", str(footer), "BeautifulSoup() = ", BeautifulSoup(str(footer))
    print "----------------------------------------------------------------------------"
#    print "footer.prettify() = ", footer.prettify(), "BeautifulSoup() = ", BeautifulSoup(footer.prettify())
    print "----------------------------------------------------------------------------"
    print "footer.prettify(formatter=uppercase_and_substitute_html_entities) = ", footer.prettify(formatter=uppercase_and_substitute_html_entities), "BeautifulSoup() = ", BeautifulSoup(footer.prettify(formatter=uppercase_and_substitute_html_entities))
    print "----------------------------------------------------------------------------"
    #logger.flush()
    footer.extract()
    footerContents = ""
    for tag in footer.findAll() :
        footerContents = footerContents + tag.prettify(formatter=uppercase_and_substitute_html_entities)
    
    print "footerContents(1) = [", footerContents, "]"
    #logger.flush()
    
for tag in sec.findAll() :
#    print "[", tag.prettify(formatter=uppercase_and_substitute_html_entities), "]"
    print "-----------------------------------------------------"    
    footerContents = footerContents + tag.prettify(formatter=uppercase_and_substitute_html_entities)
    
print "footerContents(2) = [", footerContents, "]"   
#logger.flush()    
    
chapterTemplate="<html><head><title>{ch_no}. {chapter}</title></head><body><h1>{chapter}</h1>{content}</body></html>"
    
with open("abcd.html", "w") as fn:
    footerContents = chapterTemplate.format(
        ch_no=100,
        chapter="footer",
        content=footerContents.encode('utf-8')
    )
    fn.write(footerContents)

#print "str(sec) = ", str(sec)
