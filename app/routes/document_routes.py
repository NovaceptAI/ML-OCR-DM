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
    # This endpoint could be used to perform various analyses on the document
    # For simplicity, let's assume the document's path is sent in JSON format
    data = request.get_json()
    document_path = data.get('document_path')

    # Perform various analyses
    # summary = summarization.summarize_document(document_path)
    segments = segmentation.segment_text(document_path)

    # Specify the file path where you want to save the text
    file_path = "output_segments.txt"

    with open(file_path, "w", encoding="utf-8") as file:
        for segment, text in segments.items():
            file.write(f"{segment}:\n{text}\n\n")

    # Return the analysis results
    return jsonify(segments), 200

# Additional routes can be added here for other functionalities
