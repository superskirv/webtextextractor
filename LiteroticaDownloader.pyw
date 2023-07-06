import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import threading
import time
import requests
import re
# import os

file_version = '2023.07.05.B'

#################################################
##           Reqexp Formulas Setup
#################################################
regexp_title =      r"<h1 class=\"j_bm headline j_eQ\">(.*?)</h1>"
regexp_title_alt =  r"<h1 class=\"j_bm headline j_eQ \">(.*?)</h1>"
regexp_series_page = r"\"https://www.literotica.com/series/se/(.*?)\" class=\"bn_av\""
regexp_series_pages_bulk = r"<ul class=\"series__works\">(.*?)</ul>"

regexp_author =     r"class=\"y_eU \" title=\"(.*?)\">" # class="y_eU" title="Ran_dom_Guy">
regexp_author_alt = r"class=\"y_eU\" title=\"(.*?)\">" # class="y_eR" title="Ran_dom_Guy">

regexp_tag_bulk = r'<div class=\"bn_Q bn_ar\">(.*?)</div>'
regexp_tag_single =         r" class=\"av_as av_r\">(.*?)</a>"
#regexp_tag_single_alt =    r" class=\"av_as \"(.*?)</a>" #unused.
regexp_story_page = r"<div class=\"panel article aa_eQ\">(.*?)</div>"
regexp_next_page = r"title=\"Next Page\" href=\"(.*?)\"><i class=\""

