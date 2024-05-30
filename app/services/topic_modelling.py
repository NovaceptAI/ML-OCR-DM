import re

from gensim import corpora, models
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from app.services.summarization import extract_text_from_document

# Define custom stop words to exclude from topics
custom_stopwords = set(
    stopwords.words('english') + ['a', 'an', 'the', 'that', 'this', 'it', 'is', 'are', 'was', 'were'])


def preprocess_text(text):
    # Tokenize text and remove stop words and non-alphabetic words
    tokens = word_tokenize(text)
    filtered_tokens = [word.lower() for word in tokens if word.isalpha() and word.lower() not in custom_stopwords]
    return filtered_tokens


def perform_topic_modeling(document_path):
    page_texts, complete_text = extract_text_from_document(document_path)

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

    # final_topics = filter_topics(topics)  # Implement your filter_topics function here

    return topics


# Define a function to filter out stop words and punctuation
def filter_topics(topic_results):
    filtered_topics = []
    stop_words = {"the", "of", "to", "and", "in", "on", "for"}  # Add more stop words as needed

    for topic_id, topic in topic_results:
        words = re.findall(r'"(.*?)"', topic)  # Extract words within double quotes
        filtered_words = [word for word in words if word.lower() not in stop_words and not re.match(r'[^\w\s]', word)]
        filtered_topics.append([topic_id, filtered_words[:4]])  # Select top 4 meaningful words

    return filtered_topics
