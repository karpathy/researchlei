# form the JSON database that will be read on the client

import cPickle as pickle
import os
import re
import json
import shutil

# build up list of papers
globaldb = os.path.join('db', 'papers.p')
papers = pickle.load(open(globaldb, "rb"))

out = []
for j in papers:

  pid = str(j['ID'])

  # basic meta information about this paper
  p={}
  p['i'] = j['ID']
  p['t'] = j['Title']
  p['a'] = [a['FirstName'] + ' ' + a['LastName'] for a in j['Author']]
  p['k'] = [k['Name'] for k in j['Keyword']]
  p['y'] = j['Year']
  p['b'] = j['Abstract']
  p['rn'] = j['ReferenceCount']
  p['cn'] = j['CitationCount']
  p['p'] = j['FullVersionURL']

  if j['Conference']: p['v'] = j['Conference']['ShortName']
  if j['Journal']: p['v'] = j['Journal']['ShortName']

  # see if we have computed other information for this paper
  pdir = os.path.join('db', pid)
  if os.path.isdir(pdir):

    # enter references if available
    refpath = os.path.join(pdir, 'references.p')
    if os.path.isfile(refpath):
      p['r'] = pickle.load(open(refpath, "rb"))

    # add citations if available
    citpath = os.path.join(pdir, 'citations.p')
    if os.path.isfile(citpath):
      p['c'] = pickle.load(open(citpath, "rb"))

    topWordsPicklePath = os.path.join(pdir, 'topwords.p')
    if os.path.isfile(topWordsPicklePath):
      twslist = pickle.load(open(topWordsPicklePath, "rb"))
      p['tw'] = [x[0] for x in twslist]

    # image paths
    imfiles = [f for f in os.listdir(pdir) if re.match(r'thumb.*\.png', f)]
    if len(imfiles)>0:
      thumbfiles = [("thumb-%d.png" % (i, )) for i in range(len(imfiles))]
      thumbs = [os.path.join('resources', pid, x) for x in thumbfiles]
      p['h'] = thumbs

  out.append(p)

outfile = os.path.join('client', 'db.json')
jout = json.dumps(out)
f = open(outfile, 'w')
f.write(jout)
f.close()



