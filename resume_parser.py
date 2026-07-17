#Welcome to hirewise AI

import os
import time
from pydantic import BaseModel, Field
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq


env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)
load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
  raise ValueError("API key kha hai bhai?")

client=Groq(api_key=my_api_key)
model= "llama-3.3-70b-versatile"
job_description= """
Software Engineer, Intern
Who we are
About Stripe
Stripe is a financial infrastructure platform for businesses. Millions of companies—from the world’s largest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our mission is to increase the GDP of the internet, and we have a staggering amount of work ahead. That means you have an unprecedented opportunity to put the global economy within everyone’s reach while doing the most important work of your career.

About the team
Our internship program will provide an opportunity to work on meaningful products that will grow the GDP of the internet. Through the internship, you will work with many systems and technologies, gain experience in systems design and testing, and have opportunities to present your work to your team and the wider org. Each intern has a dedicated intern manager, and every project is part of the team’s roadmap and will directly help Stripe’s mission.

What you’ll do
Every internship at Stripe centers around a real, legitimate project that our customers urgently need, touching many parts of our operations and stack. We will support you in shipping it. Yes, you will actually ship it. Some recent projects include rebuilding our statistics aggregation service, building new service discovery systems, and many user facing projects like making it easy to understand error messages on Stripe Checkout. As a Stripe intern, you'll be tackling important projects to increase global commerce, while working alongside exceptional people who insist on doing their best work. You’ll learn from people with high standards who are great at inspiring others to do more and go further. We value technical and personal growth, and see our internship program as a vehicle to foster both.

Responsibilities
Write software that will be used in production, and has meaningful impact to Stripe
Give and receive technical feedback through code reviews or design discussions
Collaborate with other engineers and cross-functional stakeholders to proactively seek and incorporate feedback
Learn quickly by asking great questions, by working with your intern manager and teammates effectively, and by communicating the status of your work clearly
Who you are
We’re looking for someone who meets the minimum requirements to be considered for the role. If you meet these requirements, you are encouraged to apply. The preferred qualifications are a bonus, not a requirement.

Minimum requirements
A strong fundamental understanding of computer science through pursuit of a Bachelor’s, Master’s, or PhD degree in computer science, math, or a related discipline
Some experience and familiarity with programming, either through side projects or classwork. We work mostly in Java, Ruby, JavaScript, Scala, and Go. We believe new programming languages can be learned if the fundamentals and general knowledge are present
Experience from previous internships or other multi-person projects, including open source contributions, that demonstrate evaluating and receiving feedback from mentors, peers, and stakeholders
Ability to learn unfamiliar systems and form an understanding of those systems, through independent research and working with a mentor and subject matter experts
Preferred qualifications
* At least 2 years of university education, or equivalent work experience
One or more areas of specialized knowledge balanced with general skills and knowledge, such as knowing more frontend technologies and, at a high level, how a service handles an HTTP request
Understanding and some experience writing high quality pull requests, with good test coverage, and working knowledge to complete projects with minimal defects
Familiarity with navigating and managing your work in new code bases, with multiple languages
Ability to write clearly to explain your work to stakeholders, team members, and other Stripes
In-office expectations
Office-assigned Stripes in most of our locations are currently expected to spend at least 50% of the time in a given month in their local office or with users. This expectation may vary depending on role, team and location. For example, Stripes in Stripe Delivery Center roles in Mexico City, Mexico, Bengaluru, India, and Dublin, Ireland work 100% from the office. Also, some teams have greater in-office attendance requirements, to appropriately support our users and workflows, which the hiring manager will discuss. This approach helps strike a balance between bringing people together for in-person collaboration and learning from each other, while supporting flexibility when possible.
Pay and benefits
Stripe does not yet include pay ranges in job postings in every country. Stripe strongly values pay transparency and is working toward pay transparency globally.

Office locations

Bengaluru

Team

University

Job type

Intern

Apply for this role 
We look forward to hearing from you
At Stripe, we're looking for people with passion, grit, and integrity. You're encouraged to apply even if your experience doesn't precisely match the job description. Your skills and passion will stand out—and set you apart—especially if your career has taken some extraordinary twists and turns. At Stripe, we welcome diverse perspectives and people who think rigorously and aren't afraid to challenge assumptions. Join us.
"""
class JobD(BaseModel):
  role:str
  required_skills: list[str]
  minimum_experience: float | None
  educational_requirements: list[str]
  responsibilities: list[str]

jobD_schema = JobD.model_json_schema()

system_prompt=f"""
You are an expert HR assistant.

your job is to analyze the resumes and extract relevant structured information from them.

Return only valid JSON matching the schema:
{jobD_schema}
IMPORTANT:
Do NOT return the schema itself.
Do NOT invent information yourself.
Do NOT  return fields like "properties", "title" pr "type".
Fill the schema with actual information from the job description.

if minimum experience is not mmentioned, return Null.
IF information for a list is missing, return an empty list.
"""

