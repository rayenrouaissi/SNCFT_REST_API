import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.sncft.com.tn/#gl"
response = requests.get(url)

if response.status_code == 200:
    print("Page fetched successfully!")
else:
    print(f"Failed to fetch the page. Status Code: {response.status_code}")


soup = BeautifulSoup(response.content, "html.parser")
dropdown = soup.find("select", {"id": "dep_garre_gl"})
if dropdown:
    options = dropdown.find_all("option")
    
    station_data = []
    
    for option in options:
        station_name = option.text.strip()
        station_id = option.get("value")
        station_data.append({"Station Name": station_name, "Station ID": station_id})
        print(station_name, station_id)  

    df = pd.DataFrame(station_data)
    df.to_csv("train_stations_GL.csv", index=False)
    print("All train stations exported to train_stations_GL.csv")
else:
    print("Dropdown not found.")

soup = BeautifulSoup(response.content, "html.parser")
dropdown = soup.find("select", {"id": "dep_garre_bt"})
if dropdown:
    options = dropdown.find_all("option")
    
    station_data = []
    
    for option in options:
        station_name = option.text.strip()
        station_id = option.get("value")
        station_data.append({"Station Name": station_name, "Station ID": station_id})
        print(station_name, station_id)  # Print to the console for verification

    df = pd.DataFrame(station_data)
    df.to_csv("train_stations_BT.csv", index=False)
    print("All train stations exported to train_stations_BT.csv")
else:
    print("Dropdown not found.")

#Scrapping Banlieue du Sahel
soup = BeautifulSoup(response.content, "html.parser")
dropdown = soup.find("select", {"id": "dep_garre_bs"})
if dropdown:
    options = dropdown.find_all("option")
    
    station_data = []
    
    for option in options:
        station_name = option.text.strip()
        station_id = option.get("value")
        station_data.append({"Station Name": station_name, "Station ID": station_id})
        print(station_name, station_id)  
    df = pd.DataFrame(station_data)
    df.to_csv("train_stations_BS.csv", index=False)
    print("All train stations exported to train_stations_BS.csv")
else:
    print("Dropdown not found.")