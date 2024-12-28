import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

def is_within_last_5_years(date_obj):
    five_years_ago = datetime.now() - timedelta(days=5*365)
    return date_obj >= five_years_ago

def categorize_press_release(title, body=""):
    t_lower = title.lower()
    if any(word in t_lower for word in ["approval", "approve", "authorized", "fda"]):
        return "Regulatory Approval"
    elif any(word in t_lower for word in ["clinical trial", "phase", "study"]):
        return "Clinical Trial Update"
    elif any(word in t_lower for word in ["financial", "dividend", "finance", "earnings", "q1", "q2"]):
        return "Financial News"
    elif any(word in t_lower for word in ["appoint", "ceo", "executive", "board of directors"]):
        return "Management Update"
    elif any(word in t_lower for word in ["launch", "commercial"]):
        return "Commercialized Drug Update"
    else:
        return "Other"

def extract_categories(text_div):
    categories = []
    cat_list = text_div.find("ul", class_="filter-list__list")
    if not cat_list:
        return categories
    cat_items = cat_list.find_all("li")
    for cat in cat_items:
        cat_a = cat.find("a", class_="tag")
        if cat_a:
            cat_text = cat_a.get_text(strip=True)
            categories.append(cat_text)
    return categories

def scrape_pfizer_press_page(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve page: {url}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    press_data = []
    result_lists = soup.find_all("ul", class_="result-list")

    for rlist in result_lists:
        releases = rlist.find_all("li", class_="grid-x")
        for item in releases:
            date_div = item.find("div", class_="cell small-12 medium-12 lmedium-2")
            if not date_div:
                continue
            date_tag = date_div.find("p", class_="date")
            if not date_tag:
                continue

            raw_date = date_tag.get_text(strip=True)  # e.g. "12.19.2024"
            try:
                date_obj = datetime.strptime(raw_date, "%m.%d.%Y")
            except ValueError:
                continue

            # Filter out older than 5 years
            if not is_within_last_5_years(date_obj):
                continue

            text_div = item.find("div", class_="cell small-12 medium-12 lmedium-10")
            if not text_div:
                continue

            title_h5 = text_div.find("h5")
            if not title_h5:
                continue
            link_a = title_h5.find("a")
            if not link_a:
                continue

            title = link_a.get_text(strip=True)
            link = link_a.get("href")
            
            cats = extract_categories(text_div)

            # Use your custom function to get the broader “bucket” category
            high_level_category = categorize_press_release(title)

            press_data.append({
                "Date": date_obj.strftime("%Y-%m-%d"),
                "Company": "Pfizer",
                "Title": title,
                "URL": "https://www.pfizer.com" + link,
                "Tags": ", ".join(cats),
                "Category": high_level_category
            })

    return press_data

def scrape_pfizer():
    """
    Example function that scrapes multiple pages.
    """
    all_press = []
    base_url = ("https://www.pfizer.com/newsroom/press-releases"
                "?field_tags_target_id%5B22256%5D=22256&page=")

    for page_num in range(0, 10):  # Adjust how many pages you want to try
        url = base_url + str(page_num)
        page_results = scrape_pfizer_press_page(url)
        if not page_results:
            break
        all_press.extend(page_results)

    return all_press

def main():
    pfizer_data = scrape_pfizer()
    # Create DataFrame
    df = pd.DataFrame(pfizer_data)
    # Sort by date descending
    df.sort_values("Date", ascending=False, inplace=True)
    df.to_excel("pfizer_press_releases.xlsx", index=False)
    print(f"Scraped {len(df)} Pfizer press releases into pfizer_press_releases.xlsx")

if __name__ == "__main__":
    main()
