########################################
# ©Copyright 2023. Guillermo Uribarren #
########################################
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

#######################################################
# This code uses ScrapeOps proxy service
# Get a Free Account at https://scrapeops.io/
# Replace empty string with your own ScrapeOps API KEY
#######################################################

API_KEY = ''

def proxy_request(url):
    response = requests.get(
        url='https://proxy.scrapeops.io/v1/',
        params={
            'api_key': API_KEY,
            'url': url,
            'country': 'mx',
        },
    )
    return response


def get_indeed_jobs(query, location):

    base_url = "https://mx.indeed.com"
    url = base_url +'/jobs?q=' + query + '&l=' + location + '&fromage7'
    response = proxy_request(url)
    results = []

    #######################################################
    # Parse Indeed Jobs response
    #######################################################
    soup = BeautifulSoup(response.text, "html.parser")
    job_elements = soup.find_all("div", class_="job_seen_beacon")

    for job_element in job_elements:
        job_title = job_element.find("h2", class_="jobTitle").text.strip()
        job_url = base_url + job_element.find("a").get("href")
        company = job_element.find("span", class_="companyName").text.strip()
        location = job_element.find("div", class_="companyLocation").text.strip()
        job_salary = ""

        try:
            if job_element.find("div", class_="attribute_snippet") is not None:
                job_salary = job_element.find("div", class_="attribute_snippet").text
            else:
                job_salary = "No info"

            job_offer_page = proxy_request(job_url)
            job_offer_soup = BeautifulSoup(job_offer_page.text, "html.parser")
            job_description = job_offer_soup.find("div", id="jobDescriptionText").get_text().strip()

        except IndexError as err:
            print(err)

        job_info = {
            "key_word": query,
            "job_title": job_title,
            "company": company,
            "location": location,
            "salary": job_salary,
            "job_offer_url": job_url,
            "job_description": job_description
        }
        results.append(job_info)

    return results


if __name__ == "__main__":

    #######################################################
    # Write custom values to queries variable
    # queries = ["profesor", "pedagogía", "..."]
    #######################################################
    queries = ["moodle", "blackboard", "brightspace", "canvas", "sakai lms", "google classroom"]
    #######################################################
    # Write custom values to find jobs near your location
    # location = "Ciudad de México"
    #######################################################
    location = "Ciudad de México"

    results = []
    for query in queries:
        print("Searching " + query + " jobs.")
        jobs = get_indeed_jobs(query, location)

        for job in jobs:
            results.append(job)

    df = pd.DataFrame(results)

    fecha_sin_formato = datetime.today()
    fecha = fecha_sin_formato.strftime("%Y-%m-%d %H:%M:%S")
    df.to_excel(fecha + '_job_offers.xlsx', index=False)
