from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from app.services.summarization import extract_text_from_document


def segment_text(document_path):
    page_texts, text = extract_text_from_document(document_path)
    text_length = len(text)
    num_segments = max(1, round(text_length / 1000))
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform([text])

    if tfidf_matrix.shape[0] <= num_segments:
        # Specify the file path where you want to save the text
        file_path = "output_segments.txt"

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text)
        return {"Segment 1": text}  # Return the entire text as a single segment

    kmeans = KMeans(n_clusters=num_segments, random_state=0)
    kmeans.fit(tfidf_matrix)

    segments = {}
    for i, label in enumerate(kmeans.labels_):
        if label not in segments:
            segments[label] = []
        segments[label].append(i)

    # Specify the file path where you want to save the text
    file_path = "output_segments.txt"

    with open(file_path, "w", encoding="utf-8") as file:
        for segment, text in segments.items():
            file.write(f"{segment}:\n{text}\n\n")

    segmented_text = {}
    for label, indices in segments.items():
        segment_text = " ".join([text[i] for i in indices])
        segmented_text += f"Segment {label + 1}:\n{segment_text}\n\n"

    return segmented_text
