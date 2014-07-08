# This will be the header to my Python code and description

#1>  References, global settings, and fixed values

icd9_ref = "H:\Academic Projects\Data Files\Vital Statistics\Mortality\ICD 9 Codes/ucod.txt"

#<#


#2> ICD-9

"""
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
C- wirte to .csv file for use in SAS analysis

"""  

#2A> Prepare concatenated 3-level list to contain ICD-9

disease = [] #make an object??#
category = [] # make a set??#
chapter = []

#<#


#2B> read .txt file line-by-line and drop in the appropriate list


icd9_raw = open(icd9_ref,"r")

    
testlines = icd9_raw.readlines(50)

import re

#prepare regular expression searches 
level1 = re.compile(r"E?[0-9][0-9][0-9]\.[0-9]*")
level2 = re.compile(r"[0-9][0-9[0-9]\s+")
level3 = re.compile(r"[IVX]\.")

# prepare 'holder' strings for upper levels to place in the list
L2 = ''
L3 = ''

for line in icd9_raw:
    if level3.search(line):
        L3 = line.strip()
        chapter.append(L3)
    
    elif level2.search(line):
        level2_split = re.split(r" ", line.strip(), 1)
        #concatenate list with chapter in front of disease category
        level2_split.insert(0,L3)
        L2 = level2_split
        category.append(level2_split)

    #match ensures it is matches at the beginning of the string
    elif level1.match(line): 
        level1_split = re.split(r" ", line.strip(), 1)
        #concatenate list with level in front of disease
        level1_split.insert(0,L2) 
        disease.append(level1_split)

 #   else:
 #       print "No Match:" + line.strip()

icd9_raw.close()

#<#

#2C write to .csv file>


#<#

