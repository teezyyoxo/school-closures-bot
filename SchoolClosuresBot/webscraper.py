# i can't figure out the libreSSL nonsense. error doesn't show when run with python3.9, but does with python3.
# so, the below will suppress the error messaging:
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')
# phew.

import requests
from bs4 import BeautifulSoup

# we're using NBC Connecticut for this one, so the URL is usually this: https://www.nbcconnecticut.com/weather/school-closings/
# but there are no closings currently, so i have no way to test. so i'm using an archived page from a few days ago for testing.
# MAKE SURE TO CHANGE THIS!
school_closures_url = "https://web.archive.org/web/20241212072827/https://www.nbcconnecticut.com/weather/school-closings/"

# Function to fetch school closures
def fetch_school_closures():
    url = school_closures_url  # Use the variable here
    # Your code for fetching the school closures goes here

    
    # Fetch the page content
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Failed to retrieve the webpage.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the section that contains the school closures
    closures_section = soup.find_all('div', class_='listing')

    school_data = []

    # Loop through each listing to extract the school name and status
    for closure in closures_section:
        school_name = closure.find('h4', class_='listing__org').text.strip()
        status = closure.find('p', class_='listing__notice').text.strip()

        school_data.append({
            'school': school_name,
            'status': status
        })

    return school_data

# Example usage
if __name__ == "__main__":
    closures = fetch_school_closures()
    for closure in closures:
        print(f"{closure['school']}: {closure['status']}")
