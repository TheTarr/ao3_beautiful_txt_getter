import requests
from bs4 import BeautifulSoup
import logging
import tkinter as tk
import sys

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR)

def process_pre_page(soup):
    # Find the <a> tag with "Proceed" text
    proceed_link = soup.find('a', text='Proceed')
    
    if proceed_link:
        # Get the URL from the "href" attribute of the <a> tag
        proceed_url = proceed_link['href']
        
        # Send a request to the proceed URL and create a new BeautifulSoup object
        response = requests.get(proceed_url)
        new_soup = BeautifulSoup(response.content, 'html.parser')
        
        return new_soup
    return None

def analyzer(url):
    if "chapters" not in url:
        is_single = True
    else:
        is_single = False
    return is_single

def convert_title(input_string):
    if ":" in input_string:
        # Split the input string into chapter number and chapter title
        split_string = input_string.split(": ")
        chapter_number = split_string[0].split(" ")[1]
        chapter_title = split_string[1]

        # Construct the output string in the desired format
        output_string = "第{}章: {}".format(chapter_number, chapter_title)

        return output_string
    else:
        chapter_number = input_string.split(" ")[1]
        output_string = "第{}章".format(chapter_number)
        return output_string

def process_next_chapter(file_name, soup, url):
    title = soup.find('h2', class_='title heading')
    # for each single chapter
    chapter_title_raw = soup.find('h3', class_='title').text.strip()
    chapter_title = convert_title(chapter_title_raw)

    p_elements = soup.select('div.userstuff p')

    # write each chapter
    with open(file_name + '.txt', 'a', encoding='utf-8', errors='ignore') as file:
        # write chapter title
        file.write(chapter_title + '\n\n')

        # chapter text
        for p in p_elements:
            p_text = p.get_text(separator='', strip=True)
            if p_text:
                file.write("　　" + p_text + '\n')
        
        file.write('\n')

    # Find the <li> element containing the "Next Chapter" link
    next_chapter_li = soup.find('li', string='Next Chapter →')
    
    if next_chapter_li:
        # Get the URL from the "href" attribute of the <a> tag
        next_chapter_url = next_chapter_li.find('a')['href']

        index = url.find("/works/")

        if index != -1:
            # Extract the string before the found index
            extracted_string = url[:index]
        else:
            print("Substring not found in the URL.")

        # Send a request to the next chapter URL and create a new BeautifulSoup object
        response = requests.get(extracted_string + next_chapter_url)
        new_soup = BeautifulSoup(response.content, 'html.parser')
        
        return new_soup
    
    return None
    
def write_file_single(soup):
    # make sure the file name is leagal
    illegal_chars = ['"', '*', '<', '>', '?', '\\', '|', '/', ':']
    
    title = soup.find('h2', class_='title heading')

    author = soup.find('a', rel='author')
    if author:
        have_author = True
    else:
        have_author = False

    for char in illegal_chars:
        file_name = title.text.strip().replace(char, '_')

    summary = soup.find('blockquote', class_='userstuff')
    if summary:
        have_summary = True
    else:
        have_summary = False

    with open(file_name + '.txt', 'w', encoding='utf-8') as file:
        file.write(title.text.strip() + '\n')
        if have_author:
            file.write("作者 - " + author.text + '\n')
        else:
            file.write("作者 - 匿名\n")
        if have_summary == True:
            file.write("简介 - " + '\n')
            if hasattr(summary, 'text'):
                file.write("　　" + summary.text.strip() + '\n')
        file.write('\n')
        
        # Write each non-empty <p> element's text as a new line in the text file
        p_elements = soup.select('div.userstuff p')
        for p in p_elements:
            if hasattr(p, 'text'):
                p_text = p.get_text(separator='', strip=True)
                if p_text:
                    file.write("　　" + p_text + '\n')
        print("TXT 文件下载完成。储存为：" + file_name + '.txt')

def write_file_multiple(soup, url):
    illegal_chars = ['"', '*', '<', '>', '?', '\\', '|', '/', ':']
    # title and information
    title = soup.find('h2', class_='title heading')

    author = soup.find('a', rel='author')
    if author:
        have_author = True
    else:
        have_author = False

    for char in illegal_chars:
        file_name = title.text.strip().replace(char, '_')

    summary = soup.find('blockquote', class_='userstuff')
    if summary:
        have_summary = True
    else:
        have_summary = False

    with open(file_name + '.txt', 'w', encoding='utf-8', errors='ignore') as file:
        file.write(title.text.strip() + '\n')
        if have_author:
            file.write("作者 - " + author.text + '\n')
        else:
            file.write("作者 - 匿名\n")
        if have_summary == True:
            file.write("简介 - " + '\n')
            if hasattr(summary, 'text'):
                file.write("　　" + summary.text.strip() + '\n')
        file.write('\n')

    while True:
        soup = process_next_chapter(file_name, soup, url)
        if soup is None:
            print("TXT 文件下载完成。储存为：" + file_name + '.txt')
            return

def main(url):
    try:
        is_single = analyzer(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        proceed_link = soup.find('a', string='Proceed')
        if proceed_link:
            print("已跳过免责声明。")
            soup = process_pre_page(soup)
        
        if is_single:
            print("检测到单章节。")
            write_file_single(soup)
        else:
            print("检测到多章节。")
            write_file_multiple(soup, url)

    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        logging.error(str(url))

# Tkinter UI code
def download_txt():
    url = url_entry.get()
    if url:
        main(url)
        url_entry.delete(0, tk.END)  # Clear the URL entry after clicking the button

# Create the main Tkinter window
root = tk.Tk()
root.title("AO3 Beautiful TXT Getter")

# Create and configure the URL entry widget
url_entry = tk.Entry(root, width=60)
url_entry.pack(pady=(20, 0))  # Increase vertical padding

# Create the download button with a white background
download_button = tk.Button(root, text="下载 TXT", command=download_txt, bg='white')
download_button.pack(pady=(10, 20))  # Increase vertical padding

# Create a text box to print messages with padding
text_box = tk.Text(root, width=80, height=15)
text_box.pack(padx=20, pady=20)  # Add padding to all sides of the text box

# # Create a scrollbar for the text box
# scrollbar = tk.Scrollbar(root)
# scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
# text_box.config(yscrollcommand=scrollbar.set)
# scrollbar.config(command=text_box.yview)

def write_to_textbox(text):
    text_box.insert(tk.END, text)
    text_box.see(tk.END)

# Redirect standard output to the text box
sys.stdout.write = write_to_textbox
print("请将文章链接贴在上面的框里，单击按钮下载。")
print("程序运行时请耐心等待，章节越多越慢，对于大于50章的文章耗时可能为几分钟……")

# Create the text box for the GitHub link as copiable text
github_text = tk.Text(root, width=80, height=1, relief=tk.FLAT, bg=root.cget("background"), wrap=tk.NONE)
github_text.insert(tk.END, "https://github.com/TheTarr/ao3_beautiful_txt_getter")
github_text.configure(state="disabled")
github_text.pack(pady=(10, 0))  # Add vertical padding

root.mainloop()