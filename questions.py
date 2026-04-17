"""
questions.py — Accessezy Question Bank
All activity types with Beginner / Intermediate / Advanced levels.
Each question has: question, options, answer, and optional hint.
"""

QUESTIONS = {

    # ─────────────────────────────────────────────
    # 🧩 LOGICAL REASONING
    # ─────────────────────────────────────────────
    "logical": {
        "beginner": [
            {
                "question": "Which shape comes next? 🔴 🔵 🔴 🔵 ?",
                "options": ["🔴", "🔵", "🟢", "🟡"],
                "answer": "🔴",
                "hint": "Look at the pattern — it repeats!"
            },
            {
                "question": "Which number comes next? 1, 2, 3, 4, ?",
                "options": ["6", "5", "7", "8"],
                "answer": "5",
                "hint": "Count up by 1 each time."
            },
            {
                "question": "A dog has 4 legs. A bird has 2 legs. Which has more legs?",
                "options": ["Bird", "Dog", "They are the same", "Neither"],
                "answer": "Dog",
                "hint": "4 is more than 2!"
            },
            {
                "question": "Which comes next? 🌙 ⭐ 🌙 ⭐ ?",
                "options": ["⭐", "🌙", "☀️", "🌈"],
                "answer": "🌙",
                "hint": "The pattern repeats every 2 steps."
            },
            {
                "question": "Tom is taller than Sam. Sam is taller than Leo. Who is the shortest?",
                "options": ["Tom", "Sam", "Leo", "They are all the same"],
                "answer": "Leo",
                "hint": "Think about who is at the bottom of the height order."
            },
        ],
        "intermediate": [
            {
                "question": "Which number comes next? 2, 4, 6, 8, ?",
                "options": ["9", "10", "12", "11"],
                "answer": "10",
                "hint": "Add 2 each time."
            },
            {
                "question": "Find the missing number: 5, 10, 15, ?, 25",
                "options": ["18", "20", "22", "19"],
                "answer": "20",
                "hint": "Count up by 5 each time."
            },
            {
                "question": "All cats are animals. Whiskers is a cat. What is Whiskers?",
                "options": ["A dog", "An animal", "A bird", "A fish"],
                "answer": "An animal",
                "hint": "If all cats are animals, then Whiskers must be..."
            },
            {
                "question": "Which shape is the odd one out? Circle, Square, Triangle, Cylinder",
                "options": ["Circle", "Square", "Triangle", "Cylinder"],
                "answer": "Cylinder",
                "hint": "One of these is 3D, the others are flat (2D)."
            },
            {
                "question": "Which comes next? A, C, E, G, ?",
                "options": ["H", "I", "J", "K"],
                "answer": "I",
                "hint": "Skip one letter each time."
            },
        ],
        "advanced": [
            {
                "question": "If all Bloops are Razzles and all Razzles are Lazzles, are all Bloops definitely Lazzles?",
                "options": ["Yes", "No", "Maybe", "Cannot tell"],
                "answer": "Yes",
                "hint": "Follow the chain: Bloops → Razzles → Lazzles."
            },
            {
                "question": "A train travels 60km in 1 hour. How far does it travel in 90 minutes?",
                "options": ["60km", "80km", "90km", "120km"],
                "answer": "90km",
                "hint": "90 minutes = 1.5 hours. Multiply 60 × 1.5."
            },
            {
                "question": "Which number is next: 1, 1, 2, 3, 5, 8, ?",
                "options": ["10", "11", "12", "13"],
                "answer": "13",
                "hint": "Each number is the sum of the two before it."
            },
            {
                "question": "Cause: It rained heavily. Which is the most likely effect?",
                "options": ["The sun came out", "The streets flooded", "It got warmer", "People went swimming"],
                "answer": "The streets flooded",
                "hint": "Think about what happens to water when it has nowhere to go."
            },
            {
                "question": "Find the odd one out: 121, 144, 169, 196, 200",
                "options": ["121", "144", "196", "200"],
                "answer": "200",
                "hint": "All the others are perfect squares (11², 12², 13², 14²...)"
            },
        ]
    },

    # ─────────────────────────────────────────────
    # 🔢 NUMERICAL ABILITY
    # ─────────────────────────────────────────────
    "numerical": {
        "beginner": [
            {
                "question": "What is 3 + 4?",
                "options": ["6", "7", "8", "9"],
                "answer": "7",
                "hint": "Count 4 steps forward from 3."
            },
            {
                "question": "What is 10 - 3?",
                "options": ["6", "7", "8", "5"],
                "answer": "7",
                "hint": "Start at 10 and count back 3."
            },
            {
                "question": "Which number is bigger: 15 or 51?",
                "options": ["15", "51", "They are equal", "Cannot tell"],
                "answer": "51",
                "hint": "Look at the tens digit first."
            },
            {
                "question": "How many apples? 🍎🍎🍎🍎🍎",
                "options": ["3", "4", "5", "6"],
                "answer": "5",
                "hint": "Count each apple one by one."
            },
            {
                "question": "What is 2 × 3?",
                "options": ["5", "6", "7", "8"],
                "answer": "6",
                "hint": "2 groups of 3."
            },
        ],
        "intermediate": [
            {
                "question": "What is 7 + 8?",
                "options": ["14", "15", "16", "13"],
                "answer": "15",
                "hint": "Try 7 + 7 = 14, then add 1 more."
            },
            {
                "question": "What is 9 × 3?",
                "options": ["27", "21", "24", "26"],
                "answer": "27",
                "hint": "9 × 3 = 9 + 9 + 9."
            },
            {
                "question": "Sarah has 20 sweets. She gives 7 to her friend. How many does she have left?",
                "options": ["11", "12", "13", "14"],
                "answer": "13",
                "hint": "20 take away 7."
            },
            {
                "question": "What is half of 36?",
                "options": ["16", "17", "18", "19"],
                "answer": "18",
                "hint": "Divide 36 by 2."
            },
            {
                "question": "Which is closest to 50? 43, 47, 53, 58",
                "options": ["43", "47", "53", "58"],
                "answer": "47",
                "hint": "Find the difference between each number and 50."
            },
        ],
        "advanced": [
            {
                "question": "A bag of 24 marbles is shared equally among 6 children. How many does each child get?",
                "options": ["3", "4", "5", "6"],
                "answer": "4",
                "hint": "24 ÷ 6 = ?"
            },
            {
                "question": "What is 15% of 200?",
                "options": ["25", "30", "35", "40"],
                "answer": "30",
                "hint": "10% of 200 is 20. 5% is 10. Add them."
            },
            {
                "question": "A book costs £12. It's on sale for 25% off. What is the sale price?",
                "options": ["£8", "£9", "£10", "£11"],
                "answer": "£9",
                "hint": "25% of £12 = £3. Subtract that from £12."
            },
            {
                "question": "What is the next number: 3, 6, 12, 24, ?",
                "options": ["36", "42", "48", "32"],
                "answer": "48",
                "hint": "Each number is doubled."
            },
            {
                "question": "If 3 pens cost £2.40, how much do 5 pens cost?",
                "options": ["£3.60", "£4.00", "£4.20", "£4.80"],
                "answer": "£4.00",
                "hint": "Find the cost of 1 pen first: £2.40 ÷ 3."
            },
        ]
    },

    # ─────────────────────────────────────────────
    # 🧠 MEMORY SKILLS
    # ─────────────────────────────────────────────
    "memory": {
        "beginner": [
            {
                "question": "Remember these: 🍎 🐶 🌟 — Which one was there?",
                "options": ["🐱", "🍎", "🚀", "🌈"],
                "answer": "🍎",
                "hint": "Picture the apple in your mind."
            },
            {
                "question": "The sky is BLUE. The grass is GREEN. What colour is the grass?",
                "options": ["Blue", "Red", "Green", "Yellow"],
                "answer": "Green",
                "hint": "Read the second sentence again."
            },
            {
                "question": "Remember: Cat, Dog, Fish. Which animal was in the middle?",
                "options": ["Cat", "Dog", "Fish", "Bird"],
                "answer": "Dog",
                "hint": "Cat was first, Fish was last..."
            },
            {
                "question": "Remember this number: 7. What was it?",
                "options": ["5", "6", "7", "8"],
                "answer": "7",
                "hint": "It was a single digit number."
            },
            {
                "question": "Emma wore a RED hat and BLUE shoes. What colour were her shoes?",
                "options": ["Red", "Blue", "Green", "Yellow"],
                "answer": "Blue",
                "hint": "Focus on the shoes, not the hat!"
            },
        ],
        "intermediate": [
            {
                "question": "Remember this sequence: 4, 9, 2. What was the second number?",
                "options": ["4", "2", "9", "6"],
                "answer": "9",
                "hint": "The first was 4, the second was..."
            },
            {
                "question": "A story: Jake went to the shop, bought milk and bread, then went home. What did Jake buy FIRST?",
                "options": ["Bread", "Milk", "Eggs", "Butter"],
                "answer": "Milk",
                "hint": "The items were listed in order."
            },
            {
                "question": "Remember: Red, Blue, Green, Yellow. Which colour was THIRD?",
                "options": ["Red", "Blue", "Green", "Yellow"],
                "answer": "Green",
                "hint": "Count along: 1st Red, 2nd Blue, 3rd..."
            },
            {
                "question": "The password is: STAR42. What number is in the password?",
                "options": ["24", "42", "22", "44"],
                "answer": "42",
                "hint": "The letters were STAR, the numbers followed."
            },
            {
                "question": "Remember these shapes: ⭐ 🔶 🔵 ⭐. How many stars were there?",
                "options": ["1", "2", "3", "4"],
                "answer": "2",
                "hint": "Count only the ⭐ symbols."
            },
        ],
        "advanced": [
            {
                "question": "Grid memory: Row 1 had 🍎🍊🍋. Row 2 had 🍇🍓🍒. What was in Row 1, position 2?",
                "options": ["🍎", "🍊", "🍋", "🍇"],
                "answer": "🍊",
                "hint": "Row 1 = Apple, Orange, Lemon. Position 2 is the middle."
            },
            {
                "question": "Story: Anna left home at 8am. She walked for 20 mins, waited 10 mins, then arrived. What time did she arrive?",
                "options": ["8:20am", "8:25am", "8:30am", "8:35am"],
                "answer": "8:30am",
                "hint": "8:00 + 20 mins + 10 mins = ?"
            },
            {
                "question": "Remember this sequence: 7, 3, 9, 1, 5. What was the FOURTH number?",
                "options": ["9", "1", "5", "3"],
                "answer": "1",
                "hint": "Count carefully: 7 (1st), 3 (2nd), 9 (3rd), ? (4th)"
            },
            {
                "question": "Recall: The cat sat on a BLUE mat near the RED door. What colour was the mat?",
                "options": ["Red", "Blue", "Green", "Yellow"],
                "answer": "Blue",
                "hint": "The mat and the door were two different colours."
            },
            {
                "question": "A phone number: 07 - 45 - 23 - 61. What were the last two digits?",
                "options": ["45", "23", "61", "07"],
                "answer": "61",
                "hint": "The number had 4 pairs. The last pair was..."
            },
        ]
    },

    # ─────────────────────────────────────────────
    # 🔷 PATTERN RECOGNITION
    # ─────────────────────────────────────────────
    "pattern": {
        "beginner": [
            {
                "question": "What comes next? 🔴 🔴 🔵 🔴 🔴 🔵 🔴 🔴 ?",
                "options": ["🔴", "🔵", "🟢", "🟡"],
                "answer": "🔵",
                "hint": "The pattern is: two reds, then one blue."
            },
            {
                "question": "What comes next? 1, 3, 1, 3, 1, ?",
                "options": ["1", "3", "2", "4"],
                "answer": "3",
                "hint": "The numbers 1 and 3 alternate."
            },
            {
                "question": "What comes next? 🐱 🐶 🐱 🐶 ?",
                "options": ["🐶", "🐱", "🐰", "🐸"],
                "answer": "🐱",
                "hint": "Cat and Dog take turns."
            },
            {
                "question": "What is missing? A _ C D _ F",
                "options": ["B and E", "B and G", "C and E", "A and E"],
                "answer": "B and E",
                "hint": "These are the letters of the alphabet in order."
            },
            {
                "question": "Which shape completes the pattern? ▲ ■ ▲ ■ ▲ ?",
                "options": ["▲", "■", "●", "★"],
                "answer": "■",
                "hint": "Triangle and square alternate."
            },
        ],
        "intermediate": [
            {
                "question": "What comes next? 2, 4, 8, 16, ?",
                "options": ["24", "28", "32", "18"],
                "answer": "32",
                "hint": "Each number is doubled."
            },
            {
                "question": "Which colour is missing? Red, Orange, Yellow, ?, Blue, Indigo, Violet",
                "options": ["Pink", "Brown", "Green", "Purple"],
                "answer": "Green",
                "hint": "Think of a rainbow — ROY G BIV!"
            },
            {
                "question": "What comes next? AB, CD, EF, ?",
                "options": ["GH", "HI", "GI", "FG"],
                "answer": "GH",
                "hint": "Each pair takes the next two letters of the alphabet."
            },
            {
                "question": "What comes next? 100, 90, 80, 70, ?",
                "options": ["65", "55", "60", "50"],
                "answer": "60",
                "hint": "Subtract 10 each time."
            },
            {
                "question": "Odd one out: 2, 4, 6, 7, 8, 10",
                "options": ["2", "6", "7", "10"],
                "answer": "7",
                "hint": "All the others are even numbers."
            },
        ],
        "advanced": [
            {
                "question": "What comes next? 1, 4, 9, 16, 25, ?",
                "options": ["30", "34", "36", "49"],
                "answer": "36",
                "hint": "These are square numbers: 1², 2², 3², 4², 5²..."
            },
            {
                "question": "What letter is missing? Z, X, V, T, R, ?",
                "options": ["P", "Q", "S", "O"],
                "answer": "P",
                "hint": "Moving backwards through the alphabet, skipping one letter each time."
            },
            {
                "question": "What comes next in this pattern? 3, 5, 8, 13, 21, ?",
                "options": ["29", "32", "34", "25"],
                "answer": "34",
                "hint": "Add the two previous numbers together each time."
            },
            {
                "question": "Which is the odd one out? 8, 27, 64, 100, 125",
                "options": ["8", "27", "100", "125"],
                "answer": "100",
                "hint": "All the others are perfect cubes (2³, 3³, 4³, 5³)."
            },
            {
                "question": "Complete the pattern: AZ, BY, CX, DW, ?",
                "options": ["EV", "EU", "FV", "EW"],
                "answer": "EV",
                "hint": "First letters go forward (A,B,C,D...), second letters go backward (Z,Y,X,W...)."
            },
        ]
    },

    # ─────────────────────────────────────────────
    # 📖 READING COMPREHENSION
    # ─────────────────────────────────────────────
    "reading": {
        "beginner": [
            {
                "question": "Read: 'The cat sat on the mat. The mat was red.' What colour was the mat?",
                "options": ["Blue", "Green", "Red", "Yellow"],
                "answer": "Red",
                "hint": "Look for the colour word in the second sentence."
            },
            {
                "question": "Read: 'Ben has a dog called Max. Max likes to run.' What is the dog's name?",
                "options": ["Ben", "Max", "Bob", "Spot"],
                "answer": "Max",
                "hint": "The dog's name is mentioned after 'called'."
            },
            {
                "question": "Read: 'It was sunny. Mia went to the park and played on the swings.' Where did Mia go?",
                "options": ["School", "Beach", "Park", "Library"],
                "answer": "Park",
                "hint": "The sentence says she went to the..."
            },
            {
                "question": "Read: 'Tom had 3 red balloons. One flew away.' How many did he have left?",
                "options": ["1", "2", "3", "0"],
                "answer": "2",
                "hint": "3 take away 1."
            },
            {
                "question": "Read: 'The bear was big and brown. It lived in the forest.' Where did the bear live?",
                "options": ["Ocean", "Desert", "Forest", "City"],
                "answer": "Forest",
                "hint": "Look for the word after 'lived in'."
            },
        ],
        "intermediate": [
            {
                "question": "Read: 'Lucy felt nervous before her speech. But once she started, she felt much better.' How did Lucy feel at the START?",
                "options": ["Happy", "Nervous", "Excited", "Sad"],
                "answer": "Nervous",
                "hint": "The first sentence tells you her feeling before the speech."
            },
            {
                "question": "Read: 'The library opens at 9am and closes at 6pm. It is closed on Sundays.' How many hours is it open on a weekday?",
                "options": ["7 hours", "8 hours", "9 hours", "6 hours"],
                "answer": "9 hours",
                "hint": "Count from 9am to 6pm."
            },
            {
                "question": "Read: 'Maya loved painting but struggled with maths. Her teacher helped her every Tuesday.' Why did Maya need help?",
                "options": ["She was bad at painting", "She struggled with maths", "She missed school", "She had no friends"],
                "answer": "She struggled with maths",
                "hint": "Look for the word 'struggled'."
            },
            {
                "question": "Read: 'The chef carefully added salt, pepper, and a squeeze of lemon to the soup.' How many ingredients were added?",
                "options": ["2", "3", "4", "1"],
                "answer": "3",
                "hint": "Count: salt, pepper, lemon."
            },
            {
                "question": "Read: 'Despite the heavy rain, the football match continued.' What does 'despite' suggest here?",
                "options": ["The match stopped because of rain", "The match continued even though it rained", "It didn't rain", "The match was cancelled"],
                "answer": "The match continued even though it rained",
                "hint": "'Despite' means 'even though' or 'in spite of'."
            },
        ],
        "advanced": [
            {
                "question": "Read: 'The scientist was elated when her experiment succeeded after months of failure.' What does 'elated' most likely mean?",
                "options": ["Tired", "Confused", "Very happy", "Disappointed"],
                "answer": "Very happy",
                "hint": "Think about how you'd feel after months of failure finally turning to success."
            },
            {
                "question": "Read: 'Although Jake claimed he was fine, his trembling hands told a different story.' What can we infer about Jake?",
                "options": ["Jake was actually fine", "Jake was nervous or scared", "Jake was cold", "Jake was lying about his name"],
                "answer": "Jake was nervous or scared",
                "hint": "Trembling hands are a sign of nerves or fear."
            },
            {
                "question": "Read: 'The village had no electricity, no running water, yet the children laughed and played freely.' What is the main message?",
                "options": ["The village needed help", "Happiness doesn't require material things", "Children shouldn't play outside", "The village was dangerous"],
                "answer": "Happiness doesn't require material things",
                "hint": "Focus on what the children were doing despite having little."
            },
            {
                "question": "Read: 'Every morning, without fail, Mrs. Chen watered her plants before sunrise.' What does this tell us about Mrs. Chen?",
                "options": ["She was lazy", "She was forgetful", "She was disciplined and caring", "She didn't like sleeping"],
                "answer": "She was disciplined and caring",
                "hint": "'Without fail' and 'every morning' suggest consistency and dedication."
            },
            {
                "question": "Read: 'The new law was met with both praise and protest.' What does this tell us?",
                "options": ["Everyone liked the law", "Nobody liked the law", "People had mixed opinions", "The law was cancelled"],
                "answer": "People had mixed opinions",
                "hint": "'Both praise and protest' means two opposite reactions."
            },
        ]
    },

    # ─────────────────────────────────────────────
    # 🎯 ATTENTION & FOCUS
    # ─────────────────────────────────────────────
    "attention": {
        "beginner": [
            {
                "question": "How many letter E's are in this word: ELEPHANT?",
                "options": ["1", "2", "3", "0"],
                "answer": "2",
                "hint": "Go through each letter one at a time: E-L-E-P-H-A-N-T"
            },
            {
                "question": "Which word is spelled differently? CAT, CAT, CAT, COT, CAT",
                "options": ["First CAT", "Second CAT", "COT", "Last CAT"],
                "answer": "COT",
                "hint": "Look very carefully at each word — one has a different vowel."
            },
            {
                "question": "Count the stars: ⭐⭐⭐⭐⭐⭐⭐",
                "options": ["5", "6", "7", "8"],
                "answer": "7",
                "hint": "Count slowly, one at a time."
            },
            {
                "question": "Which number is missing? 1, 2, 3, _, 5, 6",
                "options": ["3", "4", "5", "7"],
                "answer": "4",
                "hint": "What comes between 3 and 5?"
            },
            {
                "question": "Spot the different emoji: 🐶🐶🐶🐱🐶🐶",
                "options": ["Position 1", "Position 3", "Position 4", "Position 6"],
                "answer": "Position 4",
                "hint": "One of these is a cat, not a dog."
            },
        ],
        "intermediate": [
            {
                "question": "How many times does the letter 'S' appear? MISSISSIPPI",
                "options": ["2", "3", "4", "5"],
                "answer": "4",
                "hint": "Go slowly: M-I-S-S-I-S-S-I-P-P-I"
            },
            {
                "question": "Find the odd one out: 12, 21, 31, 13, 11",
                "options": ["12", "21", "31", "11"],
                "answer": "31",
                "hint": "All the others use only the digits 1 and 2."
            },
            {
                "question": "Read carefully: 'Paris is the capital of France. France is in Europe.' Is Paris in Europe?",
                "options": ["Yes", "No", "Maybe", "Cannot tell"],
                "answer": "Yes",
                "hint": "Connect the two facts together."
            },
            {
                "question": "Which two numbers add up to 100? 37, 63, 42, 58, 71",
                "options": ["37 and 63", "42 and 58", "Both pairs", "Neither"],
                "answer": "Both pairs",
                "hint": "Check both: 37+63 and 42+58."
            },
            {
                "question": "How many vowels in the word EDUCATION?",
                "options": ["4", "5", "6", "3"],
                "answer": "5",
                "hint": "Vowels are A, E, I, O, U. Go through each letter."
            },
        ],
        "advanced": [
            {
                "question": "A farmer has 17 sheep. All but 9 run away. How many are left?",
                "options": ["8", "9", "17", "6"],
                "answer": "9",
                "hint": "Read very carefully — 'all but 9' means 9 remain."
            },
            {
                "question": "How many months have 28 days?",
                "options": ["1", "2", "6", "12"],
                "answer": "12",
                "hint": "ALL months have at least 28 days!"
            },
            {
                "question": "If you have a 5-litre bucket and a 3-litre bucket, how do you measure exactly 4 litres?",
                "options": ["Fill the 5L, pour into 3L, empty 3L, pour remaining into 3L, fill 5L, top up 3L — 4L remains in 5L", "Just fill the 4L bucket", "Fill both buckets", "It's impossible"],
                "answer": "Fill the 5L, pour into 3L, empty 3L, pour remaining into 3L, fill 5L, top up 3L — 4L remains in 5L",
                "hint": "Think step by step — use both buckets together."
            },
            {
                "question": "I have two coins totalling 30p. One is not a 20p coin. What are the two coins?",
                "options": ["10p and 20p", "15p and 15p", "5p and 25p", "Two 15p coins"],
                "answer": "10p and 20p",
                "hint": "ONE is not a 20p — but the other one could be!"
            },
            {
                "question": "A clock shows 3:15. What is the angle between the hour and minute hands?",
                "options": ["0°", "7.5°", "90°", "45°"],
                "answer": "7.5°",
                "hint": "At 3:15, the minute hand is at 90°. The hour hand has moved 1/4 of the way from 3 to 4 (7.5° extra)."
            },
        ]
    }
}


