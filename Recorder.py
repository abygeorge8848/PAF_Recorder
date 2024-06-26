import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import math
import json
import urllib3
import threading
from reformat_paf import reformat_paf_activity, write_raw_json_data
from refactored_js import listeners, xpath_js, get_xpath_js


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


recorded_actions = []
paused_time_total= 0
paused_at = None


# Initialize Chrome driver and options
chrome_options = Options()
chrome_options.add_argument("--disable-web-security")  # WARNING: This is unsafe for regular browsing
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--remote-allow-origins=*")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--incognito")
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument('--ignore-certificate-errors')

download_path = "./downloads"  # Update this path
prefs = {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "plugins.plugins_disabled": ["Adobe Flash Player", "Chrome PDF Viewer"]
}
chrome_options.add_experimental_option("prefs", prefs)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
actions = ActionChains(driver)



def set_up_listeners():
    # Injecting JS into the main page
    inject_script_into_page()
    # Handle frame injection
    inject_script_into_frames()


def inject_script_into_frames(is_nested=False):
    original_window = driver.current_window_handle

    frames = driver.find_elements(By.TAG_NAME, 'iframe') + driver.find_elements(By.TAG_NAME, 'frame')
    if frames:
        if not is_nested:
            time.sleep(5)  # Adjust this delay as needed

        for index, frame in enumerate(frames):
            retry_frame_injection(frame, index, is_nested)

    elif not is_nested:
        print("No iframes found on this page.")

    driver.switch_to.window(original_window)


def retry_frame_injection(frame, index, is_nested, attempts=3):
    for attempt in range(attempts):
        try:
            driver.switch_to.frame(frame)
            WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState;") == "complete")
            retry_script_injection(3)
            if not is_nested:
                inject_script_into_frames(is_nested=True)
            break  # Exit the loop if successful
        except StaleElementReferenceException:
            print(f"Stale element reference for frame at index {index}, attempt {attempt + 1}")
            if attempt == attempts - 1:
                raise  # Re-raise exception if all attempts fail
        except TimeoutException:
            print(f"Timeout waiting for frame to load at index {index}, attempt {attempt + 1}")
        except Exception as e:
            print(f"Exception while injecting script into frame at index {index}, attempt {attempt + 1}: {e}")
        finally:
            driver.switch_to.default_content()



def retry_script_injection(attempts):
    for attempt in range(attempts):
        try:
            inject_script_into_page()
            return
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for script injection: {e}")
            time.sleep(1)  # Adjust the sleep time as necessary


def inject_script_into_page():
    try:
        driver.execute_script(listeners)
        print("Script injected successfully into current context.")
    except Exception as e:
        print(f"Error injecting script into current context: {e}")


def monitor_page_load(stop_thread_flag):
    global driver
    old_url = driver.current_url
    while not stop_thread_flag.is_set():
        try:
            time.sleep(0.5) # Adjust the sleep time as necessary
            new_url = driver.current_url
            if new_url != old_url:
                print(f"URL change detected. Old URL: '{old_url}', New URL: '{new_url}'")
                WebDriverWait(driver, 240).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                set_up_listeners()
                old_url = new_url
        except Exception as e:
            print(f"Exception in monitor_page_load: {e}")
            break



stop_thread_flag = threading.Event()


# Loop to continuously check for user inactivity
def start_recording(url):
    global driver, actions, start_time, last_time, stop_thread_flag, init_url
    init_url = url
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    actions = ActionChains(driver)

    setup_environment()
    
    start_time = time.time() * 1000
    last_time = time.time() * 1000

#redirects the browser to the chosen url
def redirect_url_driver(new_url):
    global init_url
    driver.get(new_url)  # Navigate to the new URL
    init_url = new_url  # Update the init_url if necessary
    setup_environment()

#Closes the browser
def close_browser_driver():
    global driver
    try:
        driver.quit()  # Recommended to quit the driver session completely
    except Exception as e:
        print(f"Error closing the browser: {e}")

#Refreshes the browser
def refresh_browser_driver():
    driver.refresh()
    setup_environment()

#Sets up the listeners and environment   
def setup_environment(): 
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    set_up_listeners()
    stop_thread_flag.clear()
    monitor_thread = threading.Thread(target=monitor_page_load, args=(stop_thread_flag,))
    monitor_thread.daemon = True
    monitor_thread.start()


def pause_recording_main():
    global is_paused, paused_at, driver
    is_paused = True
    paused_at = time.time() * 1000
    driver.execute_script("window.isPaused = true;")

def resume_recording_main():
    global is_paused, paused_at, paused_time_total, driver
    if paused_at:
        pause_duration = (time.time() * 1000) - paused_at
        paused_time_total += pause_duration
    is_paused = False
    paused_at = None
    driver.execute_script("window.isPaused = false;")


def create_xpath():
    xpath = driver.execute_async_script(xpath_js)
    return xpath

def create_xpath2():
    xpath = None
    try:
        xpath = driver.execute_async_script(get_xpath_js)
    except:
        print("No element has been clicked! Click on element to get its xpath")
    return xpath


