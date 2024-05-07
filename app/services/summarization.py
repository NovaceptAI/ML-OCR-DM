# app/services/summarization.py

from transformers import pipeline

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
        # Open and read the document
        with open(document_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Use the summarization model to generate a summary
        summary = summarizer(content, max_length=130, min_length=30, do_sample=False)

        # Extract the summary text
        summary_text = summary[0]['summary_text']

        return summary_text

    except Exception as e:
        # Handle errors in reading the file or summarizing
        return f"Error in summarizing the document: {str(e)}"
