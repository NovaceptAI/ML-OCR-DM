import fitz  # PyMuPDF
from dateutil.parser import parse
import re
from transformers import pipeline
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load NER model from Hugging Face
try:
    ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
    logger.info("NER model loaded successfully.")
except Exception as e:
    logger.error(f"Error loading NER model: {e}")


def is_valid_date(date_string):
    # Exclude patterns with three or more numbers separated by dots (e.g., IP addresses)
    if re.match(r'^\d{1,3}(\.\d{1,3}){2,}$', date_string):
        return False
    try:
        parse(date_string, fuzzy=False)
        return True
    except ValueError:
        return False


def extract_dates_with_sentences(text):
    # Extract entities using NER pipeline
    try:
        entities = ner_pipeline(text)
    except Exception as e:
        logger.error(f"Error during NER processing: {e}")
        return []

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
            if is_valid_date(match):
                try:
                    parsed_date = parse(match, fuzzy=True)
                    date_sentences.append((parsed_date, sentence))
                except ValueError:
                    continue

    for entity in entities:
        if entity['entity'] == 'B-DATE' or entity['entity'] == 'I-DATE':
            if is_valid_date(entity['word']):
                try:
                    parsed_date = parse(entity['word'], fuzzy=True)
                    for sentence in sentences:
                        if entity['word'] in sentence:
                            date_sentences.append((parsed_date, sentence))
                            break
                except ValueError:
                    continue

    return date_sentences


def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        logger.info("Text extracted successfully from PDF.")
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
    return text


def timed_events(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    if not text:
        logger.error("No text extracted from PDF.")
        return []

    dates_with_sentences = extract_dates_with_sentences(text)
    sorted_dates_with_sentences = sorted(dates_with_sentences, key=lambda x: x[0])

    sorted_events = [{"date": date.strftime("%d %B, %Y"), "sentence": sentence} for date, sentence in
                     sorted_dates_with_sentences]
    return sorted_events

# Example usage
# if __name__ == "__main__":
#     pdf_path = "/mnt/data/PDF-CRO-eBook.pdf"  # Update this with the path to your PDF
#     events = timed_events(pdf_path)
#     for event in events:
#         print(f"{event['date']}: {event['sentence']}")
