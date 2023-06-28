import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

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

def process_next_chapter(soup):
    title = soup.find('h2', class_='title heading')
    # for each single chapter
    chapter_title = soup.find('h3', class_='title')
    p_elements = soup.select('div.userstuff p')

    # write each chapters
    with open(title.text.strip() + '.txt', 'a', encoding='utf-8') as file:
        # write each chapters - title
        file.write(chapter_title.text.strip() + '\n')

        # chapter - text
        for p in p_elements:
            p_text = '\n　　'.join(p.stripped_strings)
            # p_text = p.text.strip()
            if p_text:
                file.write("　　" + p_text + '\n')
        
        file.write('\n')

    # Find the <li> element containing the "Next Chapter" link
    next_chapter_li = soup.find('li', string='Next Chapter →')
    
    if next_chapter_li:
        # Get the URL from the "href" attribute of the <a> tag
        next_chapter_url = next_chapter_li.find('a')['href']
        
        # Send a request to the next chapter URL and create a new BeautifulSoup object
        response = requests.get("https://archiveofourown.org" + next_chapter_url)
        new_soup = BeautifulSoup(response.content, 'html.parser')
        
        return new_soup
    
    return None
    
def write_file_single(soup):

    title = soup.find('h2', class_='title heading')
    author = soup.find('a', rel='author')
    try:
        summary = soup.find('blockquote', class_='userstuff')
        have_summary = True
    except:
        have_summary = False
    p_elements = soup.select('div.userstuff p')
    

    with open(title.text.strip() + '.txt', 'w', encoding='utf-8') as file:
        file.write(title.text.strip() + '\n')
        file.write("作者 - " + author.text + '\n')
        if have_summary == True:
            file.write("简介 - " + '\n')
            for p in summary:
                p_text = p.text.strip()
                if p_text:
                    file.write("　　" + p_text + '\n')
        file.write('\n')
        
        # Write each non-empty <p> element's text as a new line in the text file
        for p in p_elements:
            # p_text = p.text.strip()
            p_text = '\n　　'.join(p.stripped_strings)
            if p_text:
                file.write("　　" + p_text + '\n')

def write_file_multiple(soup):

    # title and information
    title = soup.find('h2', class_='title heading')
    author = soup.find('a', rel='author')
    try:
        summary = soup.find('blockquote', class_='userstuff')
        have_summary = True
    except:
        have_summary = False

    with open(title.text.strip() + '.txt', 'w', encoding='utf-8') as file:
        file.write(title.text.strip() + '\n')
        file.write("作者 - " + author.text + '\n')
        if have_summary == True:
            file.write("简介 - " + '\n')
            for p in summary:
                p_text = p.text.strip()
                if p_text:
                    file.write("　　" + p_text + '\n')
        file.write('\n')

    while True:
        try:
            soup = process_next_chapter(soup)
        except:
            return

# Prompt the user to enter a URL
url = input("Enter the URL: ")

is_single = analyzer(url)

# Send a GET request to the specified URL
response = requests.get(url)
    
# Create a BeautifulSoup object to parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

proceed_link = soup.find('a', text='Proceed')

if proceed_link:
    print("adult check found and processed.\n")
    soup = process_pre_page(soup)

if is_single == True:
    print("Single chapter article detected.\n")
    write_file_single(soup)
else:
    print("Mutiple chapters article detected. We will download all chapters.\n")
    write_file_multiple(soup)