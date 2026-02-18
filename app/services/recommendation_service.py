from sqlalchemy.orm import Session
from app.models.book import Book
from app.models.review import Review
from app.services.ai_service import AIService
from typing import List, Dict, Tuple
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.core.logging import get_logger 

#logging configuration
logger = get_logger(__name__)

class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()

    def analyze_sentiment_textblob(self, text: str) -> Dict:
        """
        Analyze sentiment using TextBlob (lightweight, no ML model loading).
        Returns sentiment label and polarity score.
        Polarity ranges from -1 (negative) to 1 (positive).
        """
        if not text:
            return {"label": "NEUTRAL", "score": 0.5}
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Convert polarity to label and normalized score
            if polarity > 0.1:
                label = "POSITIVE"
                score = (polarity + 1) / 2  # Normalize to 0.5-1.0
            elif polarity < -0.1:
                label = "NEGATIVE"
                score = (polarity + 1) / 2  # Normalize to 0.0-0.5
            else:
                label = "NEUTRAL"
                score = 0.5
            
            return {"label": label, "score": score, "polarity": polarity}
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {"label": "NEUTRAL", "score": 0.5}

    def get_books_with_positive_sentiment(self, user_id: int) -> List[Tuple[Book, float]]:
        """
        Get books that user reviewed with positive sentiment.
        Returns list of (book, sentiment_score) tuples.
        """
        user_reviews = self.db.query(Review).filter(Review.user_id == user_id).all()
        
        positive_books = []
        for review in user_reviews:
            book = self.db.query(Book).filter(Book.id == review.book_id).first()
            if not book:
                continue
            
            # Analyze sentiment of review comment
            if review.comment:
                sentiment = self.analyze_sentiment_textblob(review.comment)
                
                # Calculate combined score: sentiment + rating
                sentiment_score = sentiment["score"]
                rating_score = review.rating / 5.0
                combined_score = (sentiment_score * 0.6) + (rating_score * 0.4)
                
                # Only include positive reviews (score > 0.6)
                if combined_score > 0.6:
                    positive_books.append((book, combined_score))
        
        return positive_books

    def get_similar_books(self, liked_books: List[Tuple[Book, float]], all_books: List[Book]) -> List[Tuple[Book, float]]:
        """
        Find books similar to liked books using TF-IDF and cosine similarity.
        Returns list of (book, similarity_score) tuples.
        """
        if not liked_books:
            return []
        
        # Extract liked book IDs
        liked_book_ids = {book.id for book, _ in liked_books}
        
        # Get candidate books (not already liked)
        candidate_books = [book for book in all_books if book.id not in liked_book_ids]
        
        if not candidate_books:
            return []
        
        # Prepare text representations
        liked_texts = []
        for book, _ in liked_books:
            text = f"{book.title} {book.author} {book.description or ''} {book.summary or ''}"
            liked_texts.append(text)
        
        candidate_texts = []
        for book in candidate_books:
            text = f"{book.title} {book.author} {book.description or ''} {book.summary or ''}"
            candidate_texts.append(text)
        
        # Calculate TF-IDF vectors
        try:
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            all_texts = liked_texts + candidate_texts
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            
            # Calculate similarity between liked and candidate books
            liked_vectors = tfidf_matrix[:len(liked_texts)]
            candidate_vectors = tfidf_matrix[len(liked_texts):]
            
            # Compute cosine similarity
            similarities = cosine_similarity(candidate_vectors, liked_vectors)
            
            # Get max similarity for each candidate book
            max_similarities = np.max(similarities, axis=1)
            
            # Create list of similar books with scores
            similar_books = []
            for idx, book in enumerate(candidate_books):
                similarity_score = float(max_similarities[idx])
                similar_books.append((book, similarity_score))
            
            return similar_books
        
        except Exception as e:
            logger.error(f"Similarity calculation error: {e}")
            # Fallback: return candidates with neutral score
            return [(book, 0.5) for book in candidate_books]

    def rank_by_score(self, books_with_scores: List[Tuple[Book, float]]) -> List[Dict]:
        """
        Rank books by their scores and return formatted recommendations.
        """
        # Sort by score (descending)
        ranked = sorted(books_with_scores, key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for book, score in ranked:
            recommendations.append({
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "description": book.description,
                "summary": book.summary,
                "score": round(score, 3),
                "reason": f"Similar to books you enjoyed (match: {int(score * 100)}%)"
            })
        
        return recommendations

    async def get_recommendations(self, user_id: int, limit: int = 5) -> List[Dict]:
        """
        Main recommendation function following the pattern:
        1. Get books with positive sentiment from user reviews
        2. Find similar books to those liked books
        3. Rank by similarity score
        4. Return top N recommendations
        
        If user has no reviews, return all available books.
        """
        # Fetch all books from database
        all_books = self.db.query(Book).all()
        
        # Fetch user's reviews
        user_reviews = self.db.query(Review).filter(Review.user_id == user_id).all()
        
        # If user has no reviews, return all books
        if not user_reviews:
            return [
                {
                    "id": book.id,
                    "title": book.title,
                    "author": book.author,
                    "description": book.description,
                    "summary": book.summary,
                    "score": 0.5,
                    "reason": "Explore our collection"
                }
                for book in all_books[:limit]
            ]
        
        # Step 1: Get books with positive sentiment
        liked_books = self.get_books_with_positive_sentiment(user_id)
        
        # If no positive reviews, return all books
        if not liked_books:
            return [
                {
                    "id": book.id,
                    "title": book.title,
                    "author": book.author,
                    "description": book.description,
                    "summary": book.summary,
                    "score": 0.5,
                    "reason": "Try something new"
                }
                for book in all_books[:limit]
            ]
        
        # Step 2: Get similar books to liked books
        similar_books = self.get_similar_books(liked_books, all_books)
        
        # Step 3: Rank by score
        ranked_recommendations = self.rank_by_score(similar_books)
        
        # Step 4: Return top N recommendations
        return ranked_recommendations[:limit]

    async def get_genai_reviews_summary(self, user_id: int) -> Dict:
        # Fetch all reviews by the user
        user_reviews = self.db.query(Review).filter(Review.user_id == user_id).all()
        
        if not user_reviews:
            return {
                "user_id": user_id,
                "total_reviews": 0,
                "average_rating": None,
                "summary": "No reviews found for this user.",
                "sentiment_breakdown": {"positive": 0, "neutral": 0, "negative": 0},
                "reviewed_books": []
            }
        
        # Collect review data and analyze sentiment
        reviews_data = []
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        total_rating = 0
        
        for review in user_reviews:
            book = self.db.query(Book).filter(Book.id == review.book_id).first()
            book_title = book.title if book else "Unknown Book"
            book_author = book.author if book else "Unknown Author"
            
            # Analyze sentiment of the comment
            sentiment = self.analyze_sentiment_textblob(review.comment or "")
            sentiment_label = sentiment["label"].lower()
            sentiment_counts[sentiment_label] = sentiment_counts.get(sentiment_label, 0) + 1
            
            total_rating += review.rating
            
            reviews_data.append({
                "book_title": book_title,
                "book_author": book_author,
                "rating": review.rating,
                "comment": review.comment or "",
                "sentiment": sentiment_label
            })
        
        # Calculate average rating
        average_rating = round(total_rating / len(user_reviews), 2)
        
        # Prepare text for AI summarization
        reviews_text = "\n".join([
            f"- Book: '{r['book_title']}' by {r['book_author']}, Rating: {r['rating']}/5, Comment: {r['comment']}"
            for r in reviews_data
        ])
        
        # Generate AI summary
        try:
            ai_prompt = f"""Analyze and summarize the following book reviews from a single user. 
                            Provide insights about their reading preferences, favorite genres/authors, and overall sentiment.
                            Keep the summary concise (2-3 paragraphs).

                            User Reviews:
                            {reviews_text}

                            Average Rating: {average_rating}/5
                            Total Reviews: {len(user_reviews)}
                            Sentiment Breakdown: {sentiment_counts['positive']} positive, {sentiment_counts['neutral']} neutral, {sentiment_counts['negative']} negative"""

            ai_summary = await self.ai_service.summarize(ai_prompt)
            
            if not ai_summary:
                ai_summary = self._generate_fallback_summary(reviews_data, average_rating, sentiment_counts)
        except Exception as e:
            logger.error(f"AI summarization failed: {e}")
            ai_summary = self._generate_fallback_summary(reviews_data, average_rating, sentiment_counts)
        
        return {
            "user_id": user_id,
            "total_reviews": len(user_reviews),
            "average_rating": average_rating,
            "summary": ai_summary,
            "sentiment_breakdown": sentiment_counts,
            "reviewed_books": [
                {"title": r["book_title"], "author": r["book_author"], "rating": r["rating"]}
                for r in reviews_data
            ]
        }

    def _generate_fallback_summary(self, reviews_data: List[Dict], average_rating: float, sentiment_counts: Dict) -> str:
        """
        Generate a basic summary when AI service is unavailable.
        """
        total = len(reviews_data)
        positive_pct = round((sentiment_counts["positive"] / total) * 100) if total > 0 else 0
        
        # Find most reviewed authors
        authors = {}
        for r in reviews_data:
            author = r["book_author"]
            authors[author] = authors.get(author, 0) + 1
        
        top_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)[:3]
        authors_str = ", ".join([a[0] for a in top_authors]) if top_authors else "various authors"
        
        return (
            f"This user has reviewed {total} book(s) with an average rating of {average_rating}/5. "
            f"Approximately {positive_pct}% of their reviews express positive sentiment. "
            f"They have shown interest in books by {authors_str}."
        )