SkillPath AI – README
=====================

**Author:** Team A 
**Project:** SkillPath — prototype for resume skill extraction, job matching and roadmap generation  

SkillPath is an AI-powered career analysis tool that transforms a user’s resume 
into actionable job recommendations, skill-gap analysis, and a personalised 
career development roadmap.

This project was built using:
- Flask (Python backend)
- HTML/CSS/JS (Frontend)
- OpenAI API (AI-driven parsing & matching)
- FPDF (PDF generation)
- PyPDF2 / pdfplumber (PDF text extraction)

------------------------------------------------------------
1. Project Purpose
------------------------------------------------------------

Many job seekers struggle to understand which roles they qualify for, what their 
skill gaps are, and how to upskill strategically. Traditional job boards only 
match keywords and do not provide personalised development pathways.

SkillPath solves this by offering a guided workflow:
1. Upload resume (PDF)
2. Extract skills, experience, and qualifications
3. Generate AI-powered job match roles
4. Identify missing skills
5. Provide job search links (LinkedIn, Seek, Indeed)
6. Create a downloadable Career Roadmap PDF

------------------------------------------------------------
2. Key Features
------------------------------------------------------------

• Automatic resume parsing (LLM-based)  
• Skill extraction and normalisation  
• Job role matching with match score  
• Missing skill identification  
• Job search link generator  
• Roadmap PDF generation  
• Modern, animated frontend UI  
• Fully structured JSON workflows  

------------------------------------------------------------
3. How It Works
------------------------------------------------------------

/parse  
    - Accepts a PDF resume  
    - Extracts text using PyPDF2/pdfplumber  
    - Sends to OpenAI for structured parsing  

/match  
    - Takes parsed skills  
    - AI generates 5 suggested roles  
    - Each role includes missing skills and an explanation  

/roadmap  
    - Creates a personalised PDF with learning steps  
    - Includes Unicode-safe rendering with DejaVuSans  

Frontend  
    - index.html handles upload  
    - results.html shows analysis, matches, and downloads  

------------------------------------------------------------
4. Requirements
------------------------------------------------------------

Python 3.10+
pip install -r requirements.txt

Environment variable:
OPENAI_API_KEY=your_api_key_here

------------------------------------------------------------
5. Running the Project
------------------------------------------------------------

1. Set up the environment:
   pip install -r requirements.txt

2. Set OpenAI API key in .env

3. Start the server:
   python app.py

4. Open browser and navigate to:
   http://127.0.0.1:5000/

------------------------------------------------------------
6. Folder Structure
------------------------------------------------------------

app.py                 → Flask backend  
analysis.py            → AI logic, parsing, matching, PDF generation  
templates/             → HTML frontend  
uploads/               → Uploaded PDFs  
roadmaps/              → Generated roadmap PDFs  

------------------------------------------------------------
7. Future Improvements
------------------------------------------------------------

• Real job description scraping  
• Interview preparation module  
• ATS resume rewriting  
• Multi-file analysis  
• User accounts + progress tracking  
• Role-specific project generators  

------------------------------------------------------------
8. License
------------------------------------------------------------

For educational use only (prototype).
