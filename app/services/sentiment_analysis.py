from textblob import TextBlob
import PyPDF2
import boto3
import uuid
import os
from app.services.summarization import extract_text_from_document
from app.config.config import get_aws_creds


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        text = ""
        for page_num in range(num_pages):
            text += pdf_reader.pages[page_num].extract_text()
        return text


def perform_analysis(document_path):
    text = extract_text_from_pdf(document_path)
    blob = TextBlob(text)

    # Sentiment analysis at the sentence level
    sentence_sentiments = [(str(sentence), sentence.sentiment.polarity) for sentence in blob.sentences]

    # Sentiment analysis at the paragraph level
    paragraphs = text.split('\n\n')  # Assuming paragraphs are separated by double newlines
    paragraph_sentiments = [(paragraph, TextBlob(paragraph).sentiment.polarity) for paragraph in paragraphs]

    return sentence_sentiments, paragraph_sentiments


def save_sentiment_to_file(sentence_sentiments, paragraph_sentiments, output_file):
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write("Sentence Sentiments:\n")
            for sentence, sentiment in sentence_sentiments:
                file.write(f"Sentence: {sentence}\nSentiment: {sentiment}\n\n")

            file.write("Paragraph Sentiments:\n")
            for paragraph, sentiment in paragraph_sentiments:
                file.write(f"Paragraph: {paragraph}\nSentiment: {sentiment}\n\n")
        return True
    except Exception as e:
        print(f"Failed to save sentiment analysis to file: {e}")
        return False


def upload_to_s3(file_path, s3_filename):
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
    try:
        s3.upload_file(file_path, bucket_name, s3_filename)
        url = f"https://{bucket_name}.s3.amazonaws.com/{s3_filename}"
        return url
    except Exception as e:
        print(f"Failed to upload file to S3: {e}")
        return None


def perform_sentiment_analysis(document_path):
    sentence_sentiments, paragraph_sentiments = perform_analysis(document_path)
    unique_filename = str(uuid.uuid4()) + "_sentiment_analysis.txt"
    output_file = "app/tmp/" + unique_filename

    if save_sentiment_to_file(sentence_sentiments, paragraph_sentiments, output_file):
        s3_url = upload_to_s3(output_file, unique_filename)

        if s3_url:
            os.remove(output_file)
            return {
                "message": "Sentiment analysis done and uploaded successfully",
                "s3_url": s3_url,
                "sentence_sentiments": sentence_sentiments,
                "paragraph_sentiments": paragraph_sentiments
            }
        else:
            return {"error": "Failed to upload file to S3"}
    else:
        return {"error": "Failed to save sentiment analysis to file"}

# Example usage
# if __name__ == "__main__":
#     document_path = "/mnt/data/your_document.pdf"  # Update this with the path to your document
#     bucket_name = "your-s3-bucket-name"  # Replace with your S3 bucket name
#     result = main(document_path, bucket_name)
#     print(result)
