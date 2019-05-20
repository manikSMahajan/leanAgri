import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pandas as pd
import os
import json
import sys

diseases = None
origin = None
imageLink = None
suspectSpacimens = None
identification = None
comeInto = None
idComeIntoSpaciList  = []
col1 = "Disease Name"
col2= "Origin"
col3 = "Image Link"
col4 = "Identification"
col5 = "Come Into Australia"
col6 = "Suspact Spacimens"
imageDir = "./images/"

def getDiseaseName(soup1):
    global  diseases
    for header in soup1.find_all("h1"):
        diseases = (header.text).strip()

def getLink(soup1,urlWithoutEndPoint):
    global imageLink, diseases
    for img in soup1.find_all("div"):
                if img.get("class") is not None:
                    if ('pest-header-image' in img.get("class")):
                        for img1 in img.find_all("img"):
                            imageLink = urlWithoutEndPoint + img1.get("src")

    if imageLink is not None:
        status = requests.get(imageLink, stream=True)
        if status.status_code == 200:
            if not os.path.exists(imageDir):
                os.makedirs(imageDir)
            with open(imageDir + diseases, "wb") as f:
                for chunk in status:
                    f.write(chunk)

def getOrigin(soup1):
    global  origin
    for div in soup1.find_all("div"):
        divclass = div.get("class")
        if divclass is not None:
            if "pest-header-content" in divclass:
                for para in div.find_all("p"):
                    for strong in para.find_all("strong"):
                        if   "Origin" in strong.text.strip():
                           origin = strong.next_sibling.strip()

def getIdentificationComeIntoSpacimens(soup1):
    global identification, comeInto, suspectSpacimens
    idComeIntoSpaciList = []
    for div in soup1.find_all("div", recursive=True):
        divId = div.get("id")
        if divId is not None:
            if "collapsefaq" in divId:
                    for div1 in div.find_all("div", recursive=True):
                        if div1.get("class") is not None:
                            for div1Class in div1.get("class"):
                                if div1Class is not None:
                                    idComeIntoSpaciList.append(div1.get_text())
                            if len(idComeIntoSpaciList) == 3:
                                identification = idComeIntoSpaciList[0]
                                comeInto = idComeIntoSpaciList[1]
                                suspectSpacimens = idComeIntoSpaciList[2]
def main(URL,exelFilePath):
    df =pd.DataFrame(columns=[col1, col2, col3, col4 , col5, col6])
    url = URL
    data = requests.get(url)
    soup = BeautifulSoup(data.text, "html.parser")
    endpoints = []
    index = 0
    for li in soup.find_all("li"):
        if "static dynamic-children selected menu-item" in str(li):
            for a in li.find_all("a"):
                endpoints.append(a.get("href"))

    items = urlparse(url)
    urlWithoutEndPoint = items.scheme + "://" + items.netloc
    for element in endpoints:
        uri = urlWithoutEndPoint + element
        d = requests.get(uri)
        soup1 = BeautifulSoup(d.text, "html.parser")
        getDiseaseName(soup1)
        getOrigin(soup1)
        getLink(soup1, urlWithoutEndPoint)
        getIdentificationComeIntoSpacimens(soup1)

        if diseases and origin and imageLink and identification and comeInto and suspectSpacimens:
            print("Current Diseases Name:%s" % diseases)
            df.loc[index, col1] = diseases
            df.loc[index, col2] = origin
            df.loc[index, col3] = imageLink
            df.loc[index, col4] = identification
            df.loc[index, col5] = comeInto
            df.loc[index, col6] = suspectSpacimens
            writer = pd.ExcelWriter(exelFilePath,
                                            engine='xlsxwriter')  # Convert the
            index += 1
            df.to_excel(writer, sheet_name='Sheet1',
                    index=False)
            writer.save()

if __name__ == "__main__":
    try:
        if len(sys.argv) == 2:
            data = json.load(open(sys.argv[1]))
            main(data["URL"], data["exelFilePath"])
        else:
            print("insufficeint arguments, Taking default config.")
            data = json.load(open("./config.json"))
            main(data["URL"], data["exelFilePath"])
    except FileNotFoundError as error:
        print(error)
    except(ConnectionError, Exception) as error:
        print(error)