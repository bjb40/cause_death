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
'''  


#@@@@@@@@@@@@@@@@@@@@@@@
#Import dependencies and assign global variables
#@@@@@@@@@@@@@@@@@@@@@@@


print str(locals()['__doc__'])


#dependancies
import re, os, csv, time, numpy as np
from ftplib import FTP

#global variables

dirs = {
'ftp':'ftp.cdc.gov',
'icd9':'pub/Health_Statistics/NCHS/Publications/ICD-9',
'icd10':'pub/Health_Statistics/NCHS/Publications/ICD10',
'nchs113':'pub/Health_Statistics/NCHS/Datasets/Comparability/icd9_icd10/',
'dat':'H:/Academic Projects/Data Files/NVSS/nosology',
'outdir':'H:/projects/cause_death/output'
}

local9 = os.path.join(dirs['dat'] + '/icd9')
local10= os.path.join(dirs['dat'] + '/icd10')
local113 = os.path.join(dirs['dat'] + '/nchs113')

#%%
#@@@@@@@@@@@@@@@@@@@@@@@
#Connect to .ftp site and download current icd lists
#@@@@@@@@@@@@@@@@@@@@@@@

#make ftp connection for public files

print ("Connecting to %s.\n\n" % dirs['ftp'])
myftp = FTP(dirs["ftp"])
myftp.login()


if not os.path.exists(local113):
    print('Making path %s' % local113)
    os.makedirs(local113)

print("Downloading list of NCHS 113 sas codes from %s" % dirs['nchs113'])
source = os.path.join(dirs['nchs113'],'Classify_to_113_list.sas')
destination = open(os.path.join(local113,'Classify_to_113_list.sas'),'wb')
myftp.retrbinary('RETR %s' % source, destination.write)
print('%s downloaded' % os.path.split(destination.name)[1])

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

#clean memory
del(f,fname,source)

#%%
#@@@@@@@@@@@@@@@@@@@@@@@
#Parse SAS code into useable dictionary
#@@@@@@@@@@@@@@@@@@@@@@@

#load into single string
with open(os.path.join(local113,'Classify_to_113_list.sas')) as sasfile:
    nchsdiv = sasfile.read()
sasfile.close()

#split into three parts: icd9map icd10map and nchs113ti

#trim top
nchsdiv = re.split(r'\/\*CLASSIFY ICD-9 CODES\*\/',nchsdiv,1)[1]

#split summary list
(nchsdiv,nchs113ti) = re.split(r'\/\*The following format may be applied to values of UC09_113 and UC10_113 \*\/',nchsdiv,1)

#split list of 10 and 12
(icd9map,icd10map) =  re.split(r'\/\*CLASSIFY ICD-10 CODES \*\/',nchsdiv,1)

#parse 113 list
m = re.split(r'\n',nchs113ti)
rm = []
for i in range(0,len(m)):
   #print(i,m[i])
   #time.sleep(.1)
   if re.search(r'=',m[i]):
        m[i] = m[i].split(r'=')
   else:
        rm.append(i)
    
rm.reverse()
for s in rm:
    m.pop(s)

nchs113ti = [[s.strip() for s in inner] for inner in m]
del(m,rm,s,inner,nchsdiv)

#parse codes for icd9 list

#summarize length to delete 'ifcausein(' from front and 'thenuc09_113' from end
b = len('ifcausein(')
e = len(')thenuc09_113')

l = ''.join(icd9map.split()).split(r';') #split by whitespace stripped line sas code
l.pop() #get rid of extraneous line

for i in range(0,len(l)):
    l[i] = l[i].split(r'=')
    l[i] = [int(l[i][1]),str(l[i][0])[b:-e].replace("'",' ').strip()]

icd9map = l

del(l,b,e)

#parse codes for icd10 list
b = len('ifuc10in(')
e = len(')thenUC10_113')

l = ''.join(icd10map.split()).split(r';') #split by whitespace stripped line sas code
l.pop(); l.pop() #get rid of 'RUN;' statement and final semicolon
for i in range(0,len(l)):
    l[i] = l[i].split(r'=')
    l[i] = [int(l[i][1]),str(l[i][0])[b:-e].replace("'",' ').strip()]

icd10map = l

del(l,b,e)

#combine parsed lists and write to csv

#convert to numpy arrays
nchs113ti = np.array(nchs113ti)
icd10map = np.array(icd10map)
icd9map = np.array(icd9map)

#%%

#initialize empty final array
#nchsmap = np.recarray( (113,), dtype= [('id',int),('title',str),('icd9list',str),('icd10list',str),('gbd',str)])
#nchsmap['id'] = np.arange(1,114,dtype=np.int)

nchsmap = []

#strip extra characters
def stript(string):
    return(string.replace('[','').replace(']','').replace('\\t','').replace("'",'').replace('"','').replace('  ',' ').strip())

#populate final array
for l in range(1,114):
    ti = stript(np.array_str(nchs113ti[np.where(nchs113ti[:,0] ==str(l)),1]))
    l10 = stript(np.array_str(icd10map[np.where(icd10map[:,0] == str(l)),1]))
    l9 = stript(np.array_str(icd9map[np.where(icd9map[:,0] == str(l)),1]))
    #gbd based on code 
    #print([l,ti,l10,l9,'a'])
    #time.sleep(.1)
    nchsmap.append([l,ti,l9,l10,'gbd'])
    

#%%

#@@@@@@@@@@@@@@@@@@@@@@@
#Parse ICD9 into useable lists
#@@@@@@@@@@@@@@@@@@@@@@@

#Prepare concatenated 3-level list to contain ICD-9

disease = [] 
category = [] 
chapter = []

#read .txt file line-by-line and drop in the appropriate list

#prepare regular expression searches 
level1 = re.compile(r"E?[0-9][0-9][0-9]\.[0-9]*")
level2 = re.compile(r"^\s*?[0-9][0-9][0-9]\s+")
level3 = re.compile(r"[IVX]\.")

# prepare 'holder' strings for upper levels to place in the list
L1 = ''
L2 = ''
L3 = ''
l=0

with open(os.path.join(local9,'ucod.txt'),"r") as icd9_raw:
    next(icd9_raw)
    for line in icd9_raw:
        #print(line)
        #time.sleep(2)
        if level3.search(line):
            L3 = line.strip()
            chapter.append(L3)
            l=3
    
        elif level2.search(line):
            level2_split = re.split(r" ", line.strip(), 1)
            #concatenate list with chapter in front of disease category
            level2_split.insert(0,L3)
            L2 = level2_split
            category.append(L2)
            l=2
    
        #match ensures it is matches at the beginning of the string
        elif level1.match(line): 
            level1_split = re.split(r" ", line.strip(), 1)
            #concatenate list with level in front of disease
            if type(L2) is list:
                disease.append(L2+level1_split)
            l=1
            

#could use non-matches to collect notes
#        else:
#            print "No Match: Level" + str(l) + '\n' + line.strip()
#            time.sleep(2)

icd9_raw.close()

#%%

#write to .csv file>
disease9 = [[s.strip() for s in inner] for inner in disease]

with open(os.path.join(dirs['outdir'],'icd9.csv'), "wb") as f:
    writer = csv.writer(f)
    writer.writerow(['chapter','div_no','div_name','code','descrip'])
    writer.writerows(disease9)

#%%
#@@@@@@@@@@@@@@@@@@@@@@@
#Parse ICD10 into useable lists
#@@@@@@@@@@@@@@@@@@@@@@@

status = []
disease = [] 
category = [] 
chapter = []

#read .txt file line-by-line and drop in the appropriate list

#prepare regular expression searches 
statnote = re.compile(r"\t")
level0 = re.compile(r"[A-Z][0-9][0-9]\.[0-9]*") #4 character code --- only extends from 3 char
level1 = re.compile(r"[A-Z][0-9][0-9]\t") #3 character code, e.b. Y09 (only 3, not 4)
level2 = re.compile(r"[A-Z][0-9][0-9]-[A-Z][0-9][0-9]")
level3 = re.compile(r"[IVX]\.")

# prepare 'holder' strings for upper levels to place in the list
L1 = ''
L2 = ''
L3 = ''
l=0

with open(os.path.join(local10,'allvalid2011 (detailed titles headings).txt'),"r") as icd10_raw:
    for _ in xrange(7):
        next(icd10_raw)
    for line in icd10_raw:
         if statnote.match(line):
             #standard variables
             added=1999
             deleted=0
             MC_only=0
         else:
             #pop the front off for further processing
             pre = re.split(r"\t",line.strip(),1)[0]
             line = re.split(r"\t",line.strip(),1)[1]
             #print(pre)
             #time.sleep(.1)

             
             if re.match(r"Added ",pre):
                 #print(pre)
                 m=re.search(r"[0-9][0-9][0-9][0-9]",pre)
                 added=pre[m.start():m.end()]
                 deleted=0
                 MC_only=0
                 
             elif re.match(r"Deleted ",pre):
                 #print(pre)
                 m=re.search(r"[0-9][0-9][0-9][0-9]",pre)
                 deleted=pre[m.start():m.end()]
                 added=1999
                 MC_only=0
                 #print(deleted)

             elif re.match(r"MC ONLY",pre):
                 #print(pre)
                 added=1999
                 deleted=0
                 MC_only=1
                 #print(MC_only)
                 
         #if MC_only == 1:
         #    print([added,deleted,MC_only])

         if level3.search(line):
            L3 = line.strip()
            chapter.append(L3)
    
         elif level2.search(line):
            level2_split = re.split(r"\t", line.strip(), 1)
            #concatenate list with chapter in front of disease category
            level2_split.insert(0,L3)
            L2 = level2_split
            category.append(L2)
        
         elif level1.search(line):
             level1_split = re.split(r"\t",line.strip(),1)
#            #concatenate list with level in front of disease
             if type(L2) is list:
                disease.append(L2+level1_split+[int(0),added,deleted,MC_only])
   
         elif level0.search(line): 
            level1_split = re.split(r"\t", line.strip(), 1)
#            #concatenate list with level in front of disease
            if type(L2) is list:
               disease.append(L2+level1_split+[int(1),added,deleted,MC_only])

icd10_raw.close()

#%%

#write to .csv file>

with open(os.path.join(dirs['outdir'],'icd10.csv'), "wb") as f:
    writer = csv.writer(f)
    writer.writerow(['chapter','div_nos','div_name','code','descrip','four_code','year_add','year_del','mc_only'])
    writer.writerows(disease)

#%%