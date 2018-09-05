This folder contains case studies that you might find interesting to look at.

Case study 1: ChEMBL Drug Resistant Variants
ChEMBL (https://www.ebi.ac.uk/chembl) have compiled a set of 757 variants reported as inferring a drug resistence.
ChEMBL have mapped these variants to approximately 100 UniProt entries (canonical or specific isoform sequence) but
don't have any information about whether the variant colocates with a UniProt functional annotation or can be mapped
to a protein structure and if additional structural information can be gained.

The dataset is in Human_variants_ChEMBL.tsv. It is a tab delimited file with 4 columns:
VARIANT_ID - ChEMBL's internal identifier for the variant
MUTATION - single letter HGVS nomenclature that tells you the wild type residue, residue position in the sequence and the variant (mutation) residue
ACCESSION - the UniProt accession
ISOFORM - the sequence isoform.

There are a number of questions that can be answered for this dataset, below we will outline a few suggestions that are relevant to this 
tutorial but we are happy for you to analyse the data how you wish, if you have your own ideas. The time available is short so it is unlikely 
that you will be able to process the entire dataset completely; we suggest that you use a subset of variants from a single UniProt accession
as a test set. 

#### Warning: Not all the variants correctly map to the stated UniProt sequence. One test you will have to do is check that the wild type residue
matches the residue in the stated sequence at the residue position given.


#### Suggested Analyses:
1. Is the variant reported in UniProt?
2. Is the variant seen in a mapped PDBe structure?
3. Are there any protein features that colocate or overlap the variant?
4. Are there any structural features from PDBe that colocate or overlap the variant?

Big overall question - Has the information you retrieved been useful in determining how the variant(s) has(have) induced a drug resistence?

#### Notes on isoform sequences (This is a case study in itself as can be expended in to looking at the mapped protein structures):
UniProt functional annotations (features) are not mapped to isoform sequences. This is possible but you have to think of a
strategy on how to do it and to test that it is correct to map the feature to the isoform.

#### Notes on Python:
Make sure you have pandas installed. If using python 3.x run pip3 install pandas

