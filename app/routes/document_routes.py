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
    feature = data.get('feature')

    # Perform various analyses
    if feature == "Summarization":
        summary = summarization.summarize_document(document_path)
        return jsonify(summary)

    if feature == "Segmentation":
        segments = segmentation.segment_text(document_path)
        # Return the analysis results
        return jsonify(segments), 200

    if feature == "Sentiment":
        sentence_sentiments = sentiment_analysis.perform_sentiment_analysis(document_path)

        # Save sentiment analysis results to a text file
        output_file_path = "sentiment_analysis_results.txt"

        with open(output_file_path, 'w') as output_file:
            output_file.write("Sentiment Analysis Results - Sentences:\n")
            for i, sentiment in enumerate(sentence_sentiments):
                sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
                output_file.write(f"Sentence {i + 1}: Sentiment - {sentiment} ({sentiment_label})\n")

        # output_file.write("\nSentiment Analysis Results - Paragraphs:\n")

        output_statement = f"Sentiment analysis results saved to {output_file_path}"
        return output_statement

    if feature == "Chronology":
        chronolog = chronology.timed_events(document_path)
        return jsonify(chronolog)

    if feature == "Entity":
        entities = entity_resolution.find_entities(document_path, threshold=0.8)
        return jsonify(entities)

    if feature == "Keyword":
        keywords = keyword_search.search(document_path)
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
