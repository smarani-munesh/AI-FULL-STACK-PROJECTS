import requests
from bs4 import BeautifulSoup

def scrape_jobs(skill):
    url = f"https://www.naukri.com/{skill}-jobs"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all("article", class_="jobTuple bgWhite br4 mb-8")

        jobs = []
        for card in job_cards[:5]:  # Limit to 5 jobs
            title_tag = card.find("a", class_="title")
            company_tag = card.find("a", class_="subTitle")
            location_tag = card.find("li", class_="location")

            title = title_tag.text.strip() if title_tag else "N/A"
            company = company_tag.text.strip() if company_tag else "N/A"
            location = location_tag.text.strip() if location_tag else "N/A"
            job_url = title_tag["href"] if title_tag and "href" in title_tag.attrs else "#"

            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "url": job_url
            })

        return jobs if jobs else "❌ No jobs found (try a different keyword)."

    except Exception as e:
        return f"❌ Job scraping failed: {str(e)}"
