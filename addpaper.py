# adds paper to database

# usage: python addpaper.py [name|id] [query|id]
# examples:
# python addpaper.py name title of a nice paper
# python addpaper.py id 31415926535

# this should technically be several scripts, todo later

import cPickle as pickle
import time
import string
import json
import urllib2
import urllib
import os.path
import os
import sys

if len(sys.argv) <= 2:
  print "use script properly:"
  print "usage: python addpaper.py [name|id] [query|id]"
  print "examples:"
  print "python addpaper.py name title of a nice paper"
  print "python addpaper.py id 31415926535"
  sys.exit(1)

if not os.path.isfile('appid.txt'):
  print "OOPS! You're missing Microsoft Academic Search APP ID key in file appid.txt!"
  print "See Readme.md for instructions on obtaining one."
  print "Exitting."
  sys.exit(1)

if not os.path.isdir('db'): os.mkdir('db')

appid= open('appid.txt', 'r').read().rstrip()
globaldb = os.path.join('db', 'papers.p')
if not os.path.isfile(globaldb): pickle.dump([], open(globaldb, "wb"))

# form the query URL to MAS
url = "http://academic.research.microsoft.com/json.svc/search?AppId=%s" % (appid, )
url += "&StartIdx=1&EndIdx=1"
url += "&ResultObjects=publication"
qtype = sys.argv[1]
if qtype == "name":
  q = " ".join(sys.argv[2:])
  q = q.replace(' ', '+')
  url += "&TitleQuery=%s" % (q, )

elif qtype == "id":
  pubid = sys.argv[2]
  url += "&PublicationID=%s" % (pubid, )  

else:
  print "invalid query type. use [name|id]. quitting."
  sys.exit(1)

# perform request
print "querying url: %s..." % (url, )
j = json.load(urllib2.urlopen(url))
if len(j['d']['Publication']['Result']) == 0:
  print "No results found found! quitting!"
  sys.exit(1)

# go down the results...
rix = 0
while True:
  pub = j['d']['Publication']['Result'][rix] # publication json

  idstr = str(pub['ID'])
  dirpath = os.path.join('db', idstr)
  title = pub['Title']

  # print some info and ask user if this is the right paper to make sure
  papers = pickle.load(open(globaldb, "rb"))
  seenthis = any([pub['ID']==x['ID'] for x in papers])
  havethis = os.path.isdir(dirpath)

  v=""
  if pub['Conference']: v=pub['Conference'] 
  if pub['Journal']: v = pub['Journal']
  print "Found a record:"
  print "title: ", title
  print "author: ", (", ".join(a['FirstName'] + ' ' + a['LastName'] for a in pub['Author']))
  print "published in: ", v, pub['Year']
  print "citations: ", pub['CitationCount']
  print "have record of this: ", seenthis
  print "is in library: ", havethis

  isgood = raw_input("add to library? y/n: ")
  if isgood=="y" or isgood=="": 
    break
  else:
    print "ok moving to the next result..."
    rix+=1
    if rix>=len(j['d']['Publication']['Result']):
      print "that's it, not found! quitting."
      sys.exit(1)

# save the information into global papers database, if we don't already have it
if not seenthis:
  print "Updating papers.p global database."
  papers.append(pub)
  pickle.dump(papers, open(globaldb, "wb"))

# save the individual record for this paper in db/$ID/json.p
if not havethis: 
  print "Creating folder %s..." % (dirpath, )
  os.mkdir(dirpath)
jsonpath = os.path.join(dirpath, 'json.p')
pickle.dump(pub, open(jsonpath, "wb"))
print "Writing ", jsonpath

