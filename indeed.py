import requests 
from bs4 import BeautifulSoup
import time


class job_posting(object):
    def __init__(self,title,company,loc,date,link):
        self.title = title
        self.company = company
        self.loc = loc
        self.date = date
        self.link = 'https://www.indeed.com/' + link
    def to_dict(self):
        return {
                'Title' : self.title,
                'Company' : self.company,
                'Location' : self.loc,
                'Date' : self.date,
                'Link' : self.link
                }


def generate_url(position,location=None,state=None):
    position = position.split()
    title = ''
    loc = ''
    for i, word in enumerate(position):
        title += word
        if i < len(position) - 1:
            title += '+'
    if location is not None:
        city = location.split()
        for i, word in enumerate(city):
            loc += word
            if i < len(location) - 1:
                loc += '+'
        loc = loc + '%2C+' + state
        url = 'https://www.indeed.com/jobs?q=%s&l=%s&start='%(title,loc)
    else:
        url = 'https://www.indeed.com/jobs?q=%s&start='%(title)
    return url

def get_job_postings(url,max_results):   
    jobs = []
    for start in range(0, max_results, 15):
        page = requests.get(url+str(start))
        soup = BeautifulSoup(page.text, 'html.parser')
        time.sleep(.5)
        for div in soup.find_all(name='div', attrs={'class':'row'}):
            company = div.find_all(name='span', attrs={'class':'company'})
            title_link = div.find_all(name='a', attrs={'data-tn-element':'jobTitle'})
            date = div.find_all(name='span', attrs={'class':'date'})
            loc = div.find_all(name='span', attrs={'class':'location'})
            if len(date) < 1 or len(loc) < 1 or len(company) < 1 or len(title_link) < 1:
                continue
            else:
                jobs.append(job_posting(title_link[0].text,company[0].text.strip(),loc[0].text.strip(),date[0].text.strip(),title_link[0]['href']))
    return jobs
   
def get_jobs(position,location,state,max_postings):
    url = generate_url(position,location,state)
    jobs = get_job_postings(url,max_postings)
    return jobs


def min_to_day(minutes):
    return float(minutes)/(60.*24)

def hour_to_day(hours):
    return float(hours)/(24.)

def sort_by_date(jobs):
    time_dict = {}
    for job in jobs:
        date = job.date
        date = date.split()
        if date[1][0] == 'm':
            val = min_to_day(date[0])
        elif date[1][0] == 'h':
            val = hour_to_day(date[0])
        else:
            if date[0].find('+') >= 0:
                continue
            else:
                val = int(date[0])
        time_dict[val] = job
    time_sorted = []
    for date in sorted(time_dict.keys()):
        time_sorted.append(time_dict[date])
    return time_sorted

            

        
def job_search(position,max_postings=100,location=None,state=None):    
    jobs = get_jobs(position,location,state,max_postings)
    sort_jobs = sort_by_date(jobs)
    return sort_jobs
        

    
