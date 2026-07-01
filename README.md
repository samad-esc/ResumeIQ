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
```bash
pip install -r requirements.txt
```

4. Get Gemini API key
- Go to https://makersuite.google.com/app/apikey
- Create key
- Add to `.env`: `GEMINI_API_KEY=your_key`

5. Run app
```bash
streamlit run app.py
```

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