user_prompt=f"""
Analyze the following job description: 
{job_description}
"""
message_system={
  "role": "system",
  "content": system_prompt
}
message_user={
  "role": "user",
  "content": user_prompt
}
response_format={
  "type": "json_object"
}

messages=[message_system, message_user]
response=client.chat.completions.create(model=model, messages=messages, response_format=response_format)
answer=response.choices[0].message.content
raw_json=answer
#print(raw_json)

import json
job_data=json.loads(raw_json)
job=JobD(**job_data)

print(job.minimum_experience)
print(job.educational_requirements)

#parse real

class MatchResult(BaseModel):
  score: float
  details: dict

class Experience(BaseModel):
  company: str | None = None
  role: str | None = None
  duration: str | None = None
  description: str | None = None
  skills_used: list[str] = []

class Resume(BaseModel):
  name: str | None = None
  email: str | None = None
  phone: str | None = None

  total_experience : float | None = None

  skills: list[str] = []
  experiences: list[Experience] = []
  education: list[str] = []
  projects: list[str] = []
  certifications: list[str] = []

resume_schema = Resume.model_json_schema()
def final_score(job, resume):
  match_schema = MatchResult.model_json_schema()
  prompt=f"""
  you are an HR recruiter.
  compare the candidate's resume with the job description.

  JOB DESCRIPTION:
  {job.model_dump_json(indent=2)}

  CANDIDATE RESUME:
  {resume.model_dump_json(indent=2)}
  Return JSON matching this schema:
  {match_schema}
  Give me:
  1.Candidate name
  2. Matching Skills
  3. Missing important skills.
  4. Whether experience requirement is met.
  5. Overall match percentage from 0 to 100.
  6. A short final verdict.
  keep the response concise and easy to read.
  """
  message={
    "role": "user",
    "content": prompt
  }
  messages=[message]
  response_format={
    "type": "json_object"
  }
  response=client.chat.completions.create(model=model, messages=messages, response_format=response_format)
  data=json.loads(response.choices[0].message.content)
  return MatchResult(**data)
def parse_resume(resume_text):
  system_prompt=f"""
  You are a expert resume parser.
  extarct information from resume based on its meaning,
  not only based on exact section headings.

  Different resumes may use different headings.
  For example:
  - Experience
  - Professional experience
  - work history
  - employment
  - internships

  these may all contain relevant experience.
  Skills may also appaer in the skills section, work experience, internships or projects.
  Return only Valid JSON matching this schema:
  {resume_schema}  

  Important rules:

  1. Do not invent information.
  2. if a value is not available, return null.
  3. if a list has no information, return an empty list.
  4. include internships, inside experience.
  5. extract skills mentioned across the entire resume.
    """
  user_prompt = f"""
  Parse the following resume:
  {resume_text}
  """
  message_system={
    "role": "system",
    "content": system_prompt
  }
  message_user={
    "role": "system",
    "content": user_prompt
  }
  messages=[message_system, message_user]
  response_format={
    "type": "json_object"
  }
  response=client.chat.completions.create(model=model, messages=messages, response_format=response_format)
  raw_output = response.choices[0].message.content
  data = json.loads(raw_output)
  resume = Resume(**data)
  return resume
  
from pypdf import PdfReader
from docx import Document
def read_pdf(file_path):
  reader = PdfReader(file_path)
  text=""
  for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
      text+= page_text + "\n"
  return text

def read_docx(file_path):
  document = Document(file_path) 
  text= "" 
  for paragraph in document.paragraphs:
    if paragraph.text.strip():
      text += paragraph.text + "\n"
  for table in document.tables:
    for row in table.rows:
      for cell in row.cells:
        if cell.text.strip():
          text += cell.text + "\n"
  return text

def read_resume(file_path):
  if file_path.suffix.lower() == ".pdf":
    return read_pdf(file_path)
  elif file_path.suffix.lower() == ".docx":
    return read_docx(file_path)
  else:
    return None

#now lets do it
resume_folder= Path("resumes")
all_results=[]
for file_path in resume_folder.iterdir():
  if file_path.suffix.lower() not in [".pdf", ".docx"]:
    continue
  print('\nProcessing:', file_path.name)
  resume_text = read_resume(file_path)
  parsed_resume=parse_resume(resume_text)
  time.sleep(5)
  result  = final_score(job, parsed_resume)
  time.sleep(5)
  print("Score:", result.score)
  all_results.append({
    "name": parsed_resume.name,
    "score": result.score,
    "details": result.details
  })
all_results.sort(key=lambda candidate: candidate.get("Score", 0), reverse=True)

top_2 = all_results[:2]
worst_2 = all_results[-2:]

print("TOP 2 CANDIDATES")
for candidate in top_2:
  print(
    candidate["name"],
    "-",
    candidate["score"],"%"
  )

  print(candidate["details"])

print("LOWEST 2 CANDIDATES")
for candidate in worst_2:
  print(
    candidate["name"],"-",
    candidate["score"],"%"
  )
  print(candidate["details"])