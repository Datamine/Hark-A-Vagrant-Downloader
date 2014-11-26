# John Loeber | November 20 2014 | Python 2.7.8 | www.johnloeber.com
# Tool to download all _Hark a Vagrant!_ comics.

from bs4 import BeautifulSoup as bs
from shutil import copyfileobj
from os.path import exists
from os import makedirs
import requests

def makesoup(url):
    """
    Takes url, fetches html, turns it into a BS object
    """
    html = requests.get(url)
    soup = bs(html.content)
    return soup

def getPageLinks(url):
    """
    Given the _Hark a Vagrant!_ archive page, fetches all links.
    """
    soup = makesoup(url)
    links = soup.findAll('a')
    comiclinks = filter(lambda x: "?id=" in x, [i.get('href') for i in links])
    return map(lambda x: "http://harkavagrant.com/" + x, comiclinks)

def removehttps(url):
    """
    To replace https:// with http://
    """
    if "https" in url:
        return "http" + url[url.index(":"):]
    return url

def getComicLinks(links):
    """
    Given the individual page urls, scrape for the urls to the comics.
    """
    pics = []
    filterby = ["projectwonderful", "buttonabout.png", "buttonbook.png",
                "buttonstore.png", "vagrantheader.png", "buttonarchive.png",
                "buttontumblr.png", "buttonarchivebycategory.png",
                "buttonprevious.png", "buttonrandom.png", "buttonnext.png",
                "kateicon.png","paypalobjects"]
    for url in links:
        print "Parsing page: " + url
        soup = makesoup(url)
        images = soup.findAll('img')
        for i in images:
            src = i.get('src')
            if all ([(not t in src) for t in filterby]):
                pics.append(src)
    pics = map(removehttps,pics)
    return pics

def imageget(link,folder,index):
    """
    Actually downloads the image to the correct folder
    Using technique from http://stackoverflow.com/a/13137873
    """
    try:
        linkinv = link[::-1]
        extension = linkinv[:linkinv.index(".")][::-1]
        r = requests.get(link, stream=True)
        if r.status_code == 200:
            # length of index to three digits as there are about ~450 comics
            with open(folder+"/"+str("%03d" % index)+"."+extension, 'wb') as f:
                r.raw.decode_content = True
                copyfileobj(r.raw, f)
        else:
            print "Error encountered downloading: " + link
    except:
        print "Request error encountered on " + link+ ". Trying again."
        imageget(link,folder,index)
    return

def retrieve(links):
    """
    Given links to images, downloads them
    """
    for index, link in enumerate(links):
        print "Now retrieving image " + str(index)
        if "harkavagrant" in link:
            imageget(link,"original",index)
        else:
            imageget(link,"other",index)
    return
 
def checkdir(loc):
    """
    Given directory, checks if it exists. If not, then it makes the directory.
    """    
    if not exists(loc):
        makedirs(loc)
    return

def main():
    """
    Downloads all _Hark a Vagrant!_ comics
    """
    start = "http://www.harkavagrant.com/archive.php"
    pagelinks = getPageLinks(start)
    piclinks = getComicLinks(pagelinks)
    # one dir for harkavagrant-hosted images, and one dir for other ones
    checkdir("original")
    checkdir("other")
    retrieve(piclinks)

if __name__=='__main__':
    main()
