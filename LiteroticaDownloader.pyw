import os
import re
import time
import requests
import tkinter as tk
from tkinter import ttk
from collections import OrderedDict

url_downloaded = []
file_version = '2023.06.04.A'

################################################################################
################################################################################
def download_html(url, max_retries=2, retry_delay=5):
    if url in url_downloaded:
        #send_status("\nNetwork: Downloaded Link Before: " + url)
        return(0)
    else:
        url_downloaded.append(url)
    send_status("\nDownloading: " + url.rsplit("/", 1)[-1])
    retries = 0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    while retries < max_retries:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                raw_html = response.text
                return(raw_html)  # Exit the function after successful extraction
            else:
                send_status("\nError: Failed to retrieve the web page. Status code " + str(response.status_code))
        except requests.exceptions.RequestException as e:
            send_status("\nError: An error occurred during the web page lookup")

        retries += 1
        if retries < max_retries:
            message = "\nError: " + str(retries) + "Retrying in" + str(retry_delay) + "second(s)..."
            send_status(message)
            time.sleep(retry_delay)

    send_status("\nError: Max number of retries reached. Unable to retrieve data.")
    return(0)

def text_search_extract(raw_html, pattern):
    if raw_html:
        matches = re.findall(pattern, raw_html, re.DOTALL)
        if matches:
            extracted_text = matches[0].strip()
            return(extracted_text)  # Exit the function after successful extraction
    return(0)

#Writes text to file, creates new file if none exists, otherwise appends
def write_to_file(output_file, combined_text):
    if not output_file.endswith(".txt"):
        output_file = output_file + ".txt"

    send_status("\nSaving: " + output_file)
    if os.path.exists(output_file):
        with open(output_file, "a", encoding='utf-8') as filea:
             filea.write(combined_text)
        filea.close()
    else:
        with open(output_file, 'w', encoding='utf-8') as filew:
            filew.write(combined_text)
        filew.close()

################################################################################
################################################################################

#Removes extra html formating. Im sure there are more that exist or an easier way.
def format_body(TextBody):
    #Removes html formating
    TextBody = TextBody.replace("<p align=\"center\">", "\n")
    TextBody = TextBody.replace("<p>", "\n")
    TextBody = TextBody.replace("</p>", "\n")
    TextBody = TextBody.replace("<br>", "\n")
    TextBody = TextBody.replace("<div class=\"aa_ht\">", "")
    TextBody = TextBody.replace("&#x27;", "\'")
    TextBody = TextBody.replace("<div>", "")
    TextBody = TextBody.replace("</div>", "")
    TextBody = TextBody.replace("<strong>", "")
    TextBody = TextBody.replace("</strong>", "")
    TextBody = TextBody.replace("<b>", "")
    TextBody = TextBody.replace("</b>", "")
    TextBody = TextBody.replace("<i>", "")
    TextBody = TextBody.replace("</i>", "")
    TextBody = TextBody.replace("<em>", "")
    TextBody = TextBody.replace("</em>", "")
    return(TextBody)

