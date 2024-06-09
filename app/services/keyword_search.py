import os
import json
import uuid
import re
import PyPDF2
import docx
import boto3
from pydub import AudioSegment
import speech_recognition as sr
from app.config.config import get_aws_creds


def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file and keeps track of page and line numbers."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        text_by_page_and_line = []
        for page_num in range(num_pages):
            page_text = reader.pages[page_num].extract_text()
            lines = page_text.split('\n')
            for line_num, line in enumerate(lines):
                text_by_page_and_line.append((page_num + 1, line_num + 1, line))
    return text_by_page_and_line


def extract_text_from_docx(docx_path):
    """Extracts text from a DOCX file and keeps track of line numbers."""
    doc = docx.Document(docx_path)
    text_by_page_and_line = []
    for i, paragraph in enumerate(doc.paragraphs):
        text_by_page_and_line.append((1, i + 1, paragraph.text))  # Treat DOCX as one page
    return text_by_page_and_line


def extract_text_from_txt(txt_path):
    """Extracts text from a TXT file and keeps track of line numbers."""
    with open(txt_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        text_by_page_and_line = [(1, i + 1, line.strip()) for i, line in enumerate(lines) if
                                 line.strip()]  # Treat TXT as one page
    return text_by_page_and_line


def convert_audio_to_text(audio_path):
    """Converts audio file to text using speech recognition."""
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_file(audio_path)
    audio_path_wav = audio_path.rsplit('.', 1)[0] + '.wav'
    audio.export(audio_path_wav, format='wav')

    with sr.AudioFile(audio_path_wav) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)

    os.remove(audio_path_wav)
    return [(1, 1, text)]  # Treat the entire audio as one "page" and one "line"


def extract_text_from_document(file_path):
    """Extracts text from a document based on its file extension."""
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.docx':
        return extract_text_from_docx(file_path)
    elif file_extension == '.txt':
        return extract_text_from_txt(file_path)
    elif file_extension in ['.mp3', '.wav', '.flac', '.ogg']:
        return convert_audio_to_text(file_path)
    else:
        raise ValueError("Unsupported file format")


def preprocess_text(text_by_page_and_line):
    """Preprocesses the extracted text by splitting into sentences."""
    sentences = []
    for page_num, line_num, text in text_by_page_and_line:
        for sentence in re.split(r'(?<=[.!?]) +', text):
            sentences.append((page_num, line_num, sentence))
    return sentences


def search_keywords(sentences, keywords):
    """Searches for keywords in the preprocessed text and keeps track of page and line numbers."""
    found_keywords = []
    for page_num, line_num, sentence in sentences:
        for keyword in keywords:
            if re.search(rf'\b{re.escape(keyword)}\b', sentence, re.IGNORECASE):
                found_keywords.append(
                    {"keyword": keyword, "sentence": sentence, "page_number": page_num, "line_number": line_num})
    return found_keywords


def save_to_s3(data):
    """Saves the data to an S3 bucket and returns the S3 URL."""
    aws_creds = get_aws_creds()
    if not aws_creds:
        return None

    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_creds['aws_access_key_id'],
        aws_secret_access_key=aws_creds['aws_secret_access_key'],
        region_name=aws_creds['region_name']
    )
    bucket_name = aws_creds['bucket_name']
    unique_filename = str(uuid.uuid4()) + "_keyword_search.json"
    local_path = "app/tmp/" + unique_filename

    with open(local_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    try:
        s3.upload_file(local_path, bucket_name, unique_filename)
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{unique_filename}"
        return s3_url
    except Exception as e:
        print(f"Failed to upload file to S3: {e}")
        return None
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)


def search(document_path, keywords):
    """Main function to perform keyword search, save results to S3, and return the response."""
    text_by_page_and_line = extract_text_from_document(document_path)
    sentences = preprocess_text(text_by_page_and_line)
    found_keywords = search_keywords(sentences, keywords)

    s3_url = save_to_s3(found_keywords)

    if s3_url:
        return {
            "message": "Keyword search done and results uploaded successfully",
            "s3_url": s3_url,
            "found_keywords": found_keywords
        }
    else:
        return {"error": "Failed to upload results to S3"}

# Example usage
# document_path = 'C:\\Users\\novneet.patnaik\\Documents\\GitHub\\ML-OCR-DM\\app\\tmp\\example.mp3'
# bucket_name = 'your-s3-bucket-name'
# keywords = ['keyword1', 'keyword2', 'keyword3']
# result = main(document_path, bucket_name, keywords)
# print(result)
