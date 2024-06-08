import os
import json
import uuid
import PyPDF2
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
import boto3
from app.config.config import get_aws_creds


def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        text = ""
        for page_num in range(num_pages):
            page_text = reader.pages[page_num].extract_text()
            text += page_text + "\n"
    return text


def preprocess_text(text):
    """Preprocesses the extracted text by splitting into lines and removing empty lines."""
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    return pd.DataFrame(lines, columns=['text'])


def calculate_similarity(df):
    """Calculates the cosine similarity matrix for the text data."""
    vectorizer = TfidfVectorizer().fit_transform(df['text'])
    vectors = vectorizer.toarray()
    similarity_matrix = cosine_similarity(vectors)
    return similarity_matrix


def entity_resolution(df, threshold=80):
    """Finds pairs of similar text entries based on a fuzzy similarity threshold."""
    similar_pairs = []
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            similarity = fuzz.token_sort_ratio(df.iloc[i]['text'], df.iloc[j]['text'])
            if similarity >= threshold:
                similar_pairs.append((i, j, similarity))
    return similar_pairs


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
    unique_filename = str(uuid.uuid4()) + "_entity_resolution.json"
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


def find_entities(pdf_path, threshold=80):
    """Extracts text from a PDF, processes it, finds similar text entries, and saves the results to S3."""
    text = extract_text_from_pdf(pdf_path)
    df = preprocess_text(text)
    similarity_matrix = calculate_similarity(df)
    matches = entity_resolution(df, threshold)

    results = []
    for (index1, index2, similarity) in matches:
        results.append({
            "similarity": similarity,
            "line_1": {
                "line_number": index1 + 1,
                "text": df.iloc[index1]['text']
            },
            "line_2": {
                "line_number": index2 + 1,
                "text": df.iloc[index2]['text']
            }
        })

    s3_url = save_to_s3(results)

    if s3_url:
        return {
            "message": "Entity resolution done and results uploaded successfully",
            "s3_url": s3_url,
            "results": results
        }
    else:
        return {"error": "Failed to upload results to S3"}

# Example usage
# pdf_path = 'C:\\Users\\novneet.patnaik\\Documents\\GitHub\\ML-OCR-DM\\app\\tmp\\CRO_Beginners_Guide.pdf'
# bucket_name = 'your-s3-bucket-name'
# result = find_entities(pdf_path, bucket_name, threshold=80)
# print(result)