def get_story(url):
    raw_html = download_html(url)
    story_series = ""
    story_title = ""

    if raw_html:
        #Gets all the parts of the story and formats it. Then gets the next part if its multipage.
        story_title = text_search_extract(raw_html, r"<h1 class=\"j_bm headline j_eQ\">(.*?)</h1>")
        story_title = story_title.replace("&#x27;", "\'")
        story_author = text_search_extract(raw_html, r"class=\"y_eU\" title=\"(.*?)\">")

        story_body = text_search_extract(raw_html, r"<div class=\"panel article aa_eQ\">(.*?)</div>")
        story_nextpage = text_search_extract(raw_html, r"title=\"Next Page\" href=\"(.*?)\"><i class=\"")

        #check for series
        story_series = text_search_extract(raw_html, r"https://www.literotica.com/series/se/(.*?)\"")

        story_page = format_body(story_body)
        story_header = url + "\n\n" + story_title + "\n" + story_author + "\n------------------------------\n"

        #puts story together
        full_story = story_header + story_page

        url_page = 1
        if story_nextpage:
            match = re.search(r"\d+$", story_nextpage)
        else:
            match = 0;
        while(match):
            send_status(".")
            url_page = url_page + 1
            if url_page >= 25:
                send_status("\nError: Found more than 25 Pages? Is that true?")
                break

            if(int(match.group()) == url_page):
                JustPageURL = story_nextpage.split("?", 1)
                NextPageURL =  url + "?" + ''.join(JustPageURL[1])

                raw_html = download_html(NextPageURL)
                story_body = text_search_extract(raw_html, r"<div class=\"panel article aa_eQ\">(.*?)</div>")
                story_nextpage = text_search_extract(raw_html, r"title=\"Next Page\" href=\"(.*?)\"><i class=\"")
                story_page = format_body(story_body)
                full_story = full_story + story_page

                #check for series
                #story_series = text_search_extract(raw_html, r".com/series/se/(.*?)\"")
            if not story_nextpage:
                #check for series
                story_series = text_search_extract(raw_html, r".com/series/se/(.*?)\"")
                #Find Tags: class="av_as ">(.*?)</a>
                #Find Series URL: https://www.literotica.com/series/se/(.*?)\"
                break

            match = re.search(r"\d+$", story_nextpage)
    else:
        send_status("\nError: Continuing to next item.")
        return(0)

    if story_series:
        story_series_url = "https://www.literotica.com/series/se/" + story_series

        raw_html = download_html(story_series_url)
        if(raw_html != 0):
            story_series_html = text_search_extract(raw_html, r"TABLE OF CONTENTS(.*?)</li></ul></div></div></div")
            if story_series_html:
                http_links = re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", story_series_html)

                for link in http_links:
                    link_title = link.rsplit("/", 1)[-1]
                    if link_title not in list_right.get(0, tk.END):
                        list_right.insert(tk.END, link_title)
    full_story = full_story + "\n------------------------------\n   The End of \n        " + story_title + "\n\n------------------------------\n\n"
    return(full_story)

def process_url_list(list):
    send_status("\nNote: Downloading List.")

    title = ""
    url_downloaded.clear()

    for i in range(list.size()):
        current_url = list.get(i)
        story = get_story(current_url)
        if(story != 0):
            #send_status("\nCompleted Story URL..." + str(i + 1))
            #Sets the file name to the url story title(prevents overwriting)
            if(title == ""):
                #Gets text after the last foward slash '/'
                title = current_url.rsplit("/", 1)[-1]
            write_to_file(title, story)

################################################################################
################################################################################

def send_status(status_text):
    status_box.config(state=tk.NORMAL)
    status_box.update_idletasks()
    status_box.insert(tk.END, status_text)
    status_box.see(tk.END)
    status_box.config(state=tk.DISABLED)

def button_add_item():
    menu_left_add()

def button_delete_item():
    menu_left_delete()

def handle_button3():
    send_status("\nButton 3 clicked!")

def handle_button4():
    send_status("\nButton 4 clicked!")

def button_clear_status():
    clear_status_text()

def button_download(list):
    process_url_list(list)

def menu_right_message():
    selected_index = list_right.get(tk.ACTIVE)
    send_status("\nSomething Right: " + selected_index)

def menu_right_delete():
    selection = list_right.curselection()
    if selection:
        selected_index = list_right.get(tk.ACTIVE)
        index = selection[0]
        list_right.delete(index)

def menu_right_move():
    selection = list_right.curselection()
    if selection:
        selected_index = list_right.get(tk.ACTIVE)
        list_left.insert(tk.END, "https://www.literotica.com/s/" + selected_index)

def menu_right_clear():
    list_right.delete(0, tk.END)

def menu_left_message():
    selected_index = list_left.get(tk.ACTIVE)
    send_status("\nSomething Left: " + selected_index)

def menu_left_delete():
    selection = list_left.curselection()
    if selection:
        selected_index = list_left.get(tk.ACTIVE)
        index = selection[0]
        list_left.delete(index)

def menu_left_add():
    # Create a new window for the text input
    input_window = tk.Toplevel(window)
    input_window.title("Enter Text")

    # Create an entry widget for text input
    entry = tk.Entry(input_window, width=100)
    entry.pack(padx=0, pady=0)

    def save_text():
        text = entry.get()
        if text:
            list_left.insert(tk.END, text)
            input_window.destroy()
        else:
            input_window.destroy()

    # Create a save button to add the text to the list
    save_button = tk.Button(input_window, text="Add Item", command=save_text)
    save_button.pack(pady=5)

def menu_left_clear():
    list_left.delete(0, tk.END)

def show_menu_left(event):
    menu_left.tk_popup(event.x_root, event.y_root)

