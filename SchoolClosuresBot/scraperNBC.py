import warnings
import requests
from bs4 import BeautifulSoup
import argparse

# i can't figure out the libreSSL nonsense. error doesn't show when run with python3.9, but does with python3.
# so, the below will suppress the error messaging:
warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')

# we're using NBC Connecticut for this one, so the URL is usually this: https://www.nbcconnecticut.com/weather/school-closings/
# but there are no closings currently, so i have no way to test. so i'm using an archived page from a few days ago for testing.
# MAKE SURE TO CHANGE THIS!
live_school_closures_url = "https://www.nbcconnecticut.com/weather/school-closings/"
test_school_closures_url = "https://web.archive.org/web/20241212072827/https://www.nbcconnecticut.com/weather/school-closings/"

# Function to fetch school closures
def fetch_school_closures(url):
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

# Main execution
if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Fetch school closures from NBC Connecticut.")
    parser.add_argument(
        "-t", "--test", 
        action="store_true", 
        help="Run the script in test mode using an archived URL."
    )
    args = parser.parse_args()

    # Determine which URL to use
    school_closures_url = test_school_closures_url if args.test else live_school_closures_url

    # Fetch and display school closures
    closures = fetch_school_closures(school_closures_url)
    
    # Check if no closures were found
    if not closures:
        print("No closures or delays found.")
    
    # Print closures if any
    for closure in closures:
        print(f"{closure['school']}: {closure['status']}")