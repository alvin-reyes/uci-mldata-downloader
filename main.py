import requests
from bs4 import BeautifulSoup

import os
import zipfile

base_url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/'
data_folder = 'UCI_ML_data'
max_size = 3 * 1024 * 1024 * 1024  # 3 GB

# Create a directory to save the data
if not os.path.exists(data_folder):
    os.makedirs(data_folder)


# Function to download files from a given link and compress them into ZIP files of size 3 GB
def download_files(url, folder, zip_num=1, zip_size=0):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        if href.endswith('/'):
            # Sub link found, download all files from the sub link
            sub_url = url + href
            sub_folder = folder + os.path.join(folder, href[:-1])
            if not os.path.exists(sub_folder):
                os.makedirs(sub_folder)
            zip_num, zip_size = download_files(sub_url, sub_folder, zip_num, zip_size)
        else:
            # Link found, download the file
            filename = os.path.join(folder, os.path.basename(href))
            if not os.path.exists(filename):
                print(f"Downloading {href}...")
                data = requests.get(url + href).content
                with open(filename, 'wb') as f:
                    f.write(data)
                # Compress files into a ZIP file of size 3 GB
                zip_size += os.path.getsize(filename)
                if zip_size > max_size:
                    zip_num += 1
                    zip_size = os.path.getsize(filename)
                zip_filename = os.path.join(folder, f"{zip_num}.zip")
                with zipfile.ZipFile(zip_filename, mode='a', compression=zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(filename, arcname=os.path.basename(filename))
                    os.remove(filename)
    return zip_num, zip_size


# Download all files from the base URL and its sub links and compress them into ZIP files
download_files(base_url, "UCI_ML_data")
