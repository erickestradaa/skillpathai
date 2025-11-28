# job_platform_links.py

import urllib.parse

def build_job_search_links(role):
    """Builds public job search URLs for major job boards."""
    
    q = urllib.parse.quote(role)

    return {
        "linkedin": f"https://www.linkedin.com/jobs/search/?keywords={q}",
        "seek": f"https://www.seek.com.au/{q}-jobs",
        "indeed": f"https://www.indeed.com/jobs?q={q}"
    }
