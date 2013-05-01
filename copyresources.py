# copies resources from db/ to client/ that are necessary to view the database
import os.path
import os
import sys
import re
import shutil

# if an id is provided, use it. If not, do all papers
if len(sys.argv)>1: 
  pids = [sys.argv[1]]
else: 
  pids = os.listdir('db') # grab em all
  pids = [x for x in pids if os.path.isdir(os.path.join('db', x))]

# make sure client/imgs folder exists
imdir = os.path.join('client', 'resources')
if not os.path.isdir(imdir): os.mkdir(imdir)

for pid in pids:

  # copy images from db/ to client/imgs/
  pdir = os.path.join('db', pid)
  imfiles = [f for f in os.listdir(pdir) if re.match(r'thumb.*\.png', f)]
  dirto = os.path.join(imdir, pid)
  if not os.path.isdir(dirto): os.mkdir(dirto)

  for imfile in imfiles:
    pfrom = os.path.join(pdir, imfile)
    pto = os.path.join(dirto, imfile)
    shutil.copy2(pfrom, pto)

  # copy the pdf of the paper
  pfrom = os.path.join(pdir, 'paper.pdf')
  pto = os.path.join(dirto, 'paper.pdf')
  if os.path.isfile(pfrom):
    shutil.copy2(pfrom, pto)



