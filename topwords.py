# finds top words in a paper and saves them to db/$PAPERID/topwords.p
# requires paper.pdf for the paper to exist

import os.path
import os
import sys
import cPickle as pickle
from string import punctuation
from operator import itemgetter
import re

N= 100 # how many top words to retain

# load in stopwords (i.e. boring words, these we will ignore)
stopwords = open("stopwords.txt", "r").read().split()
stopwords = [x.strip(punctuation) for x in stopwords if len(x)>2]

pid = sys.argv[1]

pdfpath = os.path.join('db', pid, 'paper.pdf')
if not os.path.isfile(pdfpath):
  print "wat?? %s is missing. Can't extract top words. Exitting." % (pdfpath, )
  sys.exit(1)

picklepath = os.path.join('db', pid, 'topwords.p')
if os.path.isfile(pdfpath):

  print "processing %s " % (pid, )
  topwords = {}

  cmd = "pdftotext %s %s" % (pdfpath, "out.txt")
  print "running: " + cmd
  os.system(cmd)

  txtlst = open("out.txt").read().split() # get all words in a giant list
  words = [x.lower() for x in txtlst if re.match('^[\w-]+$', x) is not None] # take only alphanumerics
  words = [x for x in words if len(x)>2 and (not x in stopwords)] # remove stop words

  # count up frequencies of all words
  wcount = {} 
  for w in words: wcount[w] = wcount.get(w, 0) + 1
  top = sorted(wcount.iteritems(), key=itemgetter(1), reverse=True)[:N] # sort and take top N

  # top is a list of (word, frequency) items. Save it
  pickle.dump(top, open(picklepath, "wb"))
  
print "all done."
