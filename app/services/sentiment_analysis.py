from textblob import TextBlob
import PyPDF2
from app.services.summarization import extract_text_from_document


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        text = ""
        for page_num in range(num_pages):
            text += pdf_reader.pages[page_num].extract_text()
        return text


def perform_sentiment_analysis(document_path):
    text = extract_text_from_pdf(document_path)
    blob = TextBlob(text)

    # Sentiment analysis at the sentence level
    sentence_sentiments = [sentence.sentiment.polarity for sentence in blob.sentences]

    # Sentiment analysis at the paragraph level
    # paragraph_sentiments = [paragraph.sentiment.polarity for paragraph in blob.noun_phrases]

    return sentence_sentiments #, paragraph_sentiments

#
# # Example PDF file path
# pdf_path = "example.pdf"
#
# # Extract text from the PDF
# extracted_text = extract_text_from_document(pdf_path)
#
# # Perform sentiment analysis on sentences and paragraphs
# sentence_sentiments, paragraph_sentiments = perform_sentiment_analysis(extracted_text)
#
# # Print sentiment analysis results
# print("Sentiment Analysis Results - Sentences:")
# for i, sentiment in enumerate(sentence_sentiments):
#     print(f"Sentence {i + 1}: Sentiment - {sentiment}")
#
# print("\nSentiment Analysis Results - Paragraphs:")
# for i, sentiment in enumerate(paragraph_sentiments):
#     print(f"Paragraph {i + 1}: Sentiment - {sentiment}")
