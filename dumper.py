"""
This program starts at a particular wiki page and recursively grabs everything
it links to, including images.
Images are stored in a directory, all pages are stored in a probably-huge
Python dictionary.  This dictionary is then "pickled" into a file.

The dumper uses the Special:Export system, NOT api.php so is usable on older
versions of mediawiki.

I did not need to login to read... if you need to log in, you can either
temporarily disable that in your mediawiki installation, OR look at
uploader.py to see an example of logging in.
"""
import pdb
import urllib2
import urllib
import re
import os.path

SERVER = "http://localhost:8080/"
INDEXPHP = "wiki/index.php"

count = 0
imagecount = 0

def grab(page):
  """Grabs the XML of a page using the 'Special:Export' page"""
  global count
  d = {"pages":page, "action":"submit"}
  args = urllib.urlencode(d)
  infile = urllib2.urlopen(SERVER + INDEXPHP + '/Special:Export',args) 
  pagetext = infile.read()
  count += len(pagetext)
  return pagetext

def grabImage(imname):
  global imagecount
  
  fname = imname[6:].strip()
  fname = fname.replace(' ', '_')
  if not os.path.exists("images/" + fname):

    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]  # Make it think we are a browser so it does not deny bots access.
    infile = opener.open(SERVER + INDEXPHP +  "?title=Image:%s&action=edit&externaledit=true&mode=file" % fname)
    page = infile.read()
    url = page.split()[-1].split("=")[1]
    infile = opener.open(url)
    data = infile.read()
    
    imagecount += len(data)

    # Write the file into a subdirectory labelled "images/" that you need to create.
    try:
      os.makedirs("images/")
    except Exception, e:
      pass
    f = open("images/" + fname,"w")
    f.write(data)
    f.close()   
  else:
    print "Already have %s" % fname

  return "images/" + fname


def pullDown(page,cache=None,indent=0,prior=None):
  """Recursive function to pull down a page and ALL subpages
  page: a string containing the mage title
  cache: a dictionary where I keep track of all pages pulled.  This dictionary will be returned a your final result
  indent: Just the recursion depth for pretty printing purposes.
  prior: If you already pulled some of the pages down, you can "seed" the system by passing that dictionary in this variable
  """
  global count
  if cache is None: cache = {}

  if cache.has_key(page): return

  if prior.has_key(page): pagetext = prior[page]
  else:  pagetext = grab(page)
  cache[page] = pagetext

  wikilink_rx = re.compile(r"\[\[(([^\]|]|\](?=[^\]]))*)(\|(([^\]]|\](?=[^\]]))*))?\]\]")

  for match in re.finditer(wikilink_rx,pagetext):    
    print "           " + "  "*indent + str(match.groups())
    newpage = match.groups()[0]
    newpage = newpage.strip(" ")
    if not cache.has_key(newpage):
     if newpage[0] != "#": # its an internal link otherwise
      if "#" in newpage:
        newpage = newpage.split("#")[0]
      print ("%10d " % count) + ("  "*indent) + ("Pulling %s" % newpage)
      if newpage[0:6].upper() == "IMAGE:":
        print ("%10d " % count) + ("  "*indent) + ("Get image %s" % newpage[6:])
        # Rip the Image: off and put it back on canonically
        cache["Image:%s" % newpage[6:].strip()] = grabImage(newpage)   
      pullDown(newpage,cache,indent+1,prior)
  
  return cache


everything = {}

def Test():
  import pickle  
  pdb.set_trace()
  # Did we do an abortive pull and so have some data?
  # If so, load it up so we don't pull it again.
  try:
    f = open("data.pkl","r")
    prior = pickle.load(f)
  except IOError:
    prior = {}

  try:
#    result = pullDown("<your title>",everything,prior=prior)
#    result = pullDown("<your title>",everything,prior=prior)
    result = pullDown("Main_Page",everything,prior=prior)
  finally:
    # Whatever happened, store what we've got to a file.
    f = open("data.pkl","w")
    pickle.dump(everything,f)
    f.close()

