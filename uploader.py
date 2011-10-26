import pdb
import pickle
import urllib2
import urllib
import re
import os.path
import cookielib

# This module uses the poster library that can do multipart HTTP POSTs
# To install, use: easy_install poster
# http://atlee.ca/software/poster/
import poster
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

# You must set these variables
SERVER = "http://<www.yourserver.com>/"
USER   = "<username>"
PW     = "<password>"


API    = "api.php"

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

def importXmlApiPhp(opener,title,text):
  """Use the api.php method to import mediawiki xml that you exported from a different site"""
  reqdata = urllib.urlencode({"action":"query","prop":"info","intoken":"import","format":"xml","titles":title})
  req = urllib2.Request(SERVER + API,reqdata)
  t = opener.open(req).read()
  params = dictify(t)

  # Dump what is being imported for debugging
  #f = open("page/%s" % title.replace("/","_"), "w")
  #f.write(text)
  #f.close()

  fileParam = poster.encode.MultipartParam("xml",text,filename=title,filetype="text/xml",filesize=len(text))

  datagen, headers = multipart_encode([fileParam,("format","xml"),("action","import"),("token",params["importtoken"])])
  req = urllib2.Request(SERVER + API,datagen,headers)
  
  #reqdata = urllib.urlencode({"action":"import","format":"xml","token":params["importtoken"],"summary":"","xml":text})
  #req = urllib2.Request(SERVER + API,reqdata)
  
  handle = opener.open(req)
  t = handle.read()
  print "Title '%s'  Result: %s" % (title,t)

def importXml(opener,title,text):
  """I didn't text this one because the api.php version worked"""
  reqdata = urllib.urlencode({"action":"query","prop":"info","intoken":"import","format":"xml","titles":title})
  req = urllib2.Request(SERVER + API,reqdata)
  t = opener.open(req).read()
  params = dictify(t)

  fileParam = poster.encode.MultipartParam("xmlimport",text,filename=title,filetype="text/xml",filesize=len(text))

  datagen, headers = multipart_encode([fileParam,("action","submit"),("format","xml"),("source","upload"),("log-comment",""),("edittoken",params["importtoken"])])
  req = urllib2.Request(SERVER + "index.php?title=Special:Import",datagen,headers)
   
  handle = opener.open(req)
  t = handle.read()
  print t


def createImage(opener,title,filen):
  """Upload an image file"""
  f = open(filen, "rb")
  data = f.read()
  f.close()
  n,ext = os.path.splitext(filen)
  if ext.upper() == ".PNG":
      mimetype = "image/png"
  elif ext.upper() == ".JPG" or ext.upper() == ".JPEG":
      mimetype = "image/jpeg"
  elif ext.upper() == ".GIF":
      mimetype = "image/gif"
  else:
      print "\n!!NOT HANDLED %s!!\n" % filen
      return False  # Not an image I handle
  
  fileParam = poster.encode.MultipartParam("wpUploadFile",data,filename=title,filetype="image/png",filesize=len(data))
  datagen, headers = multipart_encode([fileParam,("wpWatchthis",'false'),("wpIgnoreWarning","true"),("wpDestFileWarningAck",""),("wpForReUpload",""),("wpUploadDescription",""),("wpDestFile",title),("wpSourceType","file"),("wpUploadFile", data),( "wpUpload", "Upload file")])
   
  req = urllib2.Request(SERVER + "index.php/Special:Upload",datagen,headers)  
  #handle = opener.open(req)
  handle = urllib2.urlopen(req)
  t = handle.read()
  print t
  # debugging: if you get a big chunk of html/xml you can quickly write it out to a file and load in in your browser to make sense of it
  #out = open("output.html","wb")
  #out.write(t)
  #out.close()

def UploadImagesInDir(opener, dir):
  """Upload all images in a specified directory"""
  print "uploading from %s" % dir
  for dirname, dirnames, filenames in os.walk(dir):
    for subdirname in dirnames:
        newdir = os.path.join(dirname, subdirname)
        UploadImagesInDir(opener, newdir)
        
    for filename in filenames:
        fpath = os.path.join(dirname, filename)
        print "uploading %s as %s" % (fpath, filename)
        createImage(opener,filename,fpath)

def UploadDictOfPages(opener):
  """Uploads all the pages in the pickled dictionary"""
  f = open("output.pkl","r")
  data = pickle.load(f)
  f.close()

  pdb.set_trace()
  lst = data.items()
  lst.sort()
  for (key,val) in lst:
    print "key %s" % key
    if not "File:" in key:  # We only want to upload mediawiki pages, so skip binary files
      importXmlApiPhp(opener,key,val)
    
        
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
  create(opener,"test","test page create2")
  createImage(opener,"testimage.png","images/testimage.png")
  pdb.set_trace()
