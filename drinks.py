"""
drinks.py - A  Flask application with GET /drinks?type=<type>

Usage: Run `export FLASK_APP=drinks` followed by `python3 -m flask run` to ensure the env is py3.

Project: Building an api to retrieve and transfrom drinks data from two public apis (coffee & beer).

Author: Zhang Shiyu
Date: 20 Dec 2021
"""


from collections import namedtuple
from flask import Flask, jsonify, request
from functools import lru_cache, cmp_to_key
import random
import requests
import re
import uuid

app = Flask(__name__)

COFFEE_API = "https://api.sampleapis.com/coffee/hot"
BEER_API = "https://api.sampleapis.com/beers/ale"
DEFAULT_IMAGE_API = "https://coffee.alexflipnote.dev/random.json"

DrinkItem = namedtuple(
    "Drink", ["name", "price", "rating", "description", "image", "id"]
)

BEER_DESCRIPTION = {
    "ale": "Ale is a general category of beer: You'll find sub-categories like brown ales or pale ales. This is the oldest style of beer, which dates back to antiquity. What distinguishes an ale - and also makes this category of beer accessible for home brewers - is a warm-temperature fermentation for a relatively short period of time. In the brewing process, brewers introduce top-fermenting yeasts which, as the name suggests, ferment on the top of the brew. The fermentation process turns what would otherwise be a barley and malt tea into a boozy beverage.",
    "porter": "A type of ale, porter beers are known for their dark black color and roasted malt aroma and notes. Porters may be fruity or dry in flavor, which is determined by the variety of roasted malt used in the brewing process.",
    "stout": "Like porters, stouts are dark, roasted ales. Stouts taste less sweet than porters and often feature a bitter coffee taste, which comes from unmalted roasted barley that is added to the wort. They are characterized by a thick, creamy head. Ireland's Guinness may be one of the world's best-known stouts.",
    "brownale": "Brown ales range in color from amber to brown, with chocolate, caramel, citrus, or nut notes. Brown ales are a bit of a mixed bag, since the different malts used and the country of origin can greatly affect the flavor and scent of this underrated beer style.",
    "paleale": "An English style of ale, pale ales and known for their copper color and fruity scent. Don't let the name fool you: these beers are strong enough to pair well with spicy foods.\n\nRelated to the pale is the APA, or American Pale Ale, which is somewhat of a hybrid between the traditional English pale ale and the IPA style. American pale ales are hoppier and usually feature American two row malt.",
    "ipa": "Originally, India Pale Ale or IPA was a British pale ale brewed with extra hops. High levels of this bittering agent made the beer stable enough to survive the long boat trip to India without spoiling. The extra dose of hops gives IPA beers their bitter taste. Depending on the style of hops used, IPAs may have fruit-forward citrus flavors or taste of resin and pine.\n\nAmerican brewers have taken the IPA style and run with it, introducing unusual flavors and ingredients to satisfy U.S. beer drinkers' love for the brew style.",
}


def _getDataFromEndPoint(url):
    """Get data from given API. The returned data format must be dict."""
    data = []
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)
    return data


@lru_cache
def _getDefaultImage():
    """Get a default image url from DEFAULT_IMAGE_API"""
    data = _getDataFromEndPoint(DEFAULT_IMAGE_API)
    return data.get("file")


def getBeerDescription(name):
    """Get description for beer item.
    Input: name of beer
    Output: if name of beer ends with the predefined beer types (keys of BEER_DESCRIPTION), returns the longest match key's value. This matching is regardless of empty space and captial/small characters.
    If no result found, return ""."""
    description = ""
    beerTypes = sorted(
        [
            "{}$".format(beerType.replace(" ", "").lower())
            for beerType in list(BEER_DESCRIPTION)
        ],
        key=len,
        reverse=True,
    )
    patternStr = "|".join(beerTypes)

    m = re.search(patternStr, name.replace(" ", "").lower())
    if m:
        description = BEER_DESCRIPTION[m.group()]
    return description


def postProcess(data, drinkType):
    """Post process of data by given drinkType: either "coffee" or "beer".
    Including data cleaning to remove empty value and reformatting into a dictionary with keys:
    ["name", "price", "rating", "description", "image", "id"]"""
    results = []

    for row in data:
        if not row:
            continue
        try:
            if drinkType == "coffee":
                name = row["title"]
                price = "${}.99".format(random.randint(8, 19))
                rating = "{:.3f}".format(random.uniform(1, 5))
                description = row["description"]
                imageLink = _getDefaultImage()
                drinkId = str(uuid.uuid4())

            if drinkType == "beer":
                name = row["name"]
                price = row["price"]
                rating = "{:.3f}".format(row["rating"]["average"])
                description = getBeerDescription(name)
                imageLink = row["image"]
                drinkId = str(uuid.uuid4())
            drinkItem = DrinkItem(name, price, rating, description, imageLink, drinkId)
            results.append(dict(drinkItem._asdict()))
        except KeyError as keyError:
            print(row, " is dropped due to missing value")
            print(keyError)
            continue
    return results


def getCoffeeData():
    """Get coffee data from predefined API and transform into required format."""
    coffeeData = _getDataFromEndPoint(COFFEE_API)
    cleanedCoffeeData = postProcess(coffeeData, "coffee")
    return cleanedCoffeeData


def getBeerData():
    """Get coffee data from predefined API and transform into required format."""
    beerData = _getDataFromEndPoint(BEER_API)
    cleanedBeerData = postProcess(beerData, "beer")
    return cleanedBeerData


def _compareRanking(x, y):
    """Compare rating value of two drink items.
    Return positive if the second value is larger."""
    return float(y["rating"]) - float(x["rating"])


def getAllDrinksData():
    """Get data for both coffee and beer.
    Return a list of all drinks sorted by highest ranking drink first."""
    allData = []
    allData.extend(getCoffeeData())
    allData.extend(getBeerData())
    allData = sorted(allData, key=cmp_to_key(_compareRanking))
    return allData


@app.route("/drinks", methods=["GET"])
def queryDrinks():
    """API entry point"""
    try:
        drinkType = request.args["type"]
        if drinkType == "coffee":
            response = jsonify(getCoffeeData())
            response.status_code = 200
        elif drinkType == "beer":
            response = jsonify(getBeerData())
            response.status_code = 200
        elif drinkType == "":
            response = jsonify(getAllDrinksData())
            response.status_code = 200
        else:
            response = jsonify("Please enter type either <coffee> or <beer>.")
            response.status_code = 500
    except KeyError:
        response = jsonify(getAllDrinksData())
        response.status_code = 200
    finally:
        return response
