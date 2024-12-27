import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

################################################################################
# 1. Helper Functions
################################################################################

def is_within_last_5_years(date_obj):
    """
    Checks if a datetime object is within the last 5 years from today.
    """
    five_years_ago = datetime.now() - timedelta(days=5 * 365)
    return date_obj >= five_years_ago

def categorize_press_release(title, body=""):
    """
    Very simple keyword-based categorization.
    You can expand these keywords or use a more robust approach (NLP) if needed.
    """
    title_lower = title.lower()
    body_lower = body.lower()

    # Check for Regulatory Approval
    if any(keyword in title_lower for keyword in ["approval", "approve", "authorized", "authorization", "fda"]):
        return "Regulatory Approval"
    # Check for Clinical Trial
    elif any(keyword in title_lower for keyword in ["clinical trial", "phase", "study", "data readout", "trial update"]):
        return "Clinical Trial Update"
    # Check for Financial News
    elif any(keyword in title_lower for keyword in ["earnings", "revenues", "quarterly", "financial", "annual report", "q1", "q2", "q3", "q4"]):
        return "Financial News"
    # Check for Management / Executive changes
    elif any(keyword in title_lower for keyword in ["appoint", "ceo", "cfo", "president", "board of directors"]):
        return "Management Update"
    # Check for Commercial/Launch
    elif any(keyword in title_lower for keyword in ["commercial", "launch", "market", "licensing"]):
        return "Commercialized Drug Update"
    else:
        return "Other"

def parse_date_text(date_text, date_formats):
    """
    Tries multiple date_formats (list of format strings) to parse date_text.
    Returns a datetime object or None if all parsing attempts fail.
    """
    for fmt in date_formats:
        try:
            return datetime.strptime(date_text.strip(), fmt)
        except ValueError:
            pass
    return None

################################################################################
# 2. Scraping Pfizer
#    URL: https://www.pfizer.com/newsroom/press-releases
################################################################################

def scrape_pfizer():
    """
    Scrapes press releases from Pfizer for the past 5 years.
    This example uses a hypothetical pattern with page numbering.
    Adjust the logic/pagination as needed based on actual site behavior.
    """
    base_url = "https://www.pfizer.com/newsroom/press-releases?page="

    # From manual observation, see how many pages we might need to check
    # For demonstration, let's assume up to page 20 is enough to go back 5 years.
    max_pages = 20

    pfizer_releases = []

    # The Pfizer date format might look like "September 29, 2023"
    pfizer_date_formats = ["%B %d, %Y"]

    for page_num in range(0, max_pages):
        url = base_url + str(page_num)

        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve page {page_num} for Pfizer.")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # Inspect the Pfizer site to find the correct selectors.
        # Below are placeholders; you need to update them based on the real structure.
        press_items = soup.find_all("div", class_="card")  

        if not press_items:
            # No more items found; we might have reached beyond the last page
            break

        for item in press_items:
            title_tag = item.find("h3", class_="card-title")
            date_tag = item.find("span", class_="card-date")
            link_tag = item.find("a")

            if not (title_tag and date_tag and link_tag):
                continue

            title = title_tag.get_text(strip=True)
            date_text = date_tag.get_text(strip=True)
            link = link_tag.get("href")

            # Parse the date
            date_obj = parse_date_text(date_text, pfizer_date_formats)
            if not date_obj:
                # Could not parse date; skip or handle differently
                continue

            # Filter out press releases older than 5 years
            if not is_within_last_5_years(date_obj):
                continue

            # Attempt to get more details (e.g., summary/body) if needed
            # This might require visiting the link and scraping additional text
            # For demonstration, we'll skip that extra step
            summary_or_body = ""

            # Categorize
            category = categorize_press_release(title, summary_or_body)

            pfizer_releases.append({
                "Date": date_obj.strftime("%Y-%m-%d"),
                "Company": "Pfizer",
                "Title": title,
                "URL": link,
                "Category": category
            })

    return pfizer_releases

################################################################################
# 3. Scraping Merck
#    URL: https://www.merck.com/media/news/
################################################################################