def key_left_delete(event):
    menu_left_delete()

def show_menu_right(event):
    menu_right.tk_popup(event.x_root, event.y_root)

def key_right_delete(event):
    menu_right_delete()

def clear_status_text():
    status_box.config(state=tk.NORMAL)
    status_box.delete("1.0", tk.END)
    status_box.config(state=tk.DISABLED)

################################################################################
################################################################################

################################################################################
################################################################################
# Create the GUI window
window = tk.Tk()
window.title("Main Menu")
window.geometry("800x600")

# Create a frame to hold the buttons
frame_button = tk.Frame(window)
frame_button.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
# Create a frame to hold the Get URL List
frame_list_left = tk.Frame(window)
frame_list_left.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
# Create a frame to hold the Get URL List
frame_list_right = tk.Frame(window)
frame_list_right.pack(side=tk.RIGHT, fill=tk.Y, padx=0, pady=0)
# Create a frame to Status box and Scrollbar
frame_status = tk.Frame(window)
frame_status.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=0, pady=0)

frame_status_scrollbar = tk.Frame(frame_status)
frame_status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=0, pady=0)

# Create the list on the left
list_left = tk.Listbox(frame_list_left, width=30)
list_left.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
#list_left.insert(tk.END, "Some URL")

# Add a horizontal scrollbar to the left list box
list_left_scrollbar = ttk.Scrollbar(frame_list_left, orient=tk.HORIZONTAL, command=list_left.xview)
list_left_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
list_left.config(xscrollcommand=list_left_scrollbar.set)

# Create the list on the right
list_right = tk.Listbox(frame_list_right, width=40)
list_right.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
#list_right.insert(tk.END, "Some story name")

# Add a horizontal scrollbar to the right list box
list_right_scrollbar = ttk.Scrollbar(frame_list_right, orient=tk.HORIZONTAL, command=list_right.xview)
list_right_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
list_right.config(xscrollcommand=list_right_scrollbar.set)

# Create buttons and assign actions
button_add_item = ttk.Button(frame_button, text="Add Item", command=button_add_item)
button_add_item.pack(side=tk.LEFT, padx=5)

button2 = ttk.Button(frame_button, text="Delete Item", command=button_delete_item)
button2.pack(side=tk.LEFT, padx=5)

#button3 = ttk.Button(frame_button, text="Button 3", command=handle_button3)
#button3.pack(side=tk.LEFT, padx=5)

#button4 = ttk.Button(frame_button, text="Button 4", command=handle_button4)
#button4.pack(side=tk.LEFT, padx=5)

button5 = ttk.Button(frame_button, text="Clear Status Log", command=button_clear_status)
button5.pack(side=tk.LEFT, padx=5)

button6 = ttk.Button(frame_button, text="Download", command=lambda: button_download(list_left))
button6.pack(side=tk.LEFT, padx=5)

# Create the status box as a scrolled text widget
status_box = tk.Text(frame_status)
status_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
status_box.config(state=tk.DISABLED)

# Add a vertical scrollbar to the status box
status_scrollbar = ttk.Scrollbar(frame_status_scrollbar, orient=tk.VERTICAL, command=status_box.yview)
status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=True)
status_box.config(yscrollcommand=status_scrollbar.set)

# Create a right-click menu for left list
menu_left = tk.Menu(window, tearoff=0)
menu_left.add_command(label="Do Something", command=menu_left_message)
menu_left.add_command(label="Add Item", command=menu_left_add)
menu_left.add_command(label="Delete Item", command=menu_left_delete)
menu_left.add_command(label="Clear List", command=menu_left_clear)

# Create a right-click menu for right list
menu_right = tk.Menu(window, tearoff=0)
menu_right.add_command(label="Do Something", command=menu_right_message)
menu_right.add_command(label="Add to List", command=menu_right_move)
menu_right.add_command(label="Delete Item", command=menu_right_delete)
menu_right.add_command(label="Clear List", command=menu_right_clear)

# Bind the right-click event to the listbox
list_left.bind("<Button-3>", show_menu_left)
list_left.bind("<Delete>", key_left_delete)

list_right.bind("<Button-3>", show_menu_right)
list_right.bind("<Delete>", key_left_delete)
#list_right.bind("<Double-Button-1>", menu_right_move)

# Start the GUI event loop
window.mainloop()
