@@@@@@@@@@@@@@@@
Readme automatically generated from main.py available from
https://github.com/bjb40/cause_death
Bryce Bartlett
@@@@@@@@@@@@@

Files identified below were downloaded from the Department of Health and Human Services
public ftp site, ftp.cdc.gov, and parsed using python on the following date:
 10-09-2015
 
Text files parsed using Python 2.7 with numpy package. 
 
@@@@@@@@@@@@@@@
nchs113map.csv

This is the result of a parsed .sas string developed by NVSS in connection with
the 1996 comparability study. It outlines the codes related to the 113 ADULT 
causes of death developed by NVSS at that time as a cross-walk between ICD9
and ICD10.

Source Data:
ftp.cdc.govpub/Health_Statistics/NCHS/Datasets/Comparability/icd9_icd10//Classify_to_113_list.sas 

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

Source Data:
ftp.cdc.govpub/Health_Statistics/NCHS/Publications/ICD-9/ucod.txt

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

Source Data:
ftp.cdc.govpub/Health_Statistics/NCHS/Publications/ICD10/allvalid2011 (detailed titles headings).txt

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
