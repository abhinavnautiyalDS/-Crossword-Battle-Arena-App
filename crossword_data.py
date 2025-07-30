import random

class CrosswordPuzzleManager:
    def __init__(self):
        self.puzzles = {
            "easy": [
                {
                    "title": "Basic Letters",
                    "size": 5,
                    "clues": [
                        {"id": 1, "clue": "First letter of the alphabet", "answer": "A", "points": 5, "position": (0, 0), "direction": "across", "length": 1},
                        {"id": 2, "clue": "Feline pet", "answer": "CAT", "points": 10, "position": (1, 0), "direction": "across", "length": 3},
                        {"id": 3, "clue": "Man's best friend", "answer": "DOG", "points": 10, "position": (2, 0), "direction": "across", "length": 3},
                        {"id": 4, "clue": "Opposite of hot", "answer": "COLD", "points": 15, "position": (3, 0), "direction": "across", "length": 4},
                        {"id": 5, "clue": "Large body of water", "answer": "SEA", "points": 10, "position": (4, 0), "direction": "across", "length": 3},
                    ]
                },
                {
                    "title": "Simple Words",
                    "size": 5,
                    "clues": [
                        {"id": 1, "clue": "Yellow fruit", "answer": "LEMON", "points": 15, "position": (0, 0), "direction": "across", "length": 5},
                        {"id": 2, "clue": "Red fruit", "answer": "APPLE", "points": 15, "position": (1, 0), "direction": "across", "length": 5},
                        {"id": 3, "clue": "Orange vegetable", "answer": "CARROT", "points": 20, "position": (2, 0), "direction": "across", "length": 5},
                        {"id": 4, "clue": "Round object", "answer": "BALL", "points": 12, "position": (3, 0), "direction": "across", "length": 4},
                        {"id": 5, "clue": "Flying animal", "answer": "BIRD", "points": 12, "position": (4, 0), "direction": "across", "length": 4},
                    ]
                }
            ],
            "medium": [
                {
                    "title": "Nature & Animals",
                    "size": 7,
                    "clues": [
                        {"id": 1, "clue": "King of the jungle", "answer": "LION", "points": 15, "position": (0, 0), "direction": "across", "length": 4},
                        {"id": 2, "clue": "Tall African mammal", "answer": "GIRAFFE", "points": 25, "position": (1, 0), "direction": "across", "length": 7},
                        {"id": 3, "clue": "Largest mammal", "answer": "WHALE", "points": 20, "position": (2, 0), "direction": "across", "length": 5},
                        {"id": 4, "clue": "Black and white bear", "answer": "PANDA", "points": 20, "position": (3, 0), "direction": "across", "length": 5},
                        {"id": 5, "clue": "Striped horse-like animal", "answer": "ZEBRA", "points": 20, "position": (4, 0), "direction": "across", "length": 5},
                        {"id": 6, "clue": "Largest land animal", "answer": "ELEPHANT", "points": 30, "position": (5, 0), "direction": "across", "length": 7},
                        {"id": 7, "clue": "Primate closest to humans", "answer": "CHIMP", "points": 20, "position": (6, 0), "direction": "across", "length": 5},
                    ]
                },
                {
                    "title": "Science & Technology",
                    "size": 8,
                    "clues": [
                        {"id": 1, "clue": "Device for communication", "answer": "PHONE", "points": 20, "position": (0, 0), "direction": "across", "length": 5},
                        {"id": 2, "clue": "Personal computing device", "answer": "LAPTOP", "points": 25, "position": (1, 0), "direction": "across", "length": 6},
                        {"id": 3, "clue": "Global network", "answer": "INTERNET", "points": 30, "position": (2, 0), "direction": "across", "length": 8},
                        {"id": 4, "clue": "Artificial intelligence", "answer": "ROBOT", "points": 25, "position": (3, 0), "direction": "across", "length": 5},
                        {"id": 5, "clue": "Space vehicle", "answer": "ROCKET", "points": 25, "position": (4, 0), "direction": "across", "length": 6},
                        {"id": 6, "clue": "Energy from the sun", "answer": "SOLAR", "points": 22, "position": (5, 0), "direction": "across", "length": 5},
                        {"id": 7, "clue": "Study of matter and energy", "answer": "PHYSICS", "points": 28, "position": (6, 0), "direction": "across", "length": 7},
                    ]
                }
            ],
            "hard": [
                {
                    "title": "Advanced Vocabulary",
                    "size": 10,
                    "clues": [
                        {"id": 1, "clue": "Existing in thought but not reality", "answer": "ABSTRACT", "points": 35, "position": (0, 0), "direction": "across", "length": 8},
                        {"id": 2, "clue": "State of being uncertain", "answer": "AMBIGUITY", "points": 40, "position": (1, 0), "direction": "across", "length": 9},
                        {"id": 3, "clue": "Characterized by vulgar excess", "answer": "OSTENTATIOUS", "points": 50, "position": (2, 0), "direction": "across", "length": 10},
                        {"id": 4, "clue": "Having mixed feelings", "answer": "AMBIVALENT", "points": 45, "position": (3, 0), "direction": "across", "length": 10},
                        {"id": 5, "clue": "Showing deep respect", "answer": "REVERENT", "points": 35, "position": (4, 0), "direction": "across", "length": 8},
                        {"id": 6, "clue": "Lacking substance or worth", "answer": "VACUOUS", "points": 32, "position": (5, 0), "direction": "across", "length": 7},
                        {"id": 7, "clue": "Tending to argue", "answer": "CONTENTIOUS", "points": 48, "position": (6, 0), "direction": "across", "length": 10},
                        {"id": 8, "clue": "Marked by luxury", "answer": "SUMPTUOUS", "points": 42, "position": (7, 0), "direction": "across", "length": 9},
                    ]
                },
                {
                    "title": "Literature & Arts",
                    "size": 10,
                    "clues": [
                        {"id": 1, "clue": "Author of '1984'", "answer": "ORWELL", "points": 30, "position": (0, 0), "direction": "across", "length": 6},
                        {"id": 2, "clue": "Shakespeare's tragic prince", "answer": "HAMLET", "points": 30, "position": (1, 0), "direction": "across", "length": 6},
                        {"id": 3, "clue": "Painter of 'Starry Night'", "answer": "VANGOGH", "points": 35, "position": (2, 0), "direction": "across", "length": 7},
                        {"id": 4, "clue": "Epic poem by Homer", "answer": "ODYSSEY", "points": 32, "position": (3, 0), "direction": "across", "length": 7},
                        {"id": 5, "clue": "Dante's divine journey", "answer": "COMEDY", "points": 28, "position": (4, 0), "direction": "across", "length": 6},
                        {"id": 6, "clue": "Mozart's final opera", "answer": "REQUIEM", "points": 35, "position": (5, 0), "direction": "across", "length": 7},
                        {"id": 7, "clue": "Michelangelo's ceiling", "answer": "SISTINE", "points": 35, "position": (6, 0), "direction": "across", "length": 7},
                        {"id": 8, "clue": "Beethoven's ninth", "answer": "SYMPHONY", "points": 38, "position": (7, 0), "direction": "across", "length": 8},
                    ]
                }
            ]
        }
    
    def get_puzzle(self, difficulty="medium"):
        """Get a random puzzle of the specified difficulty"""
        if difficulty not in self.puzzles:
            difficulty = "medium"
        
        return random.choice(self.puzzles[difficulty])
    
    def get_puzzle_by_category(self, difficulty, category):
        """Get a puzzle by difficulty and category"""
        puzzles = self.puzzles.get(difficulty, self.puzzles["medium"])
        category_puzzles = [p for p in puzzles if category.lower() in p["title"].lower()]
        return random.choice(category_puzzles) if category_puzzles else random.choice(puzzles)
