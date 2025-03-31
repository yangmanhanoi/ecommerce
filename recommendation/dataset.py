import random
import os
import numpy as np

# Set the seed for reproducibility
random.seed(42)
np.random.seed(42)

# Create directory if it doesn't exist
file_path = r"C:\DATA\comment_book.txt"
os.makedirs(os.path.dirname(file_path), exist_ok=True)

# Create users and books
users = [f'user_{i}' for i in range(1, 1001)]
books = [f'book_{i}' for i in range(1, 301)]

# More diverse comments with their sentiment labels (1=positive, 0=negative, 0.5=neutral)
comments_with_sentiment = [
    # Positive comments (1)
    ("Amazing book! I couldn't put it down.", 1),
    ("Loved every page of this masterpiece!", 1),
    ("Highly recommend this book to everyone.", 1),
    ("The characters are so well developed, fantastic read.", 1),
    ("One of the best books I've read this year.", 1),
    ("Brilliant storytelling and amazing plot twists.", 1),
    ("This book exceeded all my expectations.", 1),
    ("A perfect five-star read!", 1),
    ("Absolutely worth your time and money.", 1),
    ("The writing style is simply beautiful.", 1),
    
    # Negative comments (0)
    ("Terrible read, wouldn't recommend to anyone.", 0),
    ("Boring storyline with predictable ending.", 0),
    ("Waste of time and money, very disappointed.", 0),
    ("The characters felt flat and undeveloped.", 0),
    ("Couldn't even finish it, very poorly written.", 0),
    ("The plot made no sense at all.", 0),
    ("Would not buy again, complete letdown.", 0),
    ("One of the worst books I've ever read.", 0),
    ("Confusing narrative and too many plot holes.", 0),
    ("The ending was extremely disappointing.", 0),
    
    # Neutral comments (0.5)
    ("It was an okay read, nothing special.", 0.5),
    ("Some parts were good, others not so much.", 0.5),
    ("Decent book but wouldn't read it again.", 0.5),
    ("Neither great nor terrible, just average.", 0.5),
    ("Had potential but didn't quite deliver.", 0.5),
    ("Mixed feelings about this one.", 0.5),
    ("Interesting concept but average execution.", 0.5),
    ("It's fine for a casual read.", 0.5),
    ("Not bad, but not memorable either.", 0.5),
    ("Somewhat entertaining but forgettable.", 0.5)
]

# Generate random comment lengths to add variety
def generate_comment():
    base_comment, sentiment = random.choice(comments_with_sentiment)
    
    # Sometimes add additional phrases to create more variety
    if random.random() < 0.3:
        extras = [
            " I would definitely recommend it.",
            " Not sure if I'd read it again though.",
            " The author is very talented.",
            " The pacing could be better.",
            " Looking forward to more from this author.",
            " The story flows really well.",
            " The ending was unexpected.",
            " The character development was impressive.",
            " The plot was a bit weak.",
            " Great value for the price.",
        ]
        # Make sure we don't contradict the sentiment
        if sentiment == 1:
            valid_extras = [e for e in extras if "weak" not in e and "better" not in e and "Not sure" not in e]
            base_comment += random.choice(valid_extras)
        elif sentiment == 0:
            valid_extras = [e for e in extras if "recommend" not in e and "talented" not in e and "Great" not in e]
            base_comment += random.choice(valid_extras)
        else:
            base_comment += random.choice(extras)
    
    return base_comment, sentiment

# Write to file
with open(file_path, 'w', encoding='utf-8') as file:
    for user in users:
        # Each user has a slight preference for certain types of comments
        user_preference = random.random()  # Higher value means more positive
        
        for _ in range(50):
            book = random.choice(books)
            
            # Adjust selection based on user preference
            if random.random() < user_preference:
                # More likely to select positive comments
                comment, sentiment = generate_comment()
                if user_preference > 0.7 and random.random() < 0.6:
                    while sentiment != 1:
                        comment, sentiment = generate_comment()
            else:
                # More likely to select negative comments
                comment, sentiment = generate_comment()
                if user_preference < 0.3 and random.random() < 0.6:
                    while sentiment != 0:
                        comment, sentiment = generate_comment()
            
            file.write(f"{user}\t{book}\t{comment}\t{sentiment}\n")

print(f"Enhanced dataset generated and stored in {file_path}")