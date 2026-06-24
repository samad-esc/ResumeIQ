<<<<<<< HEAD
# ResumeIQ

AI-powered resume-to-job match analyzer. Upload your resume and get instant feedback on how well it aligns with a job description.

## Features

- **Job Match Score** - Semantic similarity between resume and job description (0-100%)
- **Skill Analysis** - See matching skills, missing skills, and coverage percentage
- **AI Summary** - Quick analysis of your fit for the role
- **Improvement Suggestions** - 5 actionable tips to strengthen your resume

## Tech Stack

- **Frontend:** Streamlit
- **PDF Parsing:** PyMuPDF
- **Embeddings:** Sentence-Transformers (all-MiniLM-L6-v2)
- **LLM:** Google Gemini API
- **Language:** Python

## Setup

1. Clone repo
```bash
git clone <your-repo>
cd resumeiq
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies
=======
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

### Clone Repositorycle

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

>>>>>>> 0b8f4075deb8965bf816ca3f0ddd6f9b7e9185cb
```bash
pip install -r requirements.txt
```

<<<<<<< HEAD
4. Get Gemini API key
- Go to https://makersuite.google.com/app/apikey
- Create key
- Add to `.env`: `GEMINI_API_KEY=your_key`

5. Run app
=======
---

## Environment Variables

Create a `.env` file in the root directory.

```env
GOOGLE_API_KEY=your_gemini_api_key
```

Get your Gemini API key from Google AI Studio.

---

## Run Application

>>>>>>> 0b8f4075deb8965bf816ca3f0ddd6f9b7e9185cb
```bash
streamlit run app.py
```

<<<<<<< HEAD
Visit `http://localhost:8501`

## How It Works

1. **Upload** your resume (PDF)
2. **Paste** job description
3. **Click** "Analyze Match"
4. Get instant analysis:
   - Job Match Score (semantic similarity + skill coverage)
   - Matching skills
   - Missing skills
   - AI-generated summary
   - Improvement suggestions

## Project Structure

resumeiq/

├── app.py              # Main Streamlit app

├── utils/

│   ├── pdf_parser.py   # PDF text extraction

│   ├── skill_analyzer.py  # Skill extraction & comparison

│   ├── similarity.py   # Job Match Score calculation

│   └── llm.py         # Gemini API integration

├── data/

│   └── skills.json    # Skill database

└── requirements.txt

## How Job Match Score Works

**Formula:** (Semantic Similarity × 60%) + (Skill Coverage × 40%)

- **Semantic Similarity** - Compares resume text with job description using embeddings
- **Skill Coverage** - Percentage of job's skills found in your resume

## Limitations

- Works best with text-based PDFs (not scanned images)
- Skill detection limited to 200+ common skills
- Free Gemini tier has rate limits

## Future Features (V2)

- [ ] Resume rewriting suggestions
- [ ] Multiple job comparison
- [ ] PDF report generation
- [ ] Resume version tracking
- [ ] Support for DOCX/TXT files

## License

MIT
=======
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
>>>>>>> 0b8f4075deb8965bf816ca3f0ddd6f9b7e9185cb
