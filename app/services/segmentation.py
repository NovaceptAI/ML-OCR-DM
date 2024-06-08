import os
import boto3
import uuid
import re
from PyPDF2 import PdfReader
from docx import Document
from botocore.exceptions import NoCredentialsError

# Configure AWS credentials
aws_access_key_id = 'AKIAVRUVQANFUJNOWIUW'
aws_secret_access_key = '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'
aws_region = 'us-east-1'
bucket_name = "digimachine"

# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)


def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PdfReader(file)
        num_pages = len(reader.pages)
        for page_num in range(num_pages):
            page_text = reader.pages[page_num].extract_text()
            text += page_text + "\n"
    return text


def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text


def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text


def save_to_s3(file_path, s3_filename):
    try:
        s3.upload_file(file_path, bucket_name, s3_filename)
        url = f"https://{bucket_name}.s3.amazonaws.com/{s3_filename}"
        return url
    except NoCredentialsError:
        raise IOError("Credentials not available")
    except Exception as e:
        raise IOError(f"Failed to upload file to S3: {e}")


def segment_text_by_structure(text):
    section_titles = [
        "Introduction", "Table of Contents", "Section", "Chapter", "Conclusion", "Summary",
        "Abstract", "Overview", "Preface", "Prologue", "Epilogue"
    ]
    sections = {}
    current_section = "Unknown Section"
    sections[current_section] = ""

    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if any(title.lower() in line.lower() for title in section_titles):
            current_section = line
            sections[current_section] = ""
        sections[current_section] += line + "\n"

    return sections


def save_segments_to_file(segments, output_file):
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            for section, content in segments.items():
                file.write(f"{section}\n{content}\n\n")
    except Exception as e:
        raise IOError(f"Failed to save segments to file: {e}")


def segment_text(file_path):
    unique_filename = str(uuid.uuid4()) + "_segments.txt"
    output_file = "app/tmp/" + unique_filename
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            text = extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            text = extract_text_from_txt(file_path)
        else:
            raise ValueError("Unsupported file format. Please upload a PDF, DOCX, or TXT file.")

        segments = segment_text_by_structure(text)
        save_segments_to_file(segments, output_file)
        s3_url = save_to_s3(output_file, unique_filename)

        # Delete the local file after uploading to S3
        if os.path.exists(output_file):
            os.remove(output_file)

        return {"message": "Segmentation and upload successful", "s3_url": s3_url, "segments": segments}
    except Exception as e:
        return {"error": str(e)}


# # Example usage
# file_path = "/mnt/data/PDF-CRO-eBook.pdf"  # Update this with the path to your document
# bucket_name = "your-s3-bucket-name"  # Replace with your S3 bucket name
# result = main(file_path, bucket_name)
# print(result)
