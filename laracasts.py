'''
    Author: Md. Nazmus Sakib
    Go wild with this script
'''
import requests
import os
import urllib.parse as urlparse
from bs4 import BeautifulSoup

'''
    Hell yeah !! Download that shit
    :url episode url
    :session_request the_session 
    :folder folder to save
'''
def download_file(url, session_request, folder):
    r = session_request.get(url, stream=True)
    url = r.url
    parsed = urlparse.urlparse(url)
    local_filename = urlparse.parse_qs(parsed.query)['filename'][0]
    index = 1
    save_path = os.path.join(folder, local_filename)

    while os.path.isfile(save_path):
        base_filename, file_extension = os.path.splitext(save_path)
        base_filename += str(index)
        save_path = base_filename + file_extension
        index += 1

    print("Downloading ...: " + local_filename)

    with open(save_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

    return local_filename

# Take all inputs
userEmail = input("Login Email: ")
userPassword = input("Password: ")
course_page = input("Full URL: ")


login_url = "https://laracasts.com/login"
session_requests = requests.session()
page = session_requests.get(login_url)
soup = BeautifulSoup(page.content, "lxml")

# get the token for battle CSRF protection
token = soup.find('input', {'name':'_token'})['value']

# Load the gun
payload = {
    "email": userEmail,
    "password": userPassword,
    "_token": token
}

# Send the nuke
result = session_requests.post(
    "https://laracasts.com/sessions",
    data=payload,
    headers=dict(referer=login_url)
)

# Confirmed login
print("logged in : " + result.url)

# Get all episodes
course = session_requests.get(course_page)
soup2 = BeautifulSoup(course.content, "lxml")
course_title = soup2.find("h1", {
    "class": "series-title"
})
course_title = course_title.text.strip().replace(" ", "_")
print("Course title: " + course_title)

# Create folder to store videos
if not os.path.exists(course_title):
    os.makedirs(course_title)
    print("Directory created: " + course_title)

episodes = soup2.find_all("li", {
    "class": "episode-list-item"
})

print("Downloading " + str(len(episodes)) + " episodes .......")

# Download each episodes
i = 1
for episode in episodes:
    link = episode.find("a", {
        "class": "position"
    })

    url = "https://laracasts.com" + link.get("href")
    single_html = session_requests.get(url)
    soup3 = BeautifulSoup(single_html.content, "lxml")
    download_link = soup3.find("a", {
        "class": "for-download"
    })
    # print(download_link.get("href"))
    url = "https://laracasts.com" + download_link.get("href")
    filename = download_file(url, session_requests, course_title)
    print(str(i) + ". " + filename + "......Downloaded ")
    i += 1

# Download finished .. Now zip the folder
http_dir = "/var/www/html/" + course_title + ".zip"
os.system("zip -r " + http_dir + " " + course_title)
print("=====> " + course_title + " is Downloaded in " + http_dir)

