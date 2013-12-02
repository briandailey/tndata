import re
import requests
import csv
from bs4 import BeautifulSoup

offenders_regex = re.compile('^(\d*)')
county_regex = re.compile('^([A-z ]+) County')

def counties_list():
    """ read in list of counties from the text file. """
    counties = {}
    with open('../data/PEP_2012_PEPANNRES_with_ann.csv') as f:
        csvreader = csv.DictReader(f)
        for row in csvreader:
            county = county_regex.match(row['GEO.display-label']).group(1)
            counties[county] = row['respop72012']
    return counties

def meth_per_county(limit=None):
    with open('../data/meth_per_county.csv', 'wb') as f:
        csvwriter = csv.writer(f)
        # Write header
        csvwriter.writerow(['County', 'Population', 'Offenders'])
        for county, population in counties_list().items():
            offenders_dom = dom_from_county(county)

            if not offenders_dom:
                print "Found no offenders text for {county}.".format(county=county)
                csvwriter.writerow([county, population, 0])
                continue

            matches = offenders_regex.match(offenders_dom.text)
            if not matches:
                print "No regex match on {county}.".format(county=county)
                print offenders_dom.text
                continue

            number_of_offenders = matches.group(0)

            csvwriter.writerow([county, population, number_of_offenders])

            if limit:
                break

def dom_from_county(county, css_class="pagebanner"):
    """Return dom from TN Meth offenders app"""
    url = 'https://apps.tn.gov/methor-app/search.do'
    payload = {'county': county.upper()}
    r = requests.post(url, data=payload)
    soup = BeautifulSoup(r.text)
    return soup.find(attrs={"class": css_class})
