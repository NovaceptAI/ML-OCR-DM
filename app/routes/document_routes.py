# app/routes/document_routes.py

from flask import Blueprint, request, jsonify
from app.services import summarization, segmentation, sentiment_analysis, topic_modelling, similarity, chronology, \
    entity_resolution, keyword_search

# Create a Blueprint for document-related routes
document_blueprint = Blueprint('documents', __name__)


@document_blueprint.route('/upload', methods=['POST'])
def upload_document():
    # Assume the document is sent via a form with the name 'document'
    file = request.files.get('document')
    if not file:
        return jsonify({'error': 'No document uploaded'}), 400

    # Process the document here (e.g., save it, analyze it)
    # For demonstration, let's assume we save it temporarily
    filepath = 'app/tmp' + file.filename
    file.save(filepath)

    # Return a success response
    return jsonify({'message': 'Document uploaded successfully', 'path': filepath}), 200


@document_blueprint.route('/analyze', methods=['POST'])
def analyze_document():
    # This endpoint could be used to perform various analyses on the document
    # For simplicity, let's assume the document's path is sent in JSON format
    data = request.get_json()
    document_path = data.get('document_path')

    # Perform various analyses
    summary = summarization.summarize(document_path)
    # segments = segmentation.segment(document_path)
    # sentiment = sentiment_analysis.analyze(document_path)
    # topics = topic_modelling.model_topics(document_path)
    # doc_similarity = similarity.compute_similarity(document_path)
    # timeline = chronology.build_timeline(document_path)
    # entities = entity_resolution.resolve_entities(document_path)
    # keywords = keyword_search.extract_keywords(document_path)

    # Compile results
    results = {
        'summary': summary
        # 'segments': segments,
        # 'sentiment': sentiment,
        # 'topics': topics,
        # 'similarity': doc_similarity,
        # 'chronology': timeline,
        # 'entities': entities,
        # 'keywords': keywords
    }

    # Return the analysis results
    return jsonify(results), 200

# Additional routes can be added here for other functionalities
