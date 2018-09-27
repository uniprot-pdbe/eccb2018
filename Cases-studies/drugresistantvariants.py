'''
Created on 19 Sep 2018

@author: anight
'''

import pandas as pd
import re
import time
import requests, sys
import math



class ChemblDrugResistantVariants(object):

    def __init__(self, fin, fout):
        '''
        Constructor
        '''
        self.fin = fin
        self.fout = fout
        

    def checkSequence(self, seq: str, position: int, wildtype: str) -> bool:
            if seq.find(wildtype,position):
                return True
            return False
    
    def checkResponse(self, resp) -> bool:
        if(resp.status_code == 200):
            return True
        else:
            return False  
     
    def checkNoData(self, resp) -> bool:
        if(resp.status_code == 404):
            return True
        else:
            return False
    
        
    def queryAPI(self, url: str,acc: str) -> []:
            urlFormat = "format=json"
            
            fullUrl = url + "/" + acc + "?" + urlFormat 
            #print(fullUrl)
            responseFail = 0
            response = requests.get(fullUrl) 
            if(self.checkNoData(response)):
                response.close()
                return []
            
            while(not self.checkResponse(response)):
                if(responseFail == 10):
                    break
                # Record a failed response from server
                else:
                    responseFail += 1
                    time.sleep(2)
                    response = requests.get(fullUrl)
            
            jsonResponse = response.json()
            
            response.close()
            return jsonResponse    
        
        
    
        
    def parseFeautesAndXrefs(self, quacc: str, mutdata: [], pos: int) -> []: 
        #A/D=2-1068 or A/C=227-461, B/D=133-188
        rxp = re.compile('\d+')
        url = "https://www.ebi.ac.uk/proteins/api/proteins"
        protresp = self.queryAPI(url,quacc)
        if "features" in protresp:
            feats = []
            for ft in protresp["features"]:
                #if quacc == 'Q9NTG7':
                #    print(ft)
                if not ft["begin"] == 'unknown' and not ft["end"] == 'unknown' \
                and pos >= int(ft["begin"]) and pos <= int(ft["end"]):
                    feats.append(ft)
            mutdata.append(feats)
        else:
            mutdata.append([])
        if "dbReferences" in protresp:
            xrefs = []
            for xr in protresp["dbReferences"]:
                if "PDB" == xr["type"]:
                    if "chains" in xr["properties"]: 
                        chains = xr["properties"]["chains"]
                        for ch in chains.split(','):
                            crange = rxp.findall(ch)
                            if pos >= int(crange[0]) and pos <= int(crange[1]):
                                xrefs.append(xr["id"])
            mutdata.append(xrefs)
        else:
            mutdata.append([])
        return mutdata
        
        
        
    def checkForVariant(self, varfts: [],wt: str,pos: str,vt: str) -> []:
        for ft in varfts:
            if ft["type"] == "VARIANT" and ft["begin"] == pos \
            and ft["wildType"] == wt and ft["alternativeSequence"] == vt:
                return ft
    # wt = R, alt = * and begin = 4 
    
    def updateforbadseqmatch(self, mutdata: []) -> []:
        mutdata.append('fail')
        mutdata.append('fail')
        mutdata.append([])
        mutdata.append(False)
        mutdata.append([])
    
    
    def processVariants(self):

        # Main here 
        rxp = re.compile('([A-Z])(\d+)([A-Z])')
        
        rescols = ['accession', 'wildtype', 'muttype', 'position', 'seqpass', 'knownvariant', 'varinatIDs','disease',
                   'annotation','features','pdbe']
        
        resdf = pd.DataFrame(columns=rescols)
        varcnt = 0
        url = "https://www.ebi.ac.uk/proteins/api/variation"
        
        indf = pd.read_csv(self.fin, sep="\t")
        
        #for r in indf.iterrows():
        for r in indf.values:
            print(r)
            quacc = r[2]
        
            # requires isoform?
            if not math.isnan(r[3]) and int(r[3]) != 1:
                quacc = quacc + '-' + str(int(r[3]))
        
            # 'S631A,L666A'
            for mut in r[1].split(','):
                mutdata = []
                mutdata.append(quacc)
                rxpm = rxp.match(mut)
                wt = rxpm.group(1)
                pos = rxpm.group(2)
                vt = rxpm.group(3)
                mutdata.append(wt)
                mutdata.append(vt)
                mutdata.append(pos)
        
                varresp = self.queryAPI(url,quacc)
                if(len(varresp) == 0):
                    matchedSeq = False
                else:
                    vrseq = varresp["sequence"]
                    matchedSeq = self.checkSequence(vrseq,int(pos),wt)
        
                if matchedSeq:
                    mutdata.append('pass')
                    var = self.checkForVariant(varresp["features"],wt,pos,vt)
                    if var is not None:
                        mutdata.append('pass')
                        vxrf = []
                        for xr in var["xrefs"]:
                            vxrf.append(xr["id"])
                        vxrfset = set(vxrf)
                        vxrf = list(vxrfset)
                        mutdata.append(vxrf)
                        assd = []
                        if "association" in var:
                            mutdata.append(True)
                            for ass in var["association"]:
                                assd.append(ass["name"])
                                assevid = []
                                for evid in ass["evidences"]:
                                    assevid.append(evid["source"])
                                assd.append(assevid)
                                if "xrefs" in ass:
                                    assd.append(ass["xrefs"])
                            mutdata.append(assd)
                        else:
                            mutdata.append(False)
                            mutdata.append([])
                    else:
                        mutdata.append('fail')
                        mutdata.append([])
                        mutdata.append(False)
                        mutdata.append([])
        
                    # Next step is to get features and PDB xrefs
                    mutdata = self.parseFeautesAndXrefs(quacc, mutdata, int(pos))
        
                else:
                    mutdata = self.updateforbadseqmatch(mutdata)
                resdf.loc[varcnt] = mutdata
                varcnt+=1
        
            
        resdf.to_csv(self.fout, index=False)
        #print(resdf)



if __name__ == '__main__':
    print(sys.argv)
    #fout = "<path>/ChEMBL_drug_resist_anal_results.csv"
    #fin="<path>/Human_variants_ChEMBL.tsv"
    chemblVars = ChemblDrugResistantVariants(sys.argv[1],sys.argv[2])
    chemblVars.processVariants()
    
    
    
    exit(0)