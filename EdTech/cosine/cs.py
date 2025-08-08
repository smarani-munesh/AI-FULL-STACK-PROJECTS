import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load data
df = pd.read_csv("learning_resources_large.csv")

# Combine text fields
df['text'] = df['title'] + " " + df['description'] + " " + df['subject']

# Fit TF-IDF on resource text
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['text'])

# 🔍 New Function: Recommend based on free-text query
def get_recommendations_from_query(user_query, top_n=5):
    # Transform the user query into the same TF-IDF space
    query_vector = vectorizer.transform([user_query])
    
    # Compute cosine similarity between user query and all resources
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    
    # Get top N indices
    top_indices = similarities.argsort()[-top_n:][::-1]
    
    # Return recommended items
    return df[['title', 'url', 'subject', 'difficulty', 'description']].iloc[top_indices].to_dict(orient='records')

if __name__ == "__main__":
    query = "I want to learn about algebra or math equations"
    results = get_recommendations_from_query(query)
    for res in results:
        print(res)




