# app/services/summarization.py
from flask import jsonify
from transformers import pipeline
import PyPDF2
import docx
import textract

# Initialize the summarization pipeline with a pre-trained model
summarizer = pipeline("summarization")


def extract_text_from_document(document_path):
    if document_path.endswith('.pdf'):
        with open(document_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            text = ""
            for page_num in range(num_pages):
                text += pdf_reader.pages[page_num].extract_text()
    elif document_path.endswith('.docx'):
        doc = docx.Document(document_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    elif document_path.endswith('.txt'):
        with open(document_path, 'r') as file:
            text = file.read()
    else:
        # Handle other document types here
        text = textract.process(document_path).decode('utf-8')

    return text


def summarize_document(document_path):
    try:
        text = extract_text_from_document(document_path)
        input_length = len(text)
        max_length = round(input_length / 2)
        page_summary = summarizer(text, max_length=max_length, min_length=round(max_length / 2), do_sample=False)
        full_summary = page_summary[0]['summary_text']
        results = {'summary': full_summary}

        return results

    except Exception as e:
        return {'error': f"Error in analyzing the document: {str(e)}"}, 500
