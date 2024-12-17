import requests
from bs4 import BeautifulSoup

def fetch_school_closures():
    url = "https://www.nbcconnecticut.com/weather/school-closures/"
    
    # Fetch the page content
    response = requests.get(url)
    
    # Ensure we successfully retrieved the page
    if response.status_code != 200:
        print("Failed to retrieve the webpage.")
        return []

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Debugging: Print the HTML content or part of it
    # This will help you identify the structure of the webpage
    # Uncomment the next line to view the raw HTML
    print(soup.prettify())

    # Find all schools (check for a different class if 'school-name' is incorrect)
    closures = soup.find_all('div', class_='school-name')
    delays = soup.find_all('div', class_='delay-status')  # Update this selector if necessary

    # Debugging: Print what we found
    print(f"Found {len(closures)} closures.")
    print(f"Found {len(delays)} delays.")

    school_data = []

    # Check if closures and delays match in length
    if len(closures) != len(delays):
        print("Warning: The number of closures and delays do not match.")

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