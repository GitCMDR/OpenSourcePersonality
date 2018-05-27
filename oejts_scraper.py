# Web Scraper for Open Extended Jungian Type Scales 1.2
import requests
from bs4 import BeautifulSoup
from generator import item_pool_generator
from random import randint
from tenacity import retry
import tenacity


@retry(wait=tenacity.wait_random_exponential(multiplier=1, max=60), stop=tenacity.stop_after_attempt(15))
def datasetGenerator():
    # Generate Item Pool
    item_pool = item_pool_generator()

    # PAGE 1
    r = requests.get("https://openpsychometrics.org/tests/OEJTS/")
    soup = BeautifulSoup(r.text, 'html.parser')

    # Save Post Details for Next Call
    UNQID = soup.find_all("input")[0]["value"]
    SECONDS = soup.find_all("input")[1]["value"]

    # PAGE 2
    # Prepare Payload
    payload = {
        "unqid": UNQID,
        "seconds": SECONDS
    }

    # Post Payload and Parse Results
    r = requests.post("https://openpsychometrics.org/tests/OEJTS/1.php", data=payload)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Save Post Details for Next Call
    UNQID = soup.find_all("input")[0]["value"]
    SECONDS = soup.find_all("input")[1]["value"]

    # PAGE 3
    # Prepare First Payload (28 Questions - Answer 1:5)
    UserPayload = {
        "unqid": UNQID,
        "seconds": SECONDS,
        "complete": 1
    }

    FirstPayload = {}
    for i in range(1, 28 + 1):
        FirstPayload["Q" + str(i)] = randint(1, 5)

    # Prepare Second Payload
    SecondPayload = {}
    for i in range(1, 28 + 1):
        SecondPayload["S" + str(i)] = randint(1, 5)

    count = 1
    while count < 28 + 1:
        generatedNumber = randint(2265, 2775)
        if generatedNumber not in SecondPayload:
            SecondPayload["S" + str(count) + "I"] = generatedNumber
            count += 1

    partialResultData = {**FirstPayload, **SecondPayload}  # Saving partialResultData to return

    payload = {**UserPayload, **FirstPayload, **SecondPayload}  # Merge first two dictionaries into one.

    # Post Payload and Parse Results
    r = requests.post("https://openpsychometrics.org/tests/OEJTS/2.php", data=payload)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Get Results
    # Retrieve POST Link
    postURL = soup.find_all('input')[8]['onclick'].split("action='")
    postURL = postURL[1].split("';")
    postURL = postURL[0]
    postURL = "https://openpsychometrics.org/tests/OEJTS/" + postURL

    # Prepare final Payload
    payload = {
        "IE": soup.find(attrs={"name": "IE"})["value"],
        "SN": soup.find(attrs={"name": "SN"})["value"],
        "JP": soup.find(attrs={"name": "JP"})["value"],
        "FT": soup.find(attrs={"name": "FT"})["value"],
        "surveyid": "basicpersonalitysup",
        "ptestaccurate": 2,  # Are answers accurate and can be used for research? 2 = No.
        "pparticipate": 2,  # Do you want to participate in next step? 2 = No.
        "unqid": soup.find(attrs={"name": "unqid"})["value"],
        "seconds": soup.find(attrs={"name": "seconds"})["value"],
        "surveyorid": "basicpersonalitysup",
        "frompage": 2
    }

    # Post Payload and Parse Results
    r = requests.post(postURL, data=payload)
    soup = BeautifulSoup(r.text, 'html.parser')

    resultType = soup.find('iframe')["src"].split("/")
    resultType = resultType[-1]
    resultType = resultType.split('.')[0]

    target = {
        "resultType": resultType
    }

    finalPayloadToReturn = {**partialResultData, **target}

    return finalPayloadToReturn
