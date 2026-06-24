# ResumeIQ 🎯

An AI-powered Resume-to-Job Match Analyzer that helps job seekers evaluate how well their resume aligns with a job description using skill matching, semantic similarity, and AI-generated feedback.

## Features

### 📄 Resume Parsing

* Upload resumes in PDF format
* Extract text automatically using PyPDF2/PyMuPDF
* Handle multi-page resumes

### 🎯 Job Match Analysis

* Skill extraction from resumes and job descriptions
* Matching and missing skills identification
* Skill coverage percentage calculation

### 🤖 AI-Powered Insights

* Resume summary generation
* Personalized improvement suggestions
* Job-specific recommendations using Gemini AI

### 📊 Scoring Engine

* Semantic similarity scoring using Sentence Transformers
* Skill coverage analysis
* Overall Job Match Score (0-100)

### 🎨 Interactive Dashboard

* Clean Streamlit interface
* Visual skill comparison
* Progress indicators and analytics
* Responsive layout

---

## Tech Stack

### Frontend

* Streamlit

### AI / Machine Learning

* Sentence Transformers
* Scikit-learn
* Google Gemini API

### Backend Logic

* Python
* PyPDF2
* PyMuPDF

### Utilities

* python-dotenv

---

## Project Structure

```text
resumeiq/
│
├── app.py
├── requirements.txt
├── .env
├── README.md
│
├── data/
│   └── skills.json
│
└── utils/
    ├── __init__.py
    ├── pdf_parser.py
    ├── skill_analyzer.py
    ├── similarity.py
    └── llm.py
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/resumeiq.git
cd resumeiq
```

### Create Virtual Environment

#### Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the root directory.

```env
GOOGLE_API_KEY=your_gemini_api_key
```

Get your Gemini API key from Google AI Studio.

---

## Run Application

```bash
streamlit run app.py
```

The application will start at:

```text
http://localhost:8501
```

---

## How It Works

1. Upload a PDF resume.
2. Paste a job description.
3. Click **Analyze Match**.
4. ResumeIQ will:

   * Extract resume text
   * Identify matching skills
   * Detect missing skills
   * Calculate a job match score
   * Generate AI-powered feedback

---

## Sample Output

### Match Score

* Overall Resume Match: 78%

### Matching Skills

* Python
* Machine Learning
* Pandas
* NumPy
* Git

### Missing Skills

* TensorFlow
* PyTorch
* SQL
* Deep Learning

### AI Suggestions

* Add Docker experience
* Include project impact metrics
* Highlight relevant ML projects
* Tailor resume summary to job description

---

## Future Improvements

* ATS Score Analysis
* Resume Keyword Optimization
* PDF Report Generation
* Multi-Job Comparison
* Recruiter Dashboard
* FastAPI Backend
* React Frontend
* PostgreSQL Integration

---

## Author

**Samad Mirza**

B.Tech, Electronics & Communication Engineering
National Institute of Technology Silchar

---

## License

MIT License

Feel free to use, modify, and contribute.
