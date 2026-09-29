from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from app.services.categorization import CategorizationResult

# Small starter training set covering merchants our rules don't catch.
# In a later phase, this can be replaced/extended by learning from
# user-corrected categories stored in the database.
TRAINING_EXAMPLES: list[tuple[str, str]] = [
    ("swiggy instamart", "Groceries"),
    ("licious", "Groceries"),
    ("nature basket", "Groceries"),
    ("cult fit", "Healthcare"),
    ("practo", "Healthcare"),
    ("byjus", "Education"),
    ("unacademy", "Education"),
    ("vedantu", "Education"),
    ("ixigo", "Travel"),
    ("redbus", "Travel"),
    ("housing rent payment", "Rent"),
    ("nobroker rent", "Rent"),
    ("lic premium", "Investment"),
    ("policybazaar", "Investment"),
    ("freelance payment", "Salary"),
    ("consulting fee received", "Salary"),
    ("croma electronics", "Shopping"),
    ("reliance digital", "Shopping"),
    ("bigbasket daily", "Groceries"),
    ("gym membership", "Healthcare"),
]


class MLCategorizer:
    def __init__(self) -> None:
        texts = [text for text, _ in TRAINING_EXAMPLES]
        labels = [label for _, label in TRAINING_EXAMPLES]

        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        X = self.vectorizer.fit_transform(texts)

        self.model = LogisticRegression(max_iter=1000)
        self.model.fit(X, labels)

    def predict(self, merchant: str, description: str, min_confidence: float = 0.35) -> CategorizationResult:
        text = f"{merchant} {description}".lower()
        X = self.vectorizer.transform([text])

        probabilities = self.model.predict_proba(X)[0]
        best_index = probabilities.argmax()
        confidence = float(probabilities[best_index])
        predicted_category = self.model.classes_[best_index]

        if confidence < min_confidence:
            return CategorizationResult(category="Other", source="default", confidence=confidence)

        return CategorizationResult(category=predicted_category, source="ml", confidence=confidence)


# Built once at import time, since training on this tiny fixed set is instant.
# For a bigger dataset later, this would move to a startup event or a cached model file.
ml_categorizer = MLCategorizer()