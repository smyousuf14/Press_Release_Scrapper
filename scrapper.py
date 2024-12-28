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
    """
    A helper function used by the Pfizer scraper to find <ul class="filter-list__list"> 
    categories. For Merck or other sites, you’ll adapt or skip it.
    """
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


# -------------------------- Pfizer Scraping Code --------------------------

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
            
            # Attempt to find any categories in the text_div
            cats = extract_categories(text_div)
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
    Example function that scrapes multiple pages from Pfizer's press site.
    """
    all_press = []
    base_url = ("https://www.pfizer.com/newsroom/press-releases"
                "?field_tags_target_id%5B22256%5D=22256&page=")

    for page_num in range(0, 10):  # Adjust the range as needed
        url = base_url + str(page_num)
        page_results = scrape_pfizer_press_page(url)
        # If no results or no more pages, break early (optional)
        if not page_results:
            break
        all_press.extend(page_results)

    return all_press


# -------------------------- Merck Scraping Code (Placeholder) --------------------------
def scrape_merck():
    """
    Because https://www.merck.com/media/news/ is loaded dynamically,
    a basic requests.get() + BeautifulSoup may not see any press-release items
    in the raw HTML. We'll show a placeholder approach. 
    If Merck eventually has a direct listing of releases, you can adapt accordingly.
    """
    url = "https://www.merck.com/media/news/"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve Merck page: {url}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    press_data = []

    # Attempt to locate any static press release containers in the HTML
    # (In the real site, these may not exist if content is 100% dynamic.)
    # For demonstration, let's say we look for <div class="article"> or similar.
    
    # Example placeholder – searching for something like "article" or "d8-results"
    # In practice, you'd adjust these selectors based on real static content.
    news_wrapper = soup.find("div", class_="entry-content wrapper")
    if not news_wrapper:
        # If no static article area found, return empty.
        return press_data

    # Hypothetical: assume each press release is in <div class="article-headline-link">
    # This is just an example; you will need to adjust once you see real static HTML
    articles = news_wrapper.find_all("div", class_="article-headline-link")

    for item in articles:
        # Try extracting date from a p, span, or somewhere near
        # This is hypothetical code
        date_p = item.find("p", class_="source-date")
        if not date_p:
            continue
        raw_date = date_p.get_text(strip=True)
        # e.g. "December 20, 2024"
        try:
            date_obj = datetime.strptime(raw_date, "%B %d, %Y")
        except ValueError:
            # If parse fails, skip
            continue
        if not is_within_last_5_years(date_obj):
            continue

        # Extract title & link
        link_a = item.find("a")
        if not link_a:
            continue
        title = link_a.get_text(strip=True)
        link = link_a.get("href")
        # If the link might be relative, prefix domain:
        if link and link.startswith("/"):
            link = "https://www.merck.com" + link

        # For tags, Merck might not provide them in the same way as Pfizer
        # So let's do a simple approach:
        tags_text = ""
        # If there's a tag container in the snippet or a small <p> with text
        # we can parse it. Otherwise skip.

        category = categorize_press_release(title)

        press_data.append({
            "Date": date_obj.strftime("%Y-%m-%d"),
            "Company": "Merck",
            "Title": title,
            "URL": link,
            "Tags": tags_text,
            "Category": category
        })

    return press_data


def main():
    # Scrape Pfizer
    pfizer_data = scrape_pfizer()
    df_pf = pd.DataFrame(pfizer_data)

    # Scrape Merck
    merck_data = scrape_merck()
    df_merck = pd.DataFrame(merck_data)

    # Combine them
    combined_df = pd.concat([df_pf, df_merck], ignore_index=True)

    # Sort by date descending
    combined_df.sort_values("Date", ascending=False, inplace=True)

    # Save to Excel
    combined_df.to_excel("combined_press_releases.xlsx", index=False)

    print(f"Scraped {len(df_pf)} Pfizer press releases.")
    print(f"Scraped {len(df_merck)} Merck press releases.")
    print(f"Combined data saved to combined_press_releases.xlsx.")


if __name__ == "__main__":
    main()
