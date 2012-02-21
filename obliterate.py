import pdb
import pickle
import urllib2
import urllib
import re
import os.path
import cookielib
import microdom

# This module uses the poster library that can do multipart HTTP POSTs
# To install, use: easy_install poster
# http://atlee.ca/software/poster/
import poster
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

# You must set these variables
SERVER = "http://your.wiki.com/"
USER   = "Admin"
PW     = "yourpw"
SAVEUSERS = ["MediaWiki spam cleanup","Admin","Wikiadmin","Bot"]

API    = "api.php"

token = None

def logout(opener):
  handle = opener.open(SERVER + API + "?format=xml&action=logout")
  t = handle.read()
  print t

def dictify(text):
  lst = text.split(" ")
  lst = filter(lambda x: "=" in x, lst)
  lkup = {}
  for l in lst:
      t1 = l.split("=")
      lkup[t1[0]]=t1[1].strip('"').strip("'")
  return lkup

def login(opener,user,pw):
  """Log in"""
  reqdata = urllib.urlencode({"format":"xml","action":"login","lgname":user})
  req = urllib2.Request(SERVER + API,reqdata)
  handle = opener.open(req)
  t = handle.read()
  lkup = dictify(t)
  #print t

  reqdata = urllib.urlencode({"lgtoken":lkup["token"],"format":"xml","action":"login","lgname":user,"lgpassword":pw})
  req = urllib2.Request(SERVER + API,reqdata)
  handle = opener.open(req)
  t = handle.read()

  reqdata = urllib.urlencode({"action":"query","prop":"info","intoken":"edit","format":"xml","titles":"Main Page"})
  req = urllib2.Request(SERVER + API,reqdata)
  t = opener.open(req).read()
  print t
  params = dictify(t)
  global token
  token = params["edittoken"]

  #print t


def create(opener,title,text):
  """Create a page"""
  reqdata = urllib.urlencode({"action":"query","prop":"info","intoken":"edit","format":"xml","titles":title})
  req = urllib2.Request(SERVER + API,reqdata)
  t = opener.open(req).read()
  print t
  params = dictify(t)
  print params
  
  reqdata = urllib.urlencode({"action":"edit","format":"xml","token":params["edittoken"],"title":title,"text":text})
  req = urllib2.Request(SERVER + API,reqdata)
  handle = opener.open(req)
  t = handle.read()
  print t

def getUsers(opener):
  reqdata = urllib.urlencode({"action":"query","list":"allusers","aulimit":"5000","format":"xml"})
  req = urllib2.Request(SERVER + API,reqdata)
  t = opener.open(req).read()
  md = microdom.LoadString(t)
  return [str(x.name) for x in md['query']['allusers'].children()]
   
def getUserContribs(opener,user):
  reqdata = urllib.urlencode({"action":"query","list":"usercontribs","uclimit":"5000","ucuser":user, "format":"xml"})
  req = urllib2.Request(SERVER + API,reqdata)
  t = opener.open(req).read()
  md = microdom.LoadString(t)  
  return md['query']['usercontribs'].children()
    
def deletePage(opener,pageid):
  global token
  reqdata = urllib.urlencode({"action":"delete","pageid":str(pageid),"token":token,"reason":"olbliterate","format":"xml"})
  req = urllib2.Request(SERVER + API,reqdata)
  t = opener.open(req).read()
  #print t  
        
def undoPageRev(opener,title,rev):
  global token
  reqdata = urllib.urlencode({"action":"edit","title":str(title),"token":token,"reason":"olbliterate","undo":str(rev),"format":"xml"})
  req = urllib2.Request(SERVER + API,reqdata)
  t = opener.open(req).read()
  print t  
    

def Upload():
  """This routine uploads all the images, and then all the pages"""
  cj = cookielib.LWPCookieJar()

  opener = poster.streaminghttp.register_openers()
  opener.add_handler(urllib2.HTTPCookieProcessor(cj))
  login(opener,USER,PW)


  UploadImagesInDir(opener, "images/")
  UploadDictOfPages(opener)


def Test():
  """A unit test"""
  cj = cookielib.LWPCookieJar()
  opener = poster.streaminghttp.register_openers()
  opener.add_handler(urllib2.HTTPCookieProcessor(cj))

  # If you use standard python libs, you can't do multipart POSTS.
  # opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
  # opener.add_handler(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
  
  login(opener,USER,PW)
  users = getUsers(opener)
  for keep in SAVEUSERS:
    users.remove(keep)
  pdb.set_trace()
  for u in users:
    if not u in SAVEUSERS:
      print "User: %s" % u
      uc = getUserContribs(opener, u)
      for ch in uc:
        if ch.has_key("new"):
          print "  Deleting page: title: %s comment: %s" % (str(ch.title.encode("utf8")),str(ch.comment.encode("utf8")))
          deletePage(opener,int(ch.pageid))
        else:
          print str(ch)
          pdb.set_trace()
          undoPageRev(opener,ch.title,ch.revid)
  
  pdb.set_trace()
