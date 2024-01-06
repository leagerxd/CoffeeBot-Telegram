import requests
import httpx
from bs4 import BeautifulSoup

'''
URL = "https://realpython.github.io/fake-jobs/"
page = requests.get(URL)

#print(page.text)
soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(id="ResultsContainer")

#print(results.prettify())

job_elements = results.find_all("div", class_="card-content")



for job_element in job_elements:
    title_element = job_element.find("h2", class_="title")
    company_element = job_element.find("h3", class_="company")
    location_element = job_element.find("p", class_="location")
    print(title_element.text)
    print(company_element.text)
    print(location_element.text)
    print()
'''

urls = [
    'https://newsinfo.inquirer.net',
    'https://entertainment.inquirer.net',
    'https://inquirer.net',
    'https://bandera.inquirer.net',
    'https://cebudailynews.inquirer.net'
]

for url in urls:
    with httpx.Client() as session:
        session.headers = {
            "X-Forwarded-For": '72.208.192.0'
        }
        resp = session.get(url)

        soup = BeautifulSoup(resp.content, 'html.parser')
        results = soup.find(id='mgid-pad')
        if results:
            print(results.prettify())

        # '1523714_09abb')