# download both citations and references. 
# Done with one loop since these are so similar
xx = ['CitationCount', 'ReferenceCount']
yy = ['Citation', 'Reference']
ff = ['citations.p', 'references.p']
for i in range(2):
  maxn = pub[xx[i]]
  desc = yy[i]
  fname = ff[i]

  doskip = False
  while True:
    nd = raw_input("how many top %s (up to %d) to download for %s? [empty default = all]: " % (desc, maxn, title))
    if nd=="": ndi = maxn
    else: ndi = int(nd)
    if ndi==0: 
      print "ok skipping %s." % (desc, )
      doskip = True
      break
    if ndi>maxn: ndi = maxn

    if ndi>1000:
      print "More than 1000 is too many. That's crazy, won't allow it."
    else:
      break

  if doskip: continue

  # form request URL and query. Page through results (only top 100 are given)
  print "downloading top %d %s for %s" % (ndi, desc, title)
  pubs = []
  istart = 1
  while True:
    iend = istart + 99
    if iend>ndi: iend=ndi

    print "downloading %d to %d" % (istart, iend)
    url = "http://academic.research.microsoft.com/json.svc/search?AppId=%s" % (appid, )
    url += "&ResultObjects=Publication"
    url += "&ReferenceType=%s" % (desc, )
    url += "&StartIdx=%d&EndIdx=%d" % (istart, iend)
    url += "&PublicationID=%s" % (idstr, )
    print "querying %s ... " % (url, )
    j2 = json.load(urllib2.urlopen(url))
    pubs.extend(j2['d']['Publication']['Result'])

    if iend>=ndi: break
    istart = istart+100

  # save ids
  ids = [x['ID'] for x in pubs]
  refPicklePath = os.path.join('db', idstr, fname)
  print "writing ", refPicklePath
  pickle.dump(ids, open(refPicklePath, "wb"))

  # extend global papers database
  papers = pickle.load(open(globaldb, "rb"))
  numadded=0
  for p in pubs:
    if not any([p['ID']==x['ID'] for x in papers]):
      papers.append(p)
      numadded += 1
  pickle.dump(papers, open(globaldb, "wb"))

  print "wrote %d/%d new entries to papers.p pickle." % (numadded, len(pubs))


opencommand = "gnome-open"
if sys.platform == 'darwin':
  opencommand = "open"

# download full PDF
pdfpath = os.path.join('db', idstr, 'paper.pdf')
urls = pub['FullVersionURL']
pdfurls = [u for u in urls if u.endswith('.pdf')]
gotit = False
print "All paper links:"
for u in urls: print u
for u in pdfurls:
  print "trying to retrieve: ", u
  try:
    urllib.urlretrieve(u, pdfpath)
    print "saved pdf at ", pdfpath
    try:
      print "opening the pdf using %s (%s) for your convenience to verify the download..." %(opencommand, sys.platform)
      os.system(opencommand + " " + pdfpath)
    except Error, e:
      print "%s failed. Make sure the downloaded %s pdf is correct." % (opencommand, pdfpath, )
    isok = raw_input("download good? y/n: ")
    if isok=="y":
      gotit = True
      break
  except Exception, e:
    print "ERROR retrieving: ", e

if not gotit:
  print "Couldn't get the paper pdf. Please download manually and save as %s." % (pdfpath, )
  kk = raw_input("waiting... press key to continue")

# create thumbnails
try:
  print "creating paper thumbnails..."
  thumbpath = os.path.join('db', idstr, 'thumb.png')
  cmd = "convert %s -thumbnail 150 -trim %s" % (pdfpath, thumbpath)
  print "running: " + cmd
  os.system(cmd)
except Error, e:
  print "creating thumbnails failed:"
  print e

# analyze the paper for top words
try:
  print "running topwords.py..."
  os.system("python topwords.py %s" % (idstr, ))
except Error, e:
  print "topwords.py error:"
  print e

try:
  print "running genjson.py..."
  os.system("python genjson.py")
except Error, e:
  print "genjson.py error:"
  print e

try:
  print "running copyresources.py..."
  os.system("python copyresources.py %s" % (idstr, ))
except Error, e:
  print "copyresources.py error:"
  print e

print "done. Open client/index.html to view library."
