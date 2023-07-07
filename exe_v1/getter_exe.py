import requests
from bs4 import BeautifulSoup
import logging

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
        output_string = "第{}章：{}".format(chapter_number, chapter_title)

        return output_string
    else:
        chapter_number = input_string.split(" ")[1]
        output_string = "第{}章".format(chapter_number)
        return output_string

def process_next_chapter(soup):
    title = soup.find('h2', class_='title heading')
    # for each single chapter
    chapter_title_raw = soup.find('h3', class_='title').text.strip()
    chapter_title = convert_title(chapter_title_raw)

    p_elements = soup.select('div.userstuff p')

    # write each chapters
    with open(title.text.strip() + '.txt', 'a', encoding='utf-8', errors='ignore') as file:
        # write each chapters - title
        file.write(chapter_title + '\n\n')

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
    title = soup.find('h2', class_='title heading')
    author = soup.find('a', rel='author')
    summary = soup.find('blockquote', class_='userstuff')
    if summary is not None:
        have_summary = True
    else:
        have_summary = False

    with open(title.text.strip() + '.txt', 'w', encoding='utf-8') as file:
        file.write(title.text.strip() + '\n')
        file.write("作者 - " + author.text + '\n')
        if have_summary == True:
            file.write("简介 - " + '\n')
            if hasattr(summary, 'text'):
                file.write("　　" + summary.text.strip() + '\n')
        file.write('\n')
        
        # Write each non-empty <p> element's text as a new line in the text file
        p_elements = soup.select('div.userstuff p')
        for p in p_elements:
            if hasattr(p, 'text'):
                p_text = '\n　　'.join(p.stripped_strings)
                if p_text:
                    file.write("　　" + p_text + '\n')
        print("TXT download successfully. File stored at: " + str(title.text.strip() + '.txt'))

def write_file_multiple(soup):
    # title and information
    title = soup.find('h2', class_='title heading')
    author = soup.find('a', rel='author')
    summary = soup.find('blockquote', class_='userstuff')
    if summary is not None:
        have_summary = True
    else:
        have_summary = False

    with open(title.text.strip() + '.txt', 'w', encoding='utf-8', errors='ignore') as file:
        file.write(title.text.strip() + '\n')
        file.write("作者 - " + author.text + '\n')
        if have_summary == True:
            file.write("简介 - " + '\n')
            if hasattr(summary, 'text'):
                file.write("　　" + summary.text.strip() + '\n')
        file.write('\n')

    while True:
        soup = process_next_chapter(soup)
        if soup is None:
            print("TXT download successfully. File stored at: " + str(title.text.strip() + '.txt'))
            return

def main(url):
    try:
        is_single = analyzer(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        proceed_link = soup.find('a', string='Proceed')
        if proceed_link:
            print("Adult check found and processed.")
            soup = process_pre_page(soup)
        
        if is_single:
            print("Single chapter article detected.")
            write_file_single(soup)
        else:
            print("Multiple chapters article detected. We will download all chapters.")
            write_file_multiple(soup)

    except Exception as e:
        logging.error("An error occurred: %s", str(e))

# Existing code...

if __name__ == "__main__":
    while True:
        url = input("Enter URL to download (or press Enter to exit): ")
        if url == "":
            break
        main(url)