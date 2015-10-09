#!/usr/bin/env python
'''
This script downloads raw text files related to multiple cause mortality, and 
parses them into .csv files.

global variables of importance include assigning (1) a local raw file directory 
(to house the downloaded raw files from CDC) and (2) a local output directory
(to house the paresed files).

The script also generates a detailed readme file to explain the contents of the 
.csv.
'''  

#@@@@@@@@@@@@@@@@@@@@@@@
#Import dependencies and assign global variables
#@@@@@@@@@@@@@@@@@@@@@@@


print str(locals()['__doc__'])


#dependancies
import re, os, csv, time, datetime, numpy as np
from ftplib import FTP

#global variables

dirs = {
'ftp':'ftp.cdc.gov',
'icd9':'pub/Health_Statistics/NCHS/Publications/ICD-9',
'icd10':'pub/Health_Statistics/NCHS/Publications/ICD10',
'nchs113':'pub/Health_Statistics/NCHS/Datasets/Comparability/icd9_icd10/',
'dat':'H:/Academic Projects/Data Files/NVSS/nosology', #local raw file directory
'outdir':'H:/projects/cause_death/output' #local parsed file directory
}

#creating file structure for local raw data directory
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
    cat = ''
    
    if (l <= 17) or (l>=44 and l<=46) or (l>=66 and l <=69) or (l>=90 and l <=94):
        cat = 'Acute'
    elif (l>=18 and l<=43) or (l>=47 and l <=65) or (l>=70 and l<=89):
        cat= 'Chronic'
    elif l == 95:
        cat = 'Residual'
    elif l>=96:
        cat = 'External'

    nchsmap.append([l,ti,l9,l10,cat])


#%%

#write to .csv file>

with open(os.path.join(dirs['outdir'],'nchs113map.csv'), "wb") as f:
    writer = csv.writer(f)
    writer.writerow(['nchsid','title','icd9map','icd10map','category'])
    writer.writerows(nchsmap)
    
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
level2 = re.compile(r"^\s*?E?[0-9][0-9][0-9]\s+")
level3 = re.compile(r"[IVX]\.")

# prepare 'holder' strings for upper levels to place in the list
L1 = ''
L2 = ''
L3 = ''
l=0

exchap = 'External (non-numbered) Chapter prefixed "E"'

with open(os.path.join(local9,'ucod.txt'),"r") as icd9_raw:
    next(icd9_raw)
    for line in icd9_raw:
        #print(line)
        #time.sleep(2)
        if level3.search(line):
            L3 = line.strip()
            chapter.append(L3)
         
        elif level2.search(line):
            level2_split = re.split(r" ", line.replace('\t','').strip(), 1)
            #special processing for "external" chapter
            if re.search(r'E[0-9][0-9][0-9]',line):
                L3 = exchap
            #concatenate list with chapter in front of disease category                
            level2_split.insert(0,L3)
            L2 = level2_split
            category.append(L2)
            l=2
    
        #match ensures it is matches at the beginning of the string
        elif level1.match(line): 
            level1_split = re.split(r" ", line.replace('\t','').strip(), 1)
            #concatenate list with level in front of disease
            if type(L2) is list:
                disease.append(L2+level1_split)
            l=1
            

#could use non-matches to collect notes
#        else:
#            print "No Match: Level" + str(l) + '\n' + line.strip()
#            time.sleep(.1)

icd9_raw.close()



#item finder http://stackoverflow.com/questions/15886751/python-get-index-from-list-of-lists
def findItem(theList, item):
   return [(ind, theList[ind].index(item)) for ind in xrange(len(theList)) if item in theList[ind]]

#merge with information from NCHS 113

for c in range(0,113):
    nchscod = nchsmap[c][0:2]
    nchscod.append(nchsmap[c][4])
    cod = nchsmap[c][2].split(r' ')
    print("Merging nchs no. %s: %s \n\t%s disease class" % (nchscod[0],nchscod[1],nchscod[2]))
    time.sleep(.1)

    for i in cod:
        #add "E" prefix for externals - left out of SAS file
        #print(i)
        if(i) != '' and int(i) > 7999:
            i = 'E'+ i
        #add the decimal
        i=i[:-1] + '.' + i[-1:]
        idex = findItem(disease,i)
        for d in idex:
            disease[d[0]] += nchscod


#%%

#write to .csv file>
disease9 = [[str(s).replace('\\t','').strip() for s in inner] for inner in disease]