def get_questions(activity_name, difficulty, count=5):
    """
    Get a list of questions for a given activity and difficulty.
    Returns up to `count` questions.
    """
    if activity_name not in QUESTIONS:
        return []
    if difficulty not in QUESTIONS[activity_name]:
        difficulty = "beginner"
    questions = QUESTIONS[activity_name][difficulty]
    return questions[:count]


def get_activity_info():
    """Return metadata about each activity for the dashboard."""
    return {
        "logical": {
            "name": "Logical Reasoning",
            "icon": "🧩",
            "description": "Patterns, sorting, cause and effect — train your thinking skills.",
            "color": "#5b8def"
        },
        "numerical": {
            "name": "Numerical Ability",
            "icon": "🔢",
            "description": "Numbers, sums, and word problems to build your maths confidence.",
            "color": "#10b981"
        },
        "memory": {
            "name": "Memory Skills",
            "icon": "🧠",
            "description": "Sequences, stories, and recall challenges to sharpen your memory.",
            "color": "#f59e0b"
        },
        "pattern": {
            "name": "Pattern Recognition",
            "icon": "🔷",
            "description": "Spot the pattern in shapes, colours, letters, and numbers.",
            "color": "#8b5cf6"
        },
        "reading": {
            "name": "Reading Comprehension",
            "icon": "📖",
            "description": "Read short passages and answer questions to improve understanding.",
            "color": "#f87171"
        },
        "attention": {
            "name": "Attention & Focus",
            "icon": "🎯",
            "description": "Spot the difference, find the odd one out, and focus your mind.",
            "color": "#ec4899"
        }
    }