global message_logs
message_logs = {}
#################################################
##           Thread Actions Setup
#################################################
class DownloadThread(threading.Thread):
    semaphore = threading.Semaphore(1)  # Set maximum number of allowed threads

    def __init__(self, que_id, item_id, queued_actions, message_logs):
        threading.Thread.__init__(self)
        self.que_id = que_id
        self.item_id = item_id
        self.queued_actions = queued_actions
        self.stopped = False
        self.message_logs = message_logs

    def set_status(self, status="Error", msg="No Msg", delay=0.5):
        if msg == "No Msg" and status != "Error":
            msg = status
            status = "Old Format"

        self.message_logs[self.item_id]['que_table'] = (status, *self.message_logs[self.item_id]['que_table'][1:])
        self.queued_actions.set(self.que_id, column='action_status', value=status)
        self.queued_actions.update()
        self.message_logs[self.item_id]['msg_table'].append((status, msg))
        time.sleep(delay)

    def get_html(self, url, max_retries=2, retry_delay=5):
        self.set_status("Downloading", "Start of " + url)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        retries = 0

        while retries < max_retries:
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    raw_html = response.text
                    self.set_status("Download","Success!")
                    return(raw_html)
                else:
                    self.set_status(self.item_id, "Error","Network No Status code")
            except requests.exceptions.RequestException as e:
                self.set_status("Error","Network Unknown")
            retries += 1
            if retries < max_retries:
                self.set_status(self.item_id, "Error","Retrying in... "+str(retry_delay))
                time.sleep(retry_delay)
        self.set_status("Error","Max number of retries reached.")
        return("0")

    def get_pattern(self, html, pattern):
        if html:
            matches = re.findall(pattern, html, re.DOTALL)
            if matches:
                extracted_text = matches[0].strip()
                return(extracted_text)
        return("0")

    def process_request(self, url):
        options = message_logs[self.item_id]['que_table'][2]
        raw_html = self.get_html(url)

        req_start = url
        req_title = ""
        req_filename = title = url.rsplit("/")[4]
        self.set_status("Filename", req_filename,0)
        req_author = ""
        req_series = ""
        req_links = []
        req_tags = []

        whole_file = ""
        whole_story = ""

        if raw_html != "0":
            if options.get("series", True) is not False:
                series_page = self.get_pattern(raw_html, regexp_series_page)
                self.set_status("Info","Found Series Link: " + series_page,1)
                if series_page != "0":
                    series_html = self.get_html("https://www.literotica.com/series/se/" + series_page)
                    if series_html != "0":
                        series_temp = self.get_pattern(series_html, regexp_series_pages_bulk)
                        if series_temp != "0":
                            req_links = self.get_all_links(series_temp)
                            for link in req_links:
                                self.set_status("Found Link",link,0)
                        else:
                            self.set_status("Failed","No Series Links",1)
                    else:
                        self.set_status("Failed","No Series Pages",1)
                else:
                    self.set_status("Failed","Not a Series? Falling back to single story mode.",1)
                    req_links = [url]
            else:
                #just look up the one story, by only having 1 link to look up.
                req_links = [url]

        for link in req_links:
            raw_html = self.get_html(link)

            req_title = self.get_pattern(raw_html, regexp_title)
            if req_title == "0":
                req_title = self.get_pattern(raw_html, regexp_title_alt)
            req_title = self.remove_formatting(req_title) #Fixes some formatting.
            self.set_status("Found Title", req_title,0)

            #get author
            req_author = self.get_pattern(raw_html, regexp_author)
            if req_author == "0":
                req_author = self.get_pattern(raw_html, regexp_author_alt)
            self.set_status("Found Author", req_author)
            #get story tags
            req_tags = self.get_all_tags(raw_html)
            #get story page
            whole_page = self.get_pattern(raw_html, regexp_story_page)
            whole_page_formatted = self.remove_formatting(whole_page)

            req_tags_string = ", ".join(req_tags)
            req_tags_string = req_tags_string[2:]
            story_header = link + "\n\n" + req_title + "\n" + req_author + "\n------------------------------\nTags: " + req_tags_string  + "\n------------------------------\n"
            whole_loop = whole_page_formatted

            req_nextpage = self.get_pattern(raw_html, regexp_next_page)
            while req_nextpage != "0":
                req_nextpage_link = "https://www.literotica.com" + req_nextpage
                self.set_status("Found Next Page","Link: " + req_nextpage_link,0)

                raw_html = self.get_html(req_nextpage_link,1)
                whole_page = self.get_pattern(raw_html, regexp_story_page)
                whole_page_formatted = self.remove_formatting(whole_page)

                whole_loop = whole_loop + whole_page_formatted

                req_nextpage = self.get_pattern(raw_html, regexp_next_page)

            whole_story = story_header + whole_loop + "\n------------------------------\n   The End of \n        " + req_title + "\n\n------------------------------\n\n"
            whole_file = whole_file + whole_story
        if len(whole_file) <= 200:
            self.set_status("Small File","Something likely went wrong.",0)
        else:
            #Save the file.
            self.save_text(req_filename,whole_file)

    def save_text(self, filename, story):
        options = message_logs[self.item_id]['que_table'][2]
        filetype = options.get("save_type", ".txt")
        output_file = filename + filetype
        self.set_status("Saving File", output_file,0)
        with open(output_file, 'w', encoding='utf-8') as file_write:
            file_write.write(story)
        file_write.close()

    def get_all_tags(self, html):
        tags = []
        story_tags_bulk = self.get_pattern(html, regexp_tag_bulk)
        story_tags_temp = re.findall(regexp_tag_single, story_tags_bulk)
        if story_tags_bulk != "0":
            for tag in story_tags_temp:
                if tag not in tags:
                    tags.append(tag)
            tags = sorted(tags)
            self.set_status("Found Tags","Tags: " + " ".join(tags))
        return(tags)

    def get_all_links(self, html):
        match = "https://www.literotica.com/s/"
        black_list = ["comment","feedback"]
        found_links = []

        if html != "0":
            http_links = re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", html)
            for link in http_links:
                if link.startswith(match):
                    if link.rsplit("/", 2)[-2] == "s":  # matches URL previous directory, makes sure this is a story and not feedback/comment/etc.
                        link_story = link.rsplit("/", 1)[-1]
                        if link_story not in found_links and not any(keyword in link_story for keyword in black_list):
                            found_links.append(match + link_story)
        return found_links

    def remove_formatting(self, html):
        html = html.replace("<p align=\"center\">", "\n")
        html = html.replace("<p>", "\n")
        html = html.replace("</p>", "\n")
        html = html.replace("<br>", "\n")
        html = html.replace("<div class=\"aa_ht\">", "")
        html = html.replace("&#x27;", "\'")
        html = html.replace("<div class=\"aa_ht \">", "")
        html = html.replace("<div>", "")
        html = html.replace("</div>", "")
        html = html.replace("<strong>", "")
        html = html.replace("</strong>", "")
        html = html.replace("<b>", "")
        html = html.replace("</b>", "")
        html = html.replace("<i>", "")
        html = html.replace("</i>", "")
        html = html.replace("<em>", "")
        html = html.replace("</em>", "")
        return(html)

    def run(self):
        with DownloadThread.semaphore:  # Acquire the semaphore
            self.set_status("Processing","In Progress...")
            url = message_logs[self.item_id]['que_table'][1]
            options = message_logs[self.item_id]['que_table'][2]
            self.process_request(url)
            self.queued_actions.event_generate('<<TreeviewUpdate>>')
            self.set_status("Completed","Thank you.")

    def stop(self):
        self.stopped = True

def on_closing():
    clear_all()
    for thread in threads:
        thread.stop()
    window.destroy()

def que_delete_selected():
    selection = queued_actions.selection()
    for item in selection:
        queued_actions.delete(item)

def que_move_item_up():
    selection = queued_actions.selection()
    for item in selection:
        queued_actions.move(item, queued_actions.parent(item), queued_actions.index(item) - 1)

def que_move_item_down():
    selection = queued_actions.selection()[::-1]
    for item in selection:
        queued_actions.move(item, queued_actions.parent(item), queued_actions.index(item) + 1)