with open(os.path.join(dirs['outdir'],'icd9.csv'), "wb") as f:
    writer = csv.writer(f)
    writer.writerow(['chapter','div_no','div_name','code','descrip','nchs113','nchsti','type'])
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



#merge with information from NCHS 113

for c in range(0,113):
    nchscod = nchsmap[c][0:2]
    nchscod.append(nchsmap[c][4])
    cod = nchsmap[c][3].split(r' ')
    print("Merging nchs no. %s: %s \n\t%s disease class" % (nchscod[0],nchscod[1],nchscod[2]))
    time.sleep(.1)

    for i in cod:
        #correct formatting
        if len(i) == 4:
            i = i[0:3] + '.' + i[3]

        idex = findItem(disease,i)         
        for d in idex:
            disease[d[0]] += nchscod



#%%

#write to .csv file>

with open(os.path.join(dirs['outdir'],'icd10.csv'), "wb") as f:
    writer = csv.writer(f)
    writer.writerow(['chapter','div_nos','div_name','code','descrip','four_code','year_add','year_del','mc_only','nchs113','nchsti','type'])
    writer.writerows(disease)

#%%

#write readme file

readme = open(os.path.join(dirs['outdir'],'readme.txt'),'w')

readme.write('''@@@@@@@@@@@@@@@@
Readme automatically generated from main.py available from
https://github.com/bjb40/cause_death
Bryce Bartlett
@@@@@@@@@@@@@

Files identified below were downloaded from the Department of Health and Human Services
public ftp site, %s, and parsed using python on the following date:
 %s
 
Text files parsed using Python 2.7 with numpy package. 
 
@@@@@@@@@@@@@@@
nchs113map.csv

This is the result of a parsed .sas string developed by NVSS in connection with
the 1996 comparability study. It outlines the codes related to the 113 ADULT 
causes of death developed by NVSS at that time as a cross-walk between ICD9
and ICD10.

Source Data:\n%s 

File structure:
nchsid      Arbitrary index number 113 assigned by NCHS.
title       Name assigned to each 113 classification by NCHS.
icd9map     String of icd codes under icd9 assigned to specific classification.
icd10map    String of codes under icd10 assigned to specific classification

@@@@@@@@@@@@@@@
icd9.csv

This is parsed listing of all available icd9 codes specific to cause of death classifications
in the multiple mortality files prior to 1999. It provides a listing of each
acceptable cause of death code with associated attributes.

Source Data:\n%s

File Structure: 
chapter     String reporting which of 16 of ICD9 chapters (uses Roman Numerals)
div_no      ICD number assigned at the higher level (3 code) codification of the disease
div_name    Assigned description of the division
code        UNIQUE KEY: 4 code ICD number assigned to disease classification
descrip     Official disease description
nchs113     Index number from nchs113map.csv as assigned by nchs
nchsti      Title of nchs index number from nchs113map.csv
type        Broad classification of disease as "acute","chronic","external",or "residual" (author assigned)

@@@@@@@@@@@@@@@
icd10.csv

This is parsed listing of all available icd10 codes specific to cause of death classifications
in the multiple mortality files from 1999 on. It provides a listing of each
acceptable cause of death code with associated attributes.

Source Data:\n%s

File Structure: 
chapter     String reporting which of 16 of ICD9 chapters (uses Roman Numerals)
div_nos     Span of ICD numbers assigned at the higher level (3 code) codification of the disease
div_name    Assigned description of the division
code        UNIQUE KEY: 3 or 4 code ICD number assigned to disease classification
descrip     Official disease description
four_code   Binary indicator of 3 code (A01) or 4 code (A01.1) ICD number
year_add    The year the disease classification was first used for causes of death
year_del    The year the disease classification was discontinued; coded 0 if still in use
mc_only     Indicates whether code is used in multiple cause file only (1) or used more broadly (0)
nchs113     Index number from nchs113map.csv as assigned by nchs
nchsti      Title of nchs index number from nchs113map.csv
type        Broad classification of disease as "acute","chronic","external",or "residual" (author assigned)


NOTE: It appears that some disease classifications DO NOT have a 4 digit code, 
and are only reportable using the 3 digit code.
'''
 % (dirs['ftp'],
    datetime.datetime.now().strftime('%m-%d-%Y'),
    dirs['ftp']+dirs['nchs113']+'/Classify_to_113_list.sas',
    dirs['ftp']+dirs['icd9']+'/ucod.txt',
    dirs['ftp']+dirs['icd10']+'/allvalid2011 (detailed titles headings).txt')
 )
 
readme.close() 


