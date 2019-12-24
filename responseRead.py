import os
import requests
import json as js
import re as re
from decimal import Decimal
import sys


def udf_processJSONtoDB(p_json):

    jData = p_json.split("\n")

    receipt = {}
    dPriceScan = {}

    # create list for reprocessing (instead of resetting the cursor)
    lFile = [line.strip("\n \t") for line in jData]
    lPrices = []
    
    iTotal = 0
    iRunTotal = 0
    cRS = 0 # count ReceiptScan = cRS
    fTotal = 0.0
    
    sSection = "footer"
    iCountSection = 0
    itemQty = ""

    # look from bottom of the file to find total first
    for i, line in enumerate(lFile[::-1]):
        words = line.split("\t")
        
        # check if last item in word is a linebreak
        if words[-1] == "\n":
            words.pop(len(words)-1)

        reQty = re.compile(r"\d\s?[xX]\s?")
        matchQty = reQty.search((" ").join(words[:]))
        # sprint(line)
        if matchQty:
            itemQty = (" ").join(words)
            price = -1
            continue

        # sentence loop
        for c, word in enumerate(words[::-1]):
            reCheck = re.compile(r"\d[.,]\d")
            match = reCheck.search(word)
            
            if match: 
                decimals = re.findall(r"\d*[.,]\d*", word)

                # should never be the case
                if len(decimals) < 1:
                    print(word, decimals, "ERROR!")
                    break
                
                price = float(decimals[-1].replace(",","."))
                # store as int in cents to avoid floating point errors
                price = int(round(price*100,0))

                break

            else:
                price = -1

        lPrices.append(price)

        # receipt operating dict
        if price != -1:

            dPriceScan[cRS] = {}
            dPriceScan[cRS]["price"] = price
            dPriceScan[cRS]["position"] = i
            dPriceScan[cRS]["used"] = 0
            dPriceScan[cRS]["section"] = 0
            dPriceScan[cRS]["product"] = (" ").join(words[:(len(words) - c - 1)]) + ((" ( " + itemQty + " )") if itemQty else "")
            cRS += 1

            itemQty = ""    



    # -- Section detection and assignment --

    iSectionCount = 1

    # loop over all elements to check for max if not used already
    for l, m in dPriceScan.items():
        if m["used"] == 1:
            continue
    
        maxPrice = 0
        maxNum = [-1,-1]

        # small loop to check for maximum
        for k, i in dPriceScan.items():
            
            if i["used"] == 1:
                continue

            if i["price"] > maxNum[0]:
                maxNum[0] = i["price"]
                maxNum[1] = k

        # flag found maximum as used so it will not be used again
        dPriceScan[maxNum[1]]["used"] = 1

        
        # dict for prices in proximity of max --> avoid accidental combinations being found
        dPriceSum = {k: i for k, i in dPriceScan.items() if k > maxNum[1]-3 and i["used"] != 1 and i["section"] == 0}
        maxNumSum = 0
        lSumCmponents = []
        # needed to check if all available components have been used in an incomplete sum, so to force section allocation, see (ref: dpsc)
        dPriceSumCheck = {k: i for k, i in dPriceScan.items() if i["used"] != 1 and i["section"] == 0}

        # check for sum components
        for c, (k, i) in enumerate(dPriceSum.items()):
            
            maxNumSum += i["price"]
            lSumCmponents.append(k)
            
            # >dpsc
            if maxNumSum == maxNum[0] or len(lSumCmponents) == len(dPriceSumCheck.items()): 
                
                for k, i in dPriceScan.items():
                    
                    # assign all components to the active section
                    if k <= max(lSumCmponents) and i["section"] == 0:
                        i["section"] = iSectionCount
                    else: continue
                
                iSectionCount += 1

                break
    

    # copy sections into final receipt dict. 
    for s in range(0,iSectionCount):

        lItemsInSection = [i for k, i in dPriceScan.items() if i["section"] == s]

        if not lItemsInSection: continue 

        receipt[s] = {}

        for c, p in enumerate(lItemsInSection): 
            receipt[s][c] = p

    return receipt


def udf_printSectionItems(p_dict):
    # print results
    for k, r in p_dict.items():
        print(f"Section: {k}")

        for a, b in r.items():
            print(f"\t Items: {b}")


