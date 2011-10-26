import pickle  
import pdb

data = None

def multiReplace(text, srchLst, tgt):
  for l in srchLst:  # how inefficient can I make this :-)
    text = text.replace(l,tgt)
  return text

def Test():

  # Open the dictionary data file
  global data
  f = open("data.pkl","r")
  data = pickle.load(f)

  new = {}

  # Now we simply iterate through, applying whatever transformations to the keys (page titles) and values that we need.
  for (key,val) in data.items():
    # But if this is a marker for a file that we DLed then skip it.
    if key[0:6] == "Image:" or (".png" in key) or (".gif" in key):  # Do nothing
      new[key] = val
    else:
      new[key.replace("foo","bar")] = val.replace("foo","bar")

  

  # Now this example renames every page from "Doc:sdk5.0" (and variants) to "Doc:latest"
  # It also switches all image references from "Image:" (which is old mediawiki) to "File:"
  data = new
  new = {}
  
  for (key,val) in data.items():
    if "</text>" in val: # Otherwise its a blank page
      key = key.replace("Image:","File:")
      val = val.replace("Image:","File:")

      key = multiReplace(key,["Doc:sdk5.0","Doc:Sdk 5.0","Doc:Sdk_5.0","Doc:sdk 5.0","Doc:sdk_5.0"],"Doc:latest")
      val = multiReplace(val,["Doc:sdk5.0","Doc:Sdk 5.0","Doc:Sdk_5.0","Doc:sdk 5.0","Doc:sdk_5.0"],"Doc:latest")
      new[key] = val


  # Now store it away for further modification, or for uploading.    
  f = open("output.pkl","w")
  pickle.dump(new,f)
  f.close()
