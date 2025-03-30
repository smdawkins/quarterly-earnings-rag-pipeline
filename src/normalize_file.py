

#This will be used to remove any mark up language in HTML so that only text is processed


from bs4 import BeautifulSoup, Comment
import re
import os
import pandas as pd
import html2text

def clean_file_with_soup(input_filepath, output_filepath=None):
    """
    Reads an HTML file, removes all HTML markup, and writes the plain text to a file.
    
    Args:
        input_filepath (str): Path to the input HTML file.
        output_filepath (str, optional): Path to the output plain text file.
            If not provided, '_cleaned.txt' will be appended to the original filename.
    """
    # Determine output filepath if not provided
    if output_filepath is None:
        base, ext = os.path.splitext(input_filepath)
        output_filepath = f"{base}_cleaned.txt"
    
    # Open and read the input HTML file
    with open(input_filepath, 'r', encoding='utf-8') as infile:
        html_content = infile.read()
    
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Remove script, style, and other unwanted tags
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    
    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    # Remove inline styles and other attributes from all tags
    for tag in soup.find_all():
        for attribute in ["style", "class", "id"]:
            if tag.has_attr(attribute):
                del tag[attribute]
    
    # Process tables separately: convert each table into a text representation
    for table in soup.find_all("table"):
        table_text = []
        for row in table.find_all("tr"):
            row_text = []
            # Extract header or data cells
            for cell in row.find_all(["th", "td"]):
                cell_text = cell.get_text(separator=" ", strip=True)
                row_text.append(cell_text)
            if row_text:
                table_text.append(" | ".join(row_text))
        # Replace the table tag with the joined table text
        table.replace_with("\n".join(table_text))
    
    # Get all the text with a separator and then collapse extra whitespace
    text = soup.get_text(separator=" ")
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    
    # Write the cleaned text to the output file
    with open(output_filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(cleaned_text)
    
    print(f"Cleaned text written to: {output_filepath}")

# Example usage:
# clean_html_file("path/to/your/10Q.html")


def clean_file_with_html2text(html_content):
    h = html2text.HTML2Text()
    h.ignore_links = True  # Optionally ignore converting links
    h.ignore_images = True # Optionally ignore images
    # You can tweak other settings if needed.
    return h.handle(html_content)
