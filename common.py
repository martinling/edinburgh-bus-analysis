import os, urllib, simplexml

def get(method, arg):
    filename = "cache/%s_%s.xml" % (method, arg)
    if not os.path.exists(filename):
        if not os.path.exists("cache"):
            os.mkdir("cache")
        url = "http://omnibus.subtlelogic.co.uk/%s/xml/%s/" % (method, arg)
        print "Retrieving", url
        result = urllib.urlopen(url)
        xmltext = result.read()
        file = open(filename, 'w')
        file.write(xmltext)
        file.close()
    xml = simplexml.parse(filename)
    return xml
