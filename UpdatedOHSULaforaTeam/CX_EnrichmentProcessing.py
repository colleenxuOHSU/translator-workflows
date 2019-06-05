#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Using output exported from ShinyGo: http://bioinformatics.sdstate.edu/go/
Top 30 terms only. 
"""

import pandas as pd

def makeEnrichTable(myDiseaseGenes, myEnrichTable, myCols):
    """
    Inputs:
        myDiseaseGenes: list of disease associated genes as strings (symbol/human-readable form)
        myEnrichTable: pandas dataframe from reading in ShinyGo input
        myCols: list of columns. Setup is for 'Output_Gene', 'Input_Gene', 'Term'
    Output:
        pandas dataframe with rows merged when they have the same output gene and input gene. term ends up as a list of terms
    """
    ## output table setup
    outputDF1 = pd.DataFrame({myCols[0]:[], myCols[1]:[], myCols[2]:[]})
    
    ## iterate through input enrichment file
    ## Note: iterrows is very slow for tables with > thousands of rows! Refernce: https://stackoverflow.com/a/55557758
    for (index, row) in myEnrichTable.iterrows():
        ## row['Genes'] is a string. convert to set to check if disease associated genes in it
        ## checking for set membership is the fastest way to do this
        rowGeneSet = set(row['Genes'].split(' '))
        rowTerm = row['Functional Category']
        for dGene in myDiseaseGenes:
            if dGene in rowGeneSet:
                ## want all genes except those in the input disease associated list
                resultL = list(rowGeneSet.difference(set(myDiseaseGenes)))
                for outputG in resultL:  ## write out rows
                    outputDF1 = outputDF1.append({myCols[0]: outputG, myCols[1]:dGene, myCols[2]:rowTerm}, ignore_index=True)
    
    ## Need to merge rows with same output and input genes
    outputDFfinal = outputDF1.groupby([myCols[0], myCols[1]])[myCols[2]].apply(list).reset_index()
    
    ## Add lines to truncate lists of associated terms to 3 or less
    outputDFfinal[myCols[2]] = pd.Series([termL[0:3] if len(termL)>3 else termL for termL in outputDFfinal[myCols[2]]])
    return outputDFfinal

## figure out how to grab this object from existing setup?
diseaseGenes = ['NHLRC1', 'EPM2A']

## Phenotypic (Mod1B) term enrichment
outputColsPheno = ['Output_Gene', 'Input_Gene', 'PhenoAssociatedTerms']
phenoPath = "./Lafora_Mod1B_OtherHPOEnrichment.csv"
phenoEnrichDF = pd.read_csv(phenoPath)
phenoOutput = makeEnrichTable(diseaseGenes, phenoEnrichDF, outputColsPheno)

## write out CSV (replace with pickle object for summary stuff?)
outPhenoPath = "./PhenoEnrichedLaforaOutput.csv"
phenoOutput.to_csv(outPhenoPath)


## Code chunk for Functional Enrichment processing (Mod1A)
outputColsFunct = ['Output_Gene', 'Input_Gene', 'FunctAssociatedTerms']

## this is more complicated. need to merge the two input file dataframes, sorting by FDR in descending order

## get input enrichment tables
functBioPath = "./Lafora_Mod1A_GOBioProcessEnrichment.csv"
functMolecularPath = "./Lafora_Mod1A_GOMolecularEnrichment.csv"
functBioEnrich = pd.read_csv(functBioPath)
functMolecularEnrich = pd.read_csv(functMolecularPath)
## add rows of both together in one dataframe
functInput = functBioEnrich.append(functMolecularEnrich, ignore_index=True)
functInput = functInput.sort_values(by=['Enrichment FDR'])

functOutput = makeEnrichTable(diseaseGenes, functInput, outputColsFunct)

## write out CSV (replace with pickle object for summary stuff?)
outFunctPath = "./FunctEnrichedLaforaOutput.csv"
functOutput.to_csv(outFunctPath)