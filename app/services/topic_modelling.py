import re
import os
import json
import uuid
from gensim import corpora, models
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import boto3
from app.services.summarization import extract_text_from_document
from app.config.config import get_aws_creds

# Define custom stop words to exclude from topics
custom_stopwords = set(
    stopwords.words('english') + ['a', 'an', 'the', 'that', 'this', 'it', 'is', 'are', 'was', 'were'])


def preprocess_text(text):
    """Tokenizes text and removes stop words and non-alphabetic words."""
    tokens = word_tokenize(text)
    filtered_tokens = [word.lower() for word in tokens if word.isalpha() and word.lower() not in custom_stopwords]
    return filtered_tokens


def topic_modeling(document_path):
    """Performs topic modeling on the provided document."""
    complete_text = extract_text_from_document(document_path)

    # Preprocess the complete text
    processed_text = preprocess_text(complete_text)

    # Create a dictionary representation of the documents
    dictionary = corpora.Dictionary([processed_text])

    # Convert tokenized documents into a document-term matrix
    corpus = [dictionary.doc2bow(processed_text)]

    # Build the LDA model with consistent random state for reproducibility
    lda_model = models.LdaModel(corpus, num_topics=10, id2word=dictionary, passes=15, random_state=42)

    # Get the topics
    topics = lda_model.print_topics(num_words=10)

    # Filter topics
    filtered_topics = filter_topics(topics)

    return filtered_topics


def filter_topics(topic_results):
    """Filters out stop words and punctuation from the topic results."""
    filtered_topics = []
    stop_words = {"the", "of", "to", "and", "in", "on", "for"}  # Add more stop words as needed

    for topic_id, topic in topic_results:
        words = re.findall(r'"(.*?)"', topic)  # Extract words within double quotes
        filtered_words = [word for word in words if word.lower() not in stop_words and not re.match(r'[^\w\s]', word)]
        filtered_topics.append([topic_id, filtered_words[:4]])  # Select top 4 meaningful words

    return filtered_topics


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
    unique_filename = str(uuid.uuid4()) + "_topic_modeling.json"
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


def perform_topic_modeling(document_path):
    """Main function to perform topic modeling, save results to S3, and return the response."""
    topics = topic_modeling(document_path)

    s3_url = save_to_s3(topics)

    if s3_url:
        return {
            "message": "Topic modeling done and results uploaded successfully",
            "s3_url": s3_url,
            "topics": topics
        }
    else:
        return {"error": "Failed to upload results to S3"}

# Example usage
# document_path = 'C:\\Users\\novneet.patnaik\\Documents\\GitHub\\ML-OCR-DM\\app\\tmp\\CRO_Beginners_Guide.pdf'
# bucket_name = 'your-s3-bucket-name'
# result = main(document_path, bucket_name)
# print(result)
