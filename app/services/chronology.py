import fitz  # PyMuPDF
from dateutil.parser import parse
import re


def extract_dates_with_sentences(text):
    # Regular expression to match various date patterns
    date_patterns = [
        r'\b(?:\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})\b',  # Date patterns like 01/05/2023, 01.12.2023
        r'\b(?:\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})\b',  # Date patterns like 2023-12-31
        r'\b(?:[A-Za-z]+\s\d{1,2},\s\d{4})\b',  # Date patterns like April 18, 2013
        r'\b(?:[A-Za-z]+\s\d{4})\b',  # Date patterns like April 2016, June 2023
        r'\b(?:\d{1,2}:\d{2}(?:[apAP][mM])?)\b',  # Time patterns like 10:30am, 14:30
    ]

    combined_pattern = '|'.join(date_patterns)
    sentences = re.split(r'(?<=[.!?]) +', text)  # Split text into sentences
    date_sentences = []

    for sentence in sentences:
        matches = re.findall(combined_pattern, sentence)
        for match in matches:
            try:
                parsed_date = parse(match, fuzzy=True)
                date_sentences.append((parsed_date, sentence))
            except ValueError:
                continue

    return date_sentences


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()

    return text


def timed_events(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    text = "In the sweltering heat of July 1969, humans landed on the moon for the first time, marking a giant leap " \
           "for mankind. Fast forward to the crisp autumn days of September 2007, the first iPhone was released, " \
           "revolutionizing the way we communicate. Back in the somber month of May 1945, World War II came to an " \
           "end, bringing a sense of relief and hope for the future. Moving ahead to the early days of March 1990, " \
           "the World Wide Web was born, changing the way information is accessed globally. Jumping to the hot days " \
           "of July 1776, the United States declared its independence, shaping the course of history. Looking back at " \
           "the chilly November days of 1989, the fall of the Berlin Wall symbolized the end of an era and the " \
           "beginning of new possibilities. "
    dates_with_sentences = extract_dates_with_sentences(text)
    sorted_dates_with_sentences = sorted(dates_with_sentences, key=lambda x: x[0])

    # Convert sorted sentences to a list of sentences
    sorted_sentences = [sentence.strip() for _, sentence in sorted_dates_with_sentences]
    return sorted_sentences
