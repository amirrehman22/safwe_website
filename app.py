import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd
import streamlit as st

# Streamlit app title
st.title("Carrier Email Scraper")

# Input fields for range of carrier IDs
start_id = st.number_input("Enter start Carrier ID:", min_value=1, value=1615900)
end_id = st.number_input("Enter end Carrier ID:", min_value=start_id+1, value=1615905)

# Button to start scraping
if st.button("Scrape Emails"):

    def fetch_page(url):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                st.warning(f"Failed to retrieve {url} - Status code: {response.status_code}")
                return None
        except requests.RequestException as e:
            st.error(f"An error occurred: {e}")
            return None

    def extract_emails(html):
        emails = []
        if html:
            soup = BeautifulSoup(html, "html.parser")

            # Option 1: look for <label>Email:> and extract value
            email_label = soup.find("label", string="Email: ")
            if email_label:
                email_span = email_label.find_next("span", class_="dat")
                if email_span:
                    email = email_span.get_text(strip=True)
                    if email:
                        emails.append(email)

            # Option 2: fallback - regex search for any email patterns in the page
            regex_emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", html)
            for e in regex_emails:
                if e not in emails:
                    emails.append(e)

        return emails

    results = []

    # Loop through carrier IDs
    for carrier_id in range(int(start_id), int(end_id)):
        url = f"https://ai.fmcsa.dot.gov/SMS/Carrier/{carrier_id}/CarrierRegistration.aspx"
        html = fetch_page(url)
        emails = extract_emails(html)
        email_str = emails[0] if emails else ""  # take first email or empty string
        results.append({"Emails": email_str})
        st.write(f"Carrier ID {carrier_id}: {emails}")
        time.sleep(1)  # polite delay


    # Convert results to DataFrame
    df = pd.DataFrame(results)
    #df = df.dropna(subset=["Emails"])  # remove rows where Emails column is NaN
    # Suppose df is your DataFrame
    df = df[df["Emails"] != ""]  # remove rows with empty string


    # Display DataFrame in Streamlit
    #st.dataframe(df)

    # Button to download CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download CSV", data=csv, file_name="carrier_emails.csv", mime="text/csv")
