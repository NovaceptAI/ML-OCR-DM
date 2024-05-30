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
            page_texts = []
            complete_text = ""

            for page_num in range(num_pages):
                page_text = pdf_reader.pages[page_num].extract_text()
                page_texts.append(page_text)
                complete_text += page_text

            return page_texts, complete_text

    elif document_path.endswith('.docx'):
        doc = docx.Document(document_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    elif document_path.endswith('.txt'):
        with open(document_path, 'r', encoding='utf-8') as file:
            text = file.read()
    else:
        # Handle other document types here
        text = textract.process(document_path).decode('utf-8')

    return text, text


# def summarize_document(document_path):
#     try:
#         page_texts, complete_text = extract_text_from_document(document_path)
#         input_length = len(complete_text)
#         max_length = round(input_length / 2)
#
#         page_summaries = []
#         for page_text in page_texts:
#             page_input_length = len(page_text)
#             page_max_length = min(round(page_input_length / 2), 1024)  # Limit max_length to model's constraints
#
#             # Split the page_text into segments to avoid exceeding the max sequence length
#             segments = [page_text[i:i + 1024] for i in range(0, len(page_text), 1024)]
#
#             page_summary = ""
#             for segment in segments:
#                 segment_summary = summarizer(segment, max_length=page_max_length, min_length=round(page_max_length / 2),
#                                              do_sample=False)
#                 page_summary += segment_summary[0]['summary_text']
#
#             page_summaries.append(page_summary)
#
#         # Similarly, handle complete_text if needed
#
#     except Exception as e:
#         print("Error:", str(e))


def summarize_document(document_path):
    try:
        page_texts, complete_text = extract_text_from_document(document_path)
        input_length = len(complete_text)
        max_length = round(input_length / 2)

        # Summarize the complete text
        complete_summary = summarizer(complete_text, max_length=min(max_length, 1024), min_length=round(min(max_length, 1024) / 2), do_sample=False)
        output_file_path = "summary_output.txt"

        # Save the summary to a text file
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(complete_summary[0]['summary_text'])

        return "Summary saved to file: " + output_file_path

    except Exception as e:
        print("Error:", str(e))
