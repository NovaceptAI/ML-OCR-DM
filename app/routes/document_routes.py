# app/routes/document_routes.py
import os

from flask import Blueprint, request, jsonify
from app.services import summarization, segmentation, sentiment_analysis, topic_modelling, similarity, chronology, \
    entity_resolution, keyword_search
import PyPDF2, uuid

# Create a Blueprint for document-related routes
document_blueprint = Blueprint('documents', __name__)


@document_blueprint.route('/upload', methods=['POST'])
def upload_document():
    # Assume the documents are sent via a form with the name 'document'
    files = request.files.getlist('document')
    if not files:
        return jsonify({'error': 'No documents uploaded'}), 400

    file_paths = []

    for file in files:
        if file:
            # Replace spaces in the file name with underscores
            new_filename = file.filename.replace(" ", "_")

            # Save the file temporarily with the modified file name
            filepath = 'app/tmp/' + new_filename
            file.save(filepath)

            # Collect the file path
            file_paths.append(filepath)

    return jsonify({'message': 'Documents uploaded successfully', 'file_paths': file_paths}), 200


@document_blueprint.route('/analyze', methods=['POST'])
def analyze_document():
    # This endpoint could be used to perform various analyses on the document
    # For simplicity, let's assume the document's path is sent in JSON format
    data = request.get_json()
    document_path = data.get('document_path')

    # Check if file is present
    if not os.path.exists(document_path):
        return {"error": "No file present at the specified document path"}

    feature = data.get('feature')

    # Generate a UUID
    unique_filename = str(uuid.uuid4()) + ".txt"

    # Create the file with the UUID as its name
    with open(unique_filename, 'w') as f:
        f.write("")

    # Perform various analyses
    if feature == "Summarization":
        summary = summarization.summarize_document(document_path, unique_filename)
        return jsonify(summary)

    if feature == "Segmentation":
        segments = segmentation.segment_text(document_path)
        # Return the analysis results
        return jsonify(segments), 200

    if feature == "Sentiment":
        analysis = sentiment_analysis.perform_sentiment_analysis(document_path)
        return analysis

    if feature == "Chronology":
        chronolog = chronology.timed_events(document_path)
        return jsonify(chronolog)

    if feature == "Entity":
        entities = entity_resolution.find_entities(document_path)
        return jsonify(entities)

    if feature == "Keyword":
        keyword_list = data.get('keywords')
        keywords = keyword_search.search(document_path, keyword_list)
        return jsonify(keywords)

    if feature == "TopicModelling":
        topics = topic_modelling.perform_topic_modeling(document_path)
        return jsonify(topics)

    if feature == "Similarity":
        similar = similarity.get_similarity(document_path, threshold=0.8)
        return jsonify(similar)

    else:
        return "Feature Not Available"


# Additional routes can be added here for other functionalities
