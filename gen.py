import pdb
import inspect
from types import *

IdCount = 0
def GenId():
  global IdCount
  IdCount += 1
  return IdCount

ids = {}
def uniqueId(prefix):
  if ids.has_key(prefix):
    idx = ids[prefix]
    ids[prefix] = idx + 1
    return prefix + "_%d" % idx 
  ids[prefix]=1
  return prefix

def iterable(x):
  """?? Is the thing iterable?"""
  try:
    t = iter(x)
  except TypeError:
    return False
  return True

def isInstanceOf(obj,objType):
  """?? Is the object an instance (or derived from) of the class objType?"""

  # Allow a list or tuple of objects to be passed
  if iterable(objType):
    if type(obj) is InstanceType:
      mro = inspect.getmro(obj.__class__)
      for ot in objType:
        if ot in mro: return True

  # If its not iterable do it in one line
  if type(obj) is InstanceType and objType in inspect.getmro(obj.__class__): return True

  return False


def inlif(cond,tru,fal):
  """?? Inline 'if' statement.  But note that both tru and fal are actually evaluated"""
  if cond: return tru
  return fal

def keyify(s):
  s = s.replace(":","_")
  return s

def flatten(listOflists):
  """Turn a list of list of lists into just 1 list and eliminate "None"
  """
  ret = []
  # termination case, arg is not a list
  if not type(listOflists) is ListType:
    return [listOflists]
  # recursive case, it is a list
  for list in listOflists:
    ret += flatten(list)
  return ret

