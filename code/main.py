#!/usr/bin/env python
'''
OVERVIEW
Read this text file organized as 3 level hierarchical lists.
DISEASE = The bottom, fundamental level is the single disease category: ###.[#],
  where [] indicates an open set of numbers.
CATEGORY = Level 2 is the heading to the initial 3 digits, ###
chapter = Level 3 is the "chapter" heading beginnin with a roman numberal and in all caps

NOTE that there are additoinal levels between 2 and 3 in the file, and separate levels built in ohter programs.
I am leaving them aside for the time-being.

TASKS
A-prepare concatenated 3-level list for ICD-9
B-read .txt file line-by-line and drop the information to the appropriate list
C- write to .csv file for processing in R
'''  


#@@@@@@@@@@@@@@@@@@@@@@@
#Import dependencies and assign global variables
#@@@@@@@@@@@@@@@@@@@@@@@


print str(locals()['__doc__'])


#dependancies
import re,os, time sqlite3 as dbapi
from ftplib import FTP
from StringIO import StringIO

#global variables

dirs = {
'ftp':'ftp.cdc.gov',
'icd9':'pub/Health_Statistics/NCHS/Publications/ICD-9',
'icd10':'pub/Health_Statistics/NCHS/Publications/ICD10',
'dat':'H:/Academic Projects/Data Files/NVSS/nosology',
'outdir':'H:/projects/cause_death/output'
}

local9 = os.path.join(dirs['dat'] + '/icd9')
local10= os.path.join(dirs['dat'] + '/icd10')

#%%
#@@@@@@@@@@@@@@@@@@@@@@@
#Connect to .ftp site and download current icd lists
#@@@@@@@@@@@@@@@@@@@@@@@

#make ftp connection for public files

print ("Connecting to %s.\n\n" % dirs['ftp'])
myftp = FTP(dirs["ftp"])
myftp.login()


print ("Downloading icd9-related files from:\n\t ftp:// %s %s" % (dirs["ftp"],dirs["icd9"]))

if not os.path.exists(local9):
    print('Making path %s' % local9)
    os.makedirs(local9)


print ("Placing icd9 files into %s" % local9)
mfiles = myftp.nlst(dirs["icd9"])
for f in mfiles:
    fname = os.path.split(f)[1]
    source = os.path.join(dirs['icd9'],fname)
    destination = open(os.path.join(local9,fname), "wb")
    myftp.retrbinary('RETR %s' % source, destination.write)
    destination.close()
    print('%s downloaded' % fname)

print ('\n\n ICD9 files downloaded')

if not os.path.exists(local10):
    print('Making path %s' % local10)
    os.makedirs(local10)

print ("Placing icd10 files into %s" % local10)
mfiles = myftp.nlst(dirs["icd10"])
for f in mfiles:
    fname = os.path.split(f)[1]
    source = os.path.join(dirs['icd10'],fname)
    destination = open(os.path.join(local10,fname), "wb")
    myftp.retrbinary('RETR %s' % source, destination.write)
    destination.close()
    print('%s downloaded' % fname)

print ('\n\n ICD10 files downloaded')


myftp.quit()

#%%
#@@@@@@@@@@@@@@@@@@@@@@@
#Parse ICD9 into useable lists
#@@@@@@@@@@@@@@@@@@@@@@@

#2A> Prepare concatenated 3-level list to contain ICD-9

disease = [] #make an object??#
category = [] # make a set??#
chapter = []

#<#


#2B> read .txt file line-by-line and drop in the appropriate list
icd9_raw = open(os.path.join(local9,'ucod.txt'),"r")

    
testlines = icd9_raw.readlines(50)


#prepare regular expression searches 
level1 = re.compile(r"E?[0-9][0-9][0-9]\.[0-9]*")
level2 = re.compile(r"[0-9][0-9[0-9]\s+")
level3 = re.compile(r"[IVX]\.")

# prepare 'holder' strings for upper levels to place in the list
L1 = ''
L2 = ''
L3 = ''

for line in icd9_raw:
    print(line)
    time.sleep(2)
    if level3.search(line):
        L3 = line.strip()
        chapter.append(L3)
    
    elif level2.search(line):
        level2_split = re.split(r" ", line.strip(), 1)
        #concatenate list with chapter in front of disease category
        level2_split.insert(0,L3)
        L2 = level2_split
        category.append(L2)

    #match ensures it is matches at the beginning of the string
    elif level1.match(line): 
        level1_split = re.split(r" ", line.strip(), 1)
        #concatenate list with level in front of disease
        if type(L2) is list:
            disease.append(L2+level1_split)

#    else:
#       print "No Match:" + line.strip()

icd9_raw.close()

#%%

#2C write to .csv file>
import csv

with open(os.path.join(dirs['outdir'],'icd9.csv'), "wb") as f:
    writer = csv.writer(f)
    writer.writerows(disease)

#%%