# Modify stop_and_show_records to call GPT-4 script
def stop_and_show_records(activity_name, activity_description, activity_path):

    global driver, last_time, paused_time_total, stop_thread_flag
    if driver:

        combined_events = []
        try:
            final_session_events = driver.execute_script("return window.recordedEvents || [];")
            if final_session_events:
                print(f"\n\n\n Successfully retrieved the final session events : \n{final_session_events}\n\n\n")
            else:
                final_session_events = []


            server_events = driver.execute_script("""
                var request = new XMLHttpRequest();
                request.open('GET', 'http://localhost:9005/retrieve', false);  // false for synchronous
                request.send(null);
                if (request.status === 200) {
                    return request.responseText;
                }
                return '[]';
            """)
            if server_events:
                server_events = json.loads(server_events)
                print(f"\n\n Retrieved the events from the server : \n{server_events} \n\n")
            else:
                server_events = []

            #combined_events = server_events + final_session_events
            combined_events = server_events
            print(f"\n\n The combined events are : {combined_events}\n\n")
        
        except Exception as e:
            print("Exception in stop_and_show_records: ", e)


        recorded_events = combined_events

        print(f"\n\nRecorded events: {recorded_events}\n\n\n")

        last_time = start_time
        prev_event_was_input = False
        prev_event_was_wait = False
        prev_event_was_waitforpageload = False
        combined_input = None
        combined_xpath = None
        dropdown_xpath = None
        dragged_xpath = None 

        event_queue = []
        for event in recorded_events:
            event_type, timestamp, *others = event

            # Print wait only if previous event wasn't input or current event is not input
            if (not prev_event_was_input or event_type != "input") and ((event_type != "WaitForPageLoad" and not prev_event_was_waitforpageload) and not prev_event_was_wait):
                wait_time = abs(math.ceil((timestamp - last_time - paused_time_total) / 1000.0)) * 1000
                paused_time_total=0
                event_queue.append({"event": "wait", "time": wait_time})
                prev_event_was_wait = True
                prev_event_was_waitforpageload == False

            if event_type == "click" or event_type == "dblClick" or event_type == "scroll" or event_type == "hover" or event_type == "highlight" or event_type == "clearinput": 
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                xpath = others[0]
                event_queue.append({"event": event_type, "xpath": xpath})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "dropdownXpath":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                dropdown_xpath = others[0]
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "dropdownText":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                dropdown_text = others[0]
                event_queue.append({"event": "dropdown", "xpath": dropdown_xpath, "selected": dropdown_text})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "dragStart":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                drag_xpath = others[0]
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "drop":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                drop_xpath = others[0]
                event_queue.append({"event": "DragandDrop", "src": drag_xpath, "target": drop_xpath})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "specialKeys":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                xpath = others[0]
                value = others[1]
                event_queue.append({"event": event_type, "xpath": xpath, "value": value})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False
            

            elif event_type == "getText":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                xpath = others[0]
                variable = others[1]
                after = others[2]
                before = others[3]
                event_queue.append({"event": event_type, "xpath": xpath, "variable": variable, "after": after, "before": before})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "variable-value":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                variable_name = others[0]
                variable_value = others[1]
                after = others[2]
                before = others[3]
                event_queue.append({"event": event_type, "name": variable_name, "value": variable_value, "after": after, "before": before})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "redirect-url":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                redirect_url = others[0]
                event_queue.append({"event": event_type, "url": redirect_url})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "refresh-browser" or event_type == "close-browser":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                event_queue.append({"event": event_type})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "validation-exists" or event_type == "validation-not-exists":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                xpath = others[0]
                validation_name = others[1]
                pass_msg = others[2]
                fail_msg = others[3]
                after = others[4]
                before = others[5]
                if_condition = others[6]
                if_else_condition = others[7]
                event_queue.append({"event": event_type, "validation_name": validation_name, "xpath": xpath, "pass_msg": pass_msg, "fail_msg": fail_msg, "after": after, "before": before, "if_condition": if_condition, "if_else_condition": if_else_condition})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type in ["validation-equals", "validation-not-equals", "validation-num-equals", "validation-num-not-equals", "validation-num-le", "validation-num-ge", "validation-contains", "validation-starts-with", "validation-ends-with"]:
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                validation_name = others[0]
                variable1 = others[1]
                variable2 = others[2]
                pass_msg = others[3]
                fail_msg = others[4]
                after = others[5]
                before = others[6]
                if_condition = others[7]
                event_queue.append({"event": event_type, "validation_name": validation_name, "variable1": variable1, "variable2": variable2, "pass_msg": pass_msg, "fail_msg": fail_msg, "after": after, "before": before, "if_condition": if_condition, "if_else_condition": if_else_condition})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "input":
                xpath = others[0]
                char = others[1]
                if prev_event_was_input and xpath == combined_xpath:
                    combined_input += char
                else:
                    if combined_input:
                        event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = char
                    combined_xpath = xpath
                prev_event_was_input = True
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "variable-expression":
                instruction = others[1]
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                event_queue.append({"event": event_type, "instruction": instruction})
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False


            elif event_type == "WaitForPageLoad" and prev_event_was_waitforpageload == False:
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                prev_event_was_waitforpageload = True
                event_queue.append({"event": "WaitForPageLoad"})
                prev_event_was_wait = False
            
            elif event_type == "end-if" or event_type == "end-if-then" or event_type == "end-else":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                event_queue.append({"event": event_type})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False
            
            elif event_type == "frame":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                id = others[0]
                event_queue.append({"event": event_type, "id": id})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False
            
            elif event_type == "start-loop":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                startIndex = others[0]
                lastIndex = others[1]
                increment = others[2]
                counterVar = others[3]
                event_queue.append({"event": event_type, "startIndex": startIndex, "lastIndex": lastIndex, "increment": increment, "counterVar": counterVar})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "end-loop":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                event_queue.append({"event": event_type})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "custom-step":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                custom_step = others[0]
                event_queue.append({"event": event_type, "custom_step": custom_step})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "excel-read" or event_type == "excel-write" or event_type == "excel-search":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                row = others[0]
                col = others[1]
                sheet = others[2]
                path = others[3]
                if event_type == "excel-read":
                    variable = others[4]
                    event_queue.append({"event": event_type, "row": row, "col": col, "sheet": sheet, "path": path, "variable": variable})
                elif event_type == "excel-write":
                    value = others[4]
                    event_queue.append({"event": event_type, "row": row, "col": col, "sheet": sheet, "path": path, "value": value})
                elif event_type == "excel-search":
                    text = others[4]
                    variable = others[5]
                    event_queue.append({"event": event_type, "row": row, "col": col, "sheet": sheet, "path": path, "variable": variable, "text": text})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False

            elif event_type == "alert-accept" or event_type == "alert-cancel" or event_type == "alert-getText" or event_type == "alert-input" or event_type == "alert-authenticate":
                if combined_input:
                    event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})
                    combined_input = None
                    combined_xpath = None
                if event_type == "alert-accept" or event_type == "alert-cancel":
                    event_queue.append({"event": event_type})
                elif event_type == "alert-getText":
                    keyName = others[0]
                    event_queue.append({"event": event_type, "keyName": keyName})
                elif event_type == "alert-input":
                    value = others[0]
                    event_queue.append({"event": event_type, "value": value})
                elif event_type == "alert-authenticate":
                    user = others[0]
                    pwd = others[1]
                    event_queue.append({"event": event_type, "user": user, "pwd": pwd})
                prev_event_was_input = False 
                prev_event_was_wait = False
                prev_event_was_waitforpageload == False
    

            last_time = timestamp
        # Print any remaining combined input after loop ends
        if combined_input:
            event_queue.append({"event": "input", "xpath": combined_xpath, "value": combined_input})

        stop_thread_flag.set()
        #driver.quit()


        def process_wait_in_queue(event_queue):
            i = 0
            while i < len(event_queue):
                if event_queue[i]["event"] == "wait":
                    total_time = event_queue[i]["time"]
                    if total_time == 0:
                        event_queue.pop(i)
                        continue

                    j = i+1
                    while j < len(event_queue) and event_queue[j]["event"] == "wait":
                        total_time += event_queue[j]["time"]
                        j += 1
                    
                    event_queue[i]["time"] = total_time
                    for _ in range(j - i -1):
                        event_queue.pop(i+1)

                i += 1
            
            return event_queue
        
        event_queue = process_wait_in_queue(event_queue)

        i = 0
        while i < len(event_queue) - 1: 
            current_event = event_queue[i]["event"]
            next_event = event_queue[i + 1]["event"]
            if current_event == "scroll" and next_event == "scroll":
                event_queue.pop(i)
            else:
                i += 1
#
        print(f"\n\n The event_queue for execution is : {event_queue}\n\n")

        completed_code= ""
        
        PAF_ACTIVITY = reformat_paf_activity(event_queue, activity_name, activity_description)
        write_raw_json_data(activity_name, activity_description, activity_path, event_queue)
        completed_code = PAF_ACTIVITY["PAF_SCRIPT"]
        

        with open(activity_path, 'r') as file:
            file_content = file.read()

        # Check if <activities> tag is present
        if "<activities>" in file_content and "</activities>" in file_content:
            # Find the position just after <activities> tag
            insert_position = file_content.find('<activities>') + len('<activities>') + 1  # +1 for the newline after <activities>
            # Insert an empty line and then the completed_code
            modified_content = file_content[:insert_position] + "\n" + completed_code + "\n" + file_content[insert_position:]
        else:
            # If <activities> tag is not present, format the completed_code as before
            completed_code = "<activities>\n\n" + completed_code + "\n\n</activities>"
            modified_content = completed_code

        # Write the modified content back to the file
        with open(activity_path, 'w') as file:
            file.write(modified_content)

        
    return 1
     