def scrape_merck():
    """
    Scrapes press releases from Merck for the past 5 years.
    """
    base_url = "https://www.merck.com/media/news/page/{page_num}/"

    # Adjust the max_pages based on how many pages are needed.
    max_pages = 20

    merck_releases = []

    # The date format might look like "September 29, 2023" or "Sep 29, 2023"
    merck_date_formats = ["%B %d, %Y", "%b %d, %Y"]

    for page_num in range(1, max_pages+1):
        url = base_url.format(page_num=page_num)
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve page {page_num} for Merck.")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # Inspect Merck's site to find the correct selectors.
        # Below is an example; adjust to the real structure.
        press_items = soup.find_all("article", class_="post")

        if not press_items:
            break

        for item in press_items:
            # Example: find a date in some <span> or <time> tag
            date_tag = item.find("time")
            title_tag = item.find("h2")
            link_tag = item.find("a")

            if not (date_tag and title_tag and link_tag):
                continue

            title = title_tag.get_text(strip=True)
            date_text = date_tag.get_text(strip=True)
            link = link_tag.get("href")

            # Parse date
            date_obj = parse_date_text(date_text, merck_date_formats)
            if not date_obj:
                continue

            # Filter out old press releases
            if not is_within_last_5_years(date_obj):
                continue

            summary_or_body = ""
            category = categorize_press_release(title, summary_or_body)

            merck_releases.append({
                "Date": date_obj.strftime("%Y-%m-%d"),
                "Company": "Merck",
                "Title": title,
                "URL": link,
                "Category": category
            })

    return merck_releases

################################################################################
# 4. Scraping Eli Lilly
#    URL: https://www.lilly.com/news/press-releases
################################################################################

def scrape_lilly():
    """
    Scrapes press releases from Eli Lilly for the past 5 years.
    """
    base_url = "https://www.lilly.com/news/press-releases?page={page_num}"

    max_pages = 20
    lilly_releases = []

    # The date format might look like "September 29, 2023"
    lilly_date_formats = ["%B %d, %Y"]

    for page_num in range(0, max_pages):
        url = base_url.format(page_num=page_num)
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve page {page_num} for Lilly.")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # Inspect Lilly's site for the correct selectors
        press_items = soup.find_all("div", class_="card")

        if not press_items:
            break

        for item in press_items:
            title_tag = item.find("h3")
            date_tag = item.find("span", class_="card-date")
            link_tag = item.find("a")

            if not (title_tag and date_tag and link_tag):
                continue

            title = title_tag.get_text(strip=True)
            date_text = date_tag.get_text(strip=True)
            link = link_tag.get("href")

            date_obj = parse_date_text(date_text, lilly_date_formats)
            if not date_obj:
                continue

            if not is_within_last_5_years(date_obj):
                continue

            summary_or_body = ""
            category = categorize_press_release(title, summary_or_body)

            lilly_releases.append({
                "Date": date_obj.strftime("%Y-%m-%d"),
                "Company": "Eli Lilly",
                "Title": title,
                "URL": link,
                "Category": category
            })

    return lilly_releases


################################################################################
# 5. Main Section
################################################################################

def main():
    """
    Scrape Pfizer, Merck, and Eli Lilly press releases from the last 5 years,
    categorize them, and export to an Excel file.
    """
    print("Scraping Pfizer...")
    pfizer_data = scrape_pfizer()

    print("Scraping Merck...")
    merck_data = scrape_merck()

    print("Scraping Eli Lilly...")
    lilly_data = scrape_lilly()

    # Combine all results
    all_data = pfizer_data + merck_data + lilly_data

    # Convert to DataFrame
    df = pd.DataFrame(all_data, columns=["Date", "Company", "Title", "URL", "Category"])

    # Sort by date descending (newest first) if desired
    df.sort_values(by="Date", ascending=False, inplace=True)

    # Export to Excel
    excel_filename = "pharma_press_releases.xlsx"
    df.to_excel(excel_filename, index=False)

    print(f"Done! Exported {len(df)} press releases to {excel_filename}.")

if __name__ == "__main__":
    main()
