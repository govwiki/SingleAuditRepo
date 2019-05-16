import os
import PyPDF2
import re

# Assumes last 4 characters of file name are YYYY
# Assumes date will *immediately* follow one of the known prefixes
# Assumes date is sepearated by non-alphanumeric chars (these are converted to spaces)
# Assumes date is ordered month, then day, then YYYY or day, then month, then YYYY
# Assume first instance of pattern is accurate


# Takes in a pdf file, checks if date in file name matches date in file, returns boolean
def compare_year(file_name, file_type, num_pages, **kwargs):
    """
    Args:
        file_name: valid path to PDF file.
        file_type: specify the file type e.g. "gp" for general purpose. Regex applied is file_type specific.
        num_pages: how many pages should be searched. script stops after first instance is found.

    Returns:
        (String) Confirmation year in PDF does/does not match year in file name. If does not, suggests file name

    """

    print('Checking {}'.format(file_name))
    # Sanitize inputs
    # check/exception file paths
    
    # Read in file
    with open(file_name, 'rb') as pdf_file:
        pdfReader = PyPDF2.PdfFileReader(pdf_file)

        num_pages = min([num_pages, pdfReader.numPages])

        for i in range(num_pages):
            pageObj = pdfReader.getPage(i)
            page_text = pageObj.extractText()
            if file_type == 'gp':
                return check_general_purpose_year(file_name, page_text)
            else:
                return 'File type not (yet) supported'

def check_general_purpose_year(file_name, page_text):
    # Get year from file name
    # Assumes naming convention
    file_name_year = os.path.splitext(file_name)[0][-4:]
    
    prefix_list = [' through ', 'year ended ', 'year ending ']
    
    # Get year from PDF
    # needs checks on output
    for i in prefix_list:
        start_key = i
        try:
            index_start = page_text.lower().index(start_key) + len(start_key)
            print('Prefix substring "{}" found.'.format(start_key))
            # Remove non alphanum
            clean_text = re.sub(r"[^\w\s]", ' ', page_text[index_start:])
            # Consolidate white space
            clean_text = re.sub(r"\s+", ' ', clean_text).strip()
            date_parts = clean_text.split(' ')[:3]
            # Get year
            page_text_year = date_parts[2]
            break
        except:
            print('Prefix substring "{}" not found.'.format(start_key))
    
    # Need to add year validation
    
    if 'page_text_year' not in locals():
        return 'dang. No pattern matched in file.'
    elif file_name_year == page_text_year:
        return 'yay. Year in file name matches year found in PDF.'
    else:
        file_name_rec = os.path.splitext(file_name)[0][:-4]+page_text_year
        return 'dang. Year in file name ({}) does not match year found in PDF ({}). Recommend renaming to:\n{}\n'.format(
            file_name_year
            ,page_text_year
            ,file_name_rec)
