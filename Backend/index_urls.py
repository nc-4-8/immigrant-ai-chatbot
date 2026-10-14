from src.qdrant import upload_website_to_collection

urls = [
    "https://www.uscis.gov/green-card",
    "https://www.uscis.gov/citizenship",
    "https://www.usa.gov/health-insurance",
    "https://www.usa.gov/learn-english",
    "https://www.usa.gov/immigration-and-citizenship",
    "https://www.justice.gov/eoir/self-help-materials",
    "https://iamerica.org/immigrant-resources/",
    "https://www.aclu.org/issues/immigrants-rights",
    "https://www.nilc.org/resources/",
    "https://www.ilrc.org/community-resources",
    "https://unitedwedream.org/resources/",
    "https://immigrantsrising.org/resources/",
]

for url in urls:
    try:
        upload_website_to_collection(url)
    except Exception as e:
        print(f"Failed: {url} -> {e}")