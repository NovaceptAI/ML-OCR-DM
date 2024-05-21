# app/routes/document_routes.py

from flask import Blueprint, request, jsonify
from app.services import summarization, segmentation, sentiment_analysis, topic_modelling, similarity, chronology, \
    entity_resolution, keyword_search
import PyPDF2

# Create a Blueprint for document-related routes
document_blueprint = Blueprint('documents', __name__)


@document_blueprint.route('/upload', methods=['POST'])
def upload_document():
    # Assume the document is sent via a form with the name 'document'
    file = request.files.get('document')
    if not file:
        return jsonify({'error': 'No document uploaded'}), 400

    # Replace spaces in the file name with underscores
    new_filename = file.filename.replace(" ", "_")

    # Process the document here (e.g., save it, analyze it)
    # For demonstration, let's assume we save it temporarily with the modified file name
    filepath = 'app/tmp/' + new_filename
    file.save(filepath)

    return jsonify({'message': 'Document uploaded successfully', 'filename': file.filename, 'path': filepath}), 200


@document_blueprint.route('/analyze', methods=['POST'])
def analyze_document():
    """
       Endpoint to analyze a PDF document by summarizing its content page by page.

       Returns:
           JSON: A JSON response containing the summarized content of the PDF document.
    """
    data = request.get_json()
    document_path = data.get('document_path')

    try:
        summaries = []
        if document_path.endswith('.pdf'):
            with open(document_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                for page_num in range(num_pages):
                    page_content = pdf_reader.pages[page_num].extract_text()
                    input_length = len(page_content)
                    max_length = min(2 * input_length, 130)  # Adjust max_length based on input length
                    page_summary = summarization.summarizer(page_content, max_length=max_length, min_length=30,
                                                            do_sample=False)
                    summaries.append(page_summary[0]['summary_text'])

        full_summary = " ".join(summaries)
        results = {'summary': full_summary}

        return jsonify(results), 200

    except Exception as e:
        return jsonify({'error': f"Error in analyzing the document: {str(e)}"}), 500

# Additional routes can be added here for other functionalities
