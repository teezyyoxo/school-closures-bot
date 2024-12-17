import requests
from bs4 import BeautifulSoup

def fetch_school_closures():
    url = "https://www.nbcconnecticut.com/weather/school-closings/"
    
    # Fetch the page content
    response = requests.get(url)
    
    # Ensure we successfully retrieved the page
    if response.status_code != 200:
        print("Failed to retrieve the webpage.")
        return []

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Inspect the structure of the page to identify where closures are listed.
    # These selectors may need to be updated if the webpage's structure 
changes.
    closures = soup.find_all('div', class_='school-name')  # Change this if the 
actual tag/class is different
    delays = soup.find_all('div', class_='delay-status')  # Change this if 
needed

    school_data = []

    # Zip the closures and delays together and extract relevant info
    for school, delay in zip(closures, delays):
        school_data.append({
            'school': school.text.strip(),
            'status': delay.text.strip()
        })

    return school_data

# Example usage
if __name__ == "__main__":
    closures = fetch_school_closures()
    for closure in closures:
        print(f"{closure['school']}: {closure['status']}")

# bring it aroundddddddddd town
for school, delay in zip(closures, delays):
    school_data.append({
        'school': school.text.strip(),
        'status': delay.text.strip()
    })

