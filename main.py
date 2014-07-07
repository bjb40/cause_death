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

"""  

#2A> Prepare concatenated 3-level list to contain ICD-9

disease = [] #make an object??#
category = [disease] # make a set??#
chapter = [category]

#<#


#2B> read .txt file line-by-line and drop in the appropriate list


icd9_raw = open(icd9_ref,"r")

    
testlines = icd9_raw.readlines(20)

import re

for line in testlines:
    if re.match(r"\d\d\d\.\d*", line):
        print "Match! \t" + line.strip()
        disease.append(line.strip())
#    else:
#        print "No Match!" + line.strip()

icd9_raw.close()

#<#