def que_clear_all():
    queued_actions.delete(*queued_actions.get_children())

def que_action():
    que_url = action_url.get()
    que_options = ''

    que_options = {'job_type': 'download','series': action_get_series.get(), 'save_type': '.txt'}

    entry_name = "Job " + str(len(message_logs) + 1).zfill(4)
    message_logs[entry_name] = {'que_table': ("Waiting", que_url, que_options), 'msg_table': [("Waiting","Entry added to list, waiting for que.")]}
    que_id = queued_actions.insert('', tk.END, text=entry_name, values=message_logs[entry_name]['que_table'])
    queued_actions.set(que_id, column='action_status', value="Message")

    msg_table_data = message_logs[entry_name]['msg_table']
    message_log_grid.delete(*message_log_grid.get_children())
    for item in msg_table_data:
        message_log_grid.insert('', tk.END, values=item)

    message_logs.update()

    thread = DownloadThread(que_id, entry_name, queued_actions, message_logs)
    threads.append(thread)
    thread.start()

#################################################
##           GUI Actions Setup
#################################################
def find_txt_files(directory):
    txt_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                txt_files.append(os.path.join(root, file))
    return txt_files

def display_msg_log(event):
    selected_item = queued_actions.focus()

    if selected_item:
        selected_entry = queued_actions.item(selected_item)['text']
        msg_table_data = message_logs[selected_entry]['msg_table']
        message_log_grid.delete(*message_log_grid.get_children())
        for item in msg_table_data:
            message_log_grid.insert('', tk.END, values=item)

def open_file():
    root = tk()
    root.withdraw()

    directory = filedialog.askdirectory(title='Select Directory')
    if directory:
        txt_files = find_txt_files(directory)
        que_update_job(directory, txt_files) #Runs job to update existing stories.
    else:
        print("No directory selected.")

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt")
    if file_path:
        # Save the file
        print("Saved file:", file_path)

def exit_app():
    window.quit()

#################################################
##           Create the main GUI
#################################################
window = tk.Tk()
window.title("Literotica Downloader")
window.geometry("800x600")

#################################################
##           Frame Setup
#################################################
frame_main = tk.Frame(window, width=800) #, borderwidth=2, relief="groove"
frame_main.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=0, pady=0)
#Action Buttons and Controls
frame_action = tk.Frame(frame_main, width=800, height=50, borderwidth=2, relief="groove")
frame_action.pack(side=tk.TOP, fill=tk.BOTH, padx=0, pady=0)
#Que Tree View
frame_que = tk.Frame(frame_main, width=800, height=100, borderwidth=2, relief="groove")
frame_que.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=0, pady=0)
#Status Messages
frame_message_log = tk.Frame(window, width=800, height=650)
frame_message_log.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=0, pady=0)

#################################################
##           Actions Setup
#################################################
action_lbl_url = tk.Label(frame_action, text="URL: ")
action_lbl_url.pack(side=tk.LEFT)
action_url = tk.Entry(frame_action, width=100)
action_url.pack(side=tk.LEFT, fill=tk.X, expand=True)

action_get_series = tk.BooleanVar()
action_get_series_chkbox = ttk.Checkbutton(frame_action, text='Get Whole Series', variable=action_get_series)
action_get_series_chkbox.pack(side=tk.LEFT)

action_add_action = tk.Button(frame_action, text="Add", command=que_action)
action_add_action.pack(side=tk.LEFT)
#################################################
##           Queued List
#################################################
frame_que.columnconfigure(0, weight=1)
frame_que.columnconfigure(1, weight=1)
frame_que.columnconfigure(2, weight=1)
frame_que.columnconfigure(3, weight=1)
frame_que.rowconfigure(1, weight=1)

global queued_actions
queued_actions = ttk.Treeview(frame_que, columns=("action_status", "action_url", "action_options"), show="headings")

queued_actions.heading("action_status", text="Status")
queued_actions.heading("action_url", text="URL")
queued_actions.heading("action_options", text="Options")

queued_actions.column("action_status", width=70)
queued_actions.column("action_url", width=300)
queued_actions.column("action_options", width=200)

queued_actions.grid(row=1, column=0, columnspan=4, sticky="nsew")

queued_actions.bind('<<TreeviewSelect>>', display_msg_log)

#################################################
##           Message Logs Set up
#################################################
frame_message_log.rowconfigure(0, weight=1)
frame_message_log.columnconfigure(0, weight=2)

message_log_grid = ttk.Treeview(frame_message_log, columns=("msg_type", "msg_text"), show="headings")
message_log_grid.heading("msg_type", text="Type")
message_log_grid.heading("msg_text", text="Message")

message_log_grid.column("msg_type", width=50)
message_log_grid.column("msg_text", width=600)

message_log_grid.grid(row=0, column=0, sticky="nsew")

threads = []

# Start the GUI event loop
window.mainloop()