def udf_readJSONdir():

    jsDir = "../media/testFiles/output/json"
    txtDir = "../media/testFiles/output/txt"

    for fj in os.listdir(jsDir):

        with open(os.path.join(jsDir,fj), "r") as jFile:
            data = js.load(jFile)


        sNewFileName = fj.split(".",1)[0].lower() + ".txt"
        sNewFileName_json = fj.split(".",1)[0].lower() + ".json"


        with open(os.path.join(txtDir, sNewFileName), "w") as output:
            for line in data["ParsedResults"][0]["ParsedText"].strip("\n").split("\r"):
                output.write(line)

        with open(os.path.join(txtDir, sNewFileName), "r") as f:
            

            receipt = {}
            dPriceScan = {}

            # create list for reprocessing (instead of resetting the cursor)
            lFile = [line.strip("\n \t") for line in f]
            lPrices = []
            
            iTotal = 0
            iRunTotal = 0
            cRS = 0 # count ReceiptScan = cRS
            fTotal = 0.0
            
            sSection = "footer"
            iCountSection = 0
            itemQty = ""

            # look from bottom of the file to find total first
            for i, line in enumerate(lFile[::-1]):
                words = line.split("\t")
                
                # check if last item in word is a linebreak
                if words[-1] == "\n":
                    words.pop(len(words)-1)

                reQty = re.compile(r"\d\s?[xX]\s?")
                matchQty = reQty.search((" ").join(words[:]))
                # print(line)
                if matchQty:
                    itemQty = (" ").join(words)
                    price = -1
                    continue

                # sentence loop
                for c, word in enumerate(words[::-1]):
                    reCheck = re.compile(r"\d[.,]\d")
                    match = reCheck.search(word)
                    
                    if match: 
                        decimals = re.findall(r"\d*[.,]\d*", word)

                        # should never be the case
                        if len(decimals) < 1:
                            print(word, decimals, "ERROR!")
                            break
                        
                        price = float(decimals[-1].replace(",","."))
                        # store as int in cents to avoid floating point errors
                        price = int(round(price*100,0))

                        break

                    else:
                        price = -1

                lPrices.append(price)

                # receipt operating dict
                if price != -1:

                    dPriceScan[cRS] = {}
                    dPriceScan[cRS]["price"] = price
                    dPriceScan[cRS]["position"] = i
                    dPriceScan[cRS]["used"] = 0
                    dPriceScan[cRS]["section"] = 0
                    dPriceScan[cRS]["product"] = (" ").join(words[:(len(words) - c - 1)]) + ((" ( " + itemQty + " )") if itemQty else "")
                    cRS += 1

                    itemQty = ""    



            # -- Section detection and assignment --

            iSectionCount = 1

            # loop over all elements to check for max if not used already
            for l, m in dPriceScan.items():
                if m["used"] == 1:
                    continue
            
                maxPrice = 0
                maxNum = [-1,-1]

                # small loop to check for maximum
                for k, i in dPriceScan.items():
                    
                    if i["used"] == 1:
                        continue

                    if i["price"] > maxNum[0]:
                        maxNum[0] = i["price"]
                        maxNum[1] = k

                # flag found maximum as used so it will not be used again
                dPriceScan[maxNum[1]]["used"] = 1

                
                # dict for prices in proximity of max --> avoid accidental combinations being found
                dPriceSum = {k: i for k, i in dPriceScan.items() if k > maxNum[1]-3 and i["used"] != 1 and i["section"] == 0}
                maxNumSum = 0
                lSumCmponents = []
                # needed to check if all available components have been used in an incomplete sum, so to force section allocation, see (ref: dpsc)
                dPriceSumCheck = {k: i for k, i in dPriceScan.items() if i["used"] != 1 and i["section"] == 0}

                # check for sum components
                for c, (k, i) in enumerate(dPriceSum.items()):
                    
                    maxNumSum += i["price"]
                    lSumCmponents.append(k)
                    
                    # >dpsc
                    if maxNumSum == maxNum[0] or len(lSumCmponents) == len(dPriceSumCheck.items()): 
                        
                        for k, i in dPriceScan.items():
                            
                            # assign all components to the active section
                            if k <= max(lSumCmponents) and i["section"] == 0:
                                i["section"] = iSectionCount
                            else: continue
                        
                        iSectionCount += 1

                        break
            

            # copy sections into final receipt dict. 
            for s in range(0,iSectionCount):

                lItemsInSection = [i for k, i in dPriceScan.items() if i["section"] == s]

                if not lItemsInSection: continue 

                receipt[s] = {}

                for c, p in enumerate(lItemsInSection): 
                    receipt[s][c] = p


            return receipt


            



