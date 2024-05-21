# app/services/summarization.py
from flask import jsonify
from transformers import pipeline
import PyPDF2
# Initialize the summarization pipeline with a pre-trained model
summarizer = pipeline("summarization")


def summarize(document_path):
    """
    Summarizes the content of a document.

    Args:
        document_path (str): The file path to the document to be summarized.

    Returns:
        str: A summary of the document.
    """
    try:
        summaries = []
        if document_path.endswith('.pdf'):
            with open(document_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                for page_num in range(num_pages):
                    page_content = pdf_reader.pages[page_num].extract_text()
                    input_length = len(page_content)
                    max_length = round(input_length / 2)  # Adjust max_length based on input length
                    page_summary = summarizer(page_content, max_length=max_length,
                                                            min_length=round(max_length / 2), do_sample=False)
                    summaries.append(page_summary[0]['summary_text'])

        full_summary = " ".join(summaries)
        results = {'summary': full_summary}

        return results

    except Exception as e:
        return jsonify({'error': f"Error in analyzing the document: {str(e)}"}), 500
