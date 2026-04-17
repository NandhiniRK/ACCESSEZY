# Accessezy

**Built for neurodivergent learners.**

Accessezy is a specialized web platform designed for educators and parents of neurodivergent learners (particularly those with autism/ASD). It combines behavioral tracking, AI-powered emotional and risk analysis, activity recommendations, and a supportive community forum to provide holistic support and insights.

---

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [AI Modules](#ai-modules)
- [Project Structure](#project-structure)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## Features

### 🎓 For Teachers
- **Student Management**: Create and manage student profiles with age and basic information
- **Behavioral Tracking**: Record free-text behavioral notes, structured observational logs, classroom activities, homework assignments, and learning materials
- **Automated AI Analysis**: Generate emotion distribution, risk levels, wellbeing assessments, and strength highlights automatically
- **Activity Recommendations**: Get personalized ASD-appropriate activity suggestions based on student context
- **Student Profiles**: View comprehensive student profiles with AI-generated insights and historical data
- **Community Moderation**: Pin/delete community posts, view platform activity

### 👨‍👩‍👧 For Parents
- **Child Monitoring**: View linked children with recent notes and activities
- **AI Insights**: Access AI-generated summaries and recommendations for their children
- **Community Participation**: Join discussion forums and connect with other parents
- **Homework & Materials**: View assignments and learning resources

### 🤖 AI-Powered Analytics

Four specialized ML models work together to provide comprehensive insights:

| Module | Model | Output |
|--------|-------|--------|
| **Emotion Classification** | DistilRoBERTa | Classifies student emotional state (Engaged, Calm, Anxious, Needs Support, Overstimulated) |
| **Risk & Wellbeing** | BART (Zero-shot) | Predicts risk level (Low/Medium/High) + identifies concern categories + student strengths |
| **Note Summarization** | BART-CNN | Generates weekly plain-English summaries of behavioral observations |
| **Activity Recommendations** | Sentence-Transformers | Suggests 3 age-appropriate ASD activities using semantic matching |

Optional fine-tuned DistilBERT classifier on GoEmotions dataset for enhanced emotion recognition.

### 💬 Community Forum
- **Categorized Posts**: General, Tips, Announcements
- **Anonymous Posting**: Share insights while maintaining privacy
- **Discussion Threads**: Reply to posts and engage with community
- **Reactions**: Like posts to show support
- **Moderation**: Teachers can manage community content

### 🔐 Admin Dashboard
- **User Statistics**: Track total users by role
- **Activity Metrics**: Monitor notes written, posts created, assignments
- **Top Contributors**: See most active teachers
- **Moderation Tools**: Review and manage community posts
- **Development Tools**: Database reset functionality for testing

---

## Technology Stack

**Backend**: Flask + SQLite3  
**Frontend**: Jinja2 templates with responsive CSS  
**Machine Learning**: PyTorch, HuggingFace Transformers, Sentence-Transformers  
**Authentication**: SHA256 password hashing  

---

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd accessezy
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask transformers torch datasets scikit-learn sentence-transformers python-dotenv
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your configuration:
   ```
   SECRET_KEY=your-random-secret-key
   ADMIN_EMAIL=admin@accessezy.com
   ```

5. **Initialize the database**
   ```bash
   python app.py
   ```
   The database will auto-initialize on first run.

6. **(Optional) Train custom classifier**
   ```bash
   python train_classifier.py --fast  # Fast mode: ~15-20 min
   python train_classifier.py          # Full training: ~2-4 hours
   ```

---

## Configuration

### Environment Variables (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session secret key | `random-string-here` |
| `ADMIN_EMAIL` | Email address that gets admin access | `admin@accessezy.com` |




---

## Usage

### Running the Application
```bash
python app.py
```
Access the application at `http://localhost:5000`

### User Registration Flow
1. **Sign Up**: Fill in name, email, password, and select role (teacher or parent)
2. **Account Created**: Account is immediately ready
3. **Log In**: Use email and password to access the dashboard

### Teacher Workflow
1. **Login** as teacher (email doesn't need to be admin)
2. **Add Student**: Create student profile with name and age
3. **Record Data**: Add behavioral notes, logs, activities, homework, materials
4. **View Analytics**: Click on student profile to see AI-generated insights
5. **Manage Links**: Connect parent accounts to students

### Parent Workflow
1. **Login** as parent
2. **View Children**: See all linked student profiles
3. **Review Insights**: Read AI summaries and recommendations
4. **Community**: Participate in forum discussions

### Admin Dashboard
- Access at `/admin` (requires `admin@accessezy.com` email)
- View platform statistics and moderation tools
- Reset database (development only): `/admin/reset-db`

---

## Architecture

### Application Flow

```
User Registration → Dashboard (Role-Based)
                        ↑
                   [Flask App]
                   ├── Auth Routes (Register, Login, Logout)
                   ├── Teacher Routes
                   ├── Parent Routes
                   ├── Student Profiles → AI Engine
                   ├── Community Routes
                   └── Admin Routes
                        ║
                   [SQLite Database]
                   └── 11 Tables
```

### AI Processing Pipeline (Student Profile View)

```
Teacher Notes/Logs → Emotion Classification
                    ├→ Risk Prediction
                    ├→ Summarization
                    └→ Activity Matching
                        ↓
                    Generate Insights Card
                    (Emotion Distribution, Risk Level, 
                     Wellbeing Tags, Strengths, 
                     Summary, Recommendations)
```

### Key Components

| File | Purpose |
|------|---------|
| `app.py` | Main Flask application with all routes |
| `ai_engine.py` | AI/ML pipeline (emotion, risk, summarization, recommendations) |
| `database.py` | SQLite database schema and initialization |

| `train_classifier.py` | Fine-tune DistilBERT on GoEmotions dataset |
| `evaluate_classifier.py` | Evaluate classifier performance vs. keyword baseline |
| `questions.py` | Activity recommendation question bank (50+ questions) |

---

## Database Schema

### Core Tables

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `users` | User accounts (teachers & parents) | email, password_hash, role, created_at |
| `student_profiles` | Student records | name, age, date_of_birth, created_by (teacher_id), created_at |
| `parent_student_link` | Parent-child relationships | parent_id, student_id |
| `behavioral_notes` | Teacher observations | student_id, note_text, created_at |
| `observational_logs` | Structured weekly logs | student_id, log_date, content, created_at |
| `classroom_activities` | Activity completion records | student_id, activity_name, completion_date |
| `homework` | Assignments | student_id, title, due_date, created_at |
| `learning_materials` | Resources | student_id, title, url, created_at |
| `community_posts` | Forum posts | title, content, author_id, is_anonymous, category, is_pinned, created_at |
| `community_replies` | Post replies | post_id, author_id, reply_text, created_at |
| `post_reactions` | Post likes | post_id, user_id, created_at |

**Total Tables**: 11  
**Initial Database Size**: ~1-2 MB

---

## AI Modules

### 1. Emotion Classification
- **Model**: `j-hartmann/emotion-english-distilroberta-base` (lightweight, ~160MB)
- **Input**: Teacher note text
- **Output**: Distribution across 5 emotions (Engaged, Calm, Anxious, Needs Support, Overstimulated)
- **Use Case**: Real-time emotion trend tracking
- **Latency**: ~500ms per note

### 2. Risk Prediction & Wellbeing
- **Model**: `facebook/bart-large-mnli` (zero-shot classification, ~1.6GB)
- **Input**: Behavioral context (notes + history)
- **Outputs**:
  - Risk Level: Low, Medium, High
  - Concern Categories: Academic Overload, Social Stress, Emotional Regulation, Attendance
  - Student Strengths: Focus, Creativity, Empathy, Memory, Logic, Enthusiasm, Communication, Resilience
- **Latency**: ~2-3s per student profile

### 3. Note Summarization
- **Model**: `facebook/bart-large-cnn` (~1.6GB)
- **Input**: Multiple behavioral notes from a date range
- **Output**: Plain-English weekly summary (3-5 sentences)
- **Use Case**: Quick insight generation for parents/teachers
- **Latency**: ~2s per summary

### 4. Activity Recommendations
- **Model**: `sentence-transformers/all-MiniLM-L6-v2` (~90MB)
- **Input**: Student profile context + activity descriptions
- **Output**: 3 ranked ASD-appropriate activities with reasoning
- **Activity Bank**: 18 curated activities (puzzle games, sensory activities, logical reasoning, etc.)
- **Latency**: ~500ms per student

### Optional: Fine-Tuned Emotion Classifier
- **Model**: DistilBERT fine-tuned on GoEmotions (3 wellbeing categories)
- **Training Data**: ~27K+ examples
- **Training Time**: 15-20 min (fast mode), 2-4 hours (full)
- **Fallback**: Keyword matching if model unavailable
- **Size**: ~270MB

---

## Project Structure

```
accessezy/
├── README.md
├── .env                          # Environment variables (not in git)
├── .env.example                  # Template for environment variables
├── .gitignore
├── app.py                        # Main Flask application
├── ai_engine.py                  # AI/ML pipeline
├── database.py                   # SQLite schema & initialization
├── train_classifier.py           # Fine-tune emotion classifier
├── evaluate_classifier.py        # Evaluate classifier performance
├── questions.py                  # Activity recommendation questions
├── data/
│   ├── evaluation_results.json   # Classifier evaluation metrics
│   └── goemotions_remapped_test.json  # Test dataset
├── models/
│   └── wellbeing_classifier/     # Fine-tuned model & checkpoints
│       ├── config.json
│       ├── model.safetensors
│       ├── tokenizer.json
│       └── checkpoints/          # Training checkpoints
├── static/
│   └── css/
│       └── style.css             # Main stylesheet (design system)
├── templates/                    # Jinja2 HTML templates
│   ├── base.html                 # Base layout
│   ├── index.html                # Home/landing page
│   ├── login.html
│   ├── register.html
│   ├── admin_portal.html
│   ├── teacher_dashboard.html
│   ├── parent_dashboard.html
│   ├── student_profile.html
│   ├── community.html
│   └── post_detail.html
└── venv/                         # Virtual environment

```

---

## Development

### Running Tests/Evaluation

```bash
# Evaluate fine-tuned classifier
python evaluate_classifier.py

# View results
cat data/evaluation_results.json
```

### Training a Custom Classifier

```bash
# Quick training (15-20 minutes)
python train_classifier.py --fast

# Full training (2-4 hours)
python train_classifier.py

# Model checkpoints saved to: models/wellbeing_classifier/checkpoints/
```

### Database Reset (Development Only)

```bash
# Visit in browser
http://localhost:5000/admin/reset-db
```

### Adding New Activities

Edit `questions.py` to add new activities to the recommendation bank. Activities should include:
- Title
- Description
- Age suitability
- Difficulty level
- ASD-specific benefits

---

## Troubleshooting

### Models Not Loading
- **Solution**: Models download automatically on first use (~4.5GB total)
- Ensure sufficient disk space and internet bandwidth
- Check for network/firewall issues

### Slow AI Response Times
- **BART models** take 2-3 seconds per request (normal)
- Consider implementing Redis caching for production
- Use `--fast` mode for classifier training on limited hardware

### SQLite Performance Issues
- Current setup suitable for <100 concurrent users
- For larger deployments, migrate to PostgreSQL
- Consider adding database indexing on frequently queried columns

### Port Already in Use
```bash
# Change port in app.py or use:
python app.py --port 5001
```

### Permission Denied on Files
Ensure virtual environment activation:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

---

## Future Enhancements

- [ ] Redis caching layer for AI results
- [ ] Async task queue (Celery) for model training
- [ ] Mobile app (iOS/Android)
- [ ] Automated alerts for high-risk predictions
- [ ] File upload for learning materials
- [ ] PostgreSQL migration for scalability
- [ ] API rate limiting and metrics
- [ ] Multi-language support
- [ ] Export functionality (PDF reports, CSV data)
- [ ] Integration with learning management systems (LMS)

---

## License

[Specify your license here - e.g., MIT, Apache 2.0]

---

## Support

For issues, questions, or feature requests, please open an issue in the repository.

---

**Accessezy**: Empowering educators and parents to support neurodivergent learners with AI-driven insights.
