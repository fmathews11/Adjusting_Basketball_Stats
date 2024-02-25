import requests
import json

SEASON = 2024


def main() -> None:
    from bs4 import BeautifulSoup

    team_name_id_dict = {}

    # URL for data from all schools
    all_schools_url = f'https://www.sports-reference.com/cbb/seasons/men/{SEASON}-school-stats.html'
    response = requests.get(all_schools_url, timeout=10)
    soup = BeautifulSoup(response.content)
    # Find table ('tr')
    table = soup.findAll('tr')

    # Iterate through rows
    for row in table:
        # Returns a None object if nothing is found
        search = row.find('a', href=True)
        # If we have something
        if search:
            # Extract the name and URL via string manipulation
            url_suffix = str(search).split('"')[1].replace(".html", "")
            team_name = str(search).split(">")[1].replace("</a", "").strip()
            # Update the dictionary
            team_name_id_dict[team_name] = url_suffix.split("/")[3]

    with open('team_uis.json', 'w') as f:
        json.dump(team_name_id_dict, f)
    print("JSON file written")

    return


if __name__ == '__main__':
    main()
