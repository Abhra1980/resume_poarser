"""
Tools for CrewAI agents
"""
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
from crew_app.file_tools.file_loader import detect_and_extract, extract_text_from_pdf, extract_text_from_docx

class FileReaderInput(BaseModel):
    """Input schema for FileReaderTool"""
    file_path: str = Field(..., description="Path to the file to read")

class FileReaderTool(BaseTool):
    name: str = "file_reader"
    description: str = "Read and extract text from PDF, DOCX, or TXT files"
    args_schema: Type[BaseModel] = FileReaderInput

    def _run(self, file_path: str) -> str:
        """Read file and extract text"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    file_bytes = f.read()
                ext, text = detect_and_extract(file_path, file_bytes)
                return f"File type: {ext}\nExtracted text:\n{text}"
            else:
                return f"File not found: {file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

class TextProcessorInput(BaseModel):
    """Input schema for TextProcessorTool"""
    text: str = Field(..., description="Text to process and clean")

class TextProcessorTool(BaseTool):
    name: str = "text_processor"
    description: str = "Clean and normalize text content, remove artifacts and format consistently"
    args_schema: Type[BaseModel] = TextProcessorInput

    def _run(self, text: str) -> str:
        """Process and clean text"""
        try:
            # Basic text cleaning
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Remove extra whitespace
                line = line.strip()
                
                # Skip empty lines and page numbers
                if not line or line.isdigit() or len(line) < 3:
                    continue
                    
                # Normalize bullet points
                if line.startswith('•') or line.startswith('*') or line.startswith('-'):
                    line = '- ' + line[1:].strip()
                
                cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
        except Exception as e:
            return f"Error processing text: {str(e)}"

class ATSAnalyzerInput(BaseModel):
    """Input schema for ATSAnalyzerTool"""
    resume_text: str = Field(..., description="Resume text to analyze")
    job_description: str = Field(..., description="Job description to compare against")

class ATSAnalyzerTool(BaseTool):
    name: str = "ats_analyzer"
    description: str = "Analyze resume for ATS compatibility and keyword matching"
    args_schema: Type[BaseModel] = ATSAnalyzerInput

    def _run(self, resume_text: str, job_description: str) -> str:
        """Analyze ATS compatibility with enhanced keyword matching"""
        try:
            import re
            
            # Clean and extract meaningful keywords
            def extract_keywords(text):
                # Convert to lowercase and extract words
                words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
                
                # Filter out common words
                stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'this', 'that', 'they', 'them', 'their', 'there', 'then', 'than', 'when', 'where', 'who', 'what', 'why', 'how', 'can', 'may', 'must', 'shall', 'should', 'would', 'could', 'might', 'need', 'want', 'like', 'know', 'think', 'see', 'get', 'make', 'take', 'come', 'go', 'say', 'tell', 'ask', 'give', 'put', 'set', 'run', 'move', 'live', 'feel', 'show', 'try', 'call', 'work', 'seem', 'leave', 'keep', 'let', 'begin', 'help', 'talk', 'turn', 'start', 'might', 'find', 'look', 'right', 'new', 'first', 'last', 'long', 'great', 'little', 'own', 'other', 'old', 'right', 'big', 'high', 'different', 'small', 'large', 'next', 'early', 'young', 'important', 'few', 'public', 'bad', 'same', 'able'}
                
                return [word for word in words if word not in stop_words and len(word) > 2]
            
            # Extract technical and professional keywords
            jd_keywords = set(extract_keywords(job_description))
            resume_keywords = set(extract_keywords(resume_text))
            
            # Find matches and gaps
            matching = jd_keywords.intersection(resume_keywords)
            missing = jd_keywords - resume_keywords
            
            # Calculate match percentage
            match_rate = (len(matching) / len(jd_keywords) * 100) if jd_keywords else 0
            
            # Prioritize missing technical terms
            critical_missing = [word for word in missing if any(tech in word for tech in ['python', 'machine', 'learning', 'data', 'ai', 'model', 'algorithm', 'analysis', 'engineer', 'developer', 'software', 'technical', 'programming', 'coding', 'development', 'framework', 'database', 'cloud', 'system'])][:5]
            
            if not critical_missing:
                critical_missing = list(missing)[:5]
            
            # Calculate ATS score based on multiple factors
            keyword_score = min(match_rate / 20, 5)  # 20% match = score of 5
            
            # Check for standard sections
            sections = ['summary', 'skills', 'experience', 'education']
            section_score = sum(1 for section in sections if section in resume_text.lower()) * 1.25
            
            # Check for quantified achievements (numbers/percentages)
            import re
            numbers = len(re.findall(r'\d+%|\d+\+|\d+ years|\d+ million|\d+ billion', resume_text))
            metrics_score = min(numbers / 3, 5)  # 3+ metrics = score of 5
            
            # Check for action verbs
            action_verbs = ['led', 'developed', 'implemented', 'achieved', 'managed', 'created', 'designed', 'built', 'optimized', 'enhanced', 'delivered', 'established', 'spearheaded', 'orchestrated']
            verb_count = sum(1 for verb in action_verbs if verb in resume_text.lower())
            verb_score = min(verb_count / 5, 5)  # 5+ verbs = score of 5
            
            # Overall ATS score (0-100)
            overall_score = (keyword_score + section_score + metrics_score + verb_score + 5) * 4  # Max 100
            overall_score = min(overall_score, 100)
            
            return f"""ATS ANALYSIS RESULTS:
Overall ATS Score: {overall_score:.0f}/100

BREAKDOWN:
- Keyword Match: {keyword_score:.1f}/5 ({match_rate:.1f}% match rate)
- Section Structure: {section_score:.1f}/5
- Quantified Metrics: {metrics_score:.1f}/5 ({numbers} metrics found)
- Action Verbs: {verb_score:.1f}/5 ({verb_count} strong verbs)
- Format Quality: 5/5

CRITICAL MISSING KEYWORDS: {', '.join(critical_missing[:5])}

OPTIMIZATION STRATEGY:
1. Add these keywords in SUMMARY: {', '.join(critical_missing[:3])}
2. Include more quantified achievements (target 5+ metrics)
3. Use stronger action verbs: {', '.join([v for v in action_verbs if v not in resume_text.lower()][:3])}
4. Repeat key terms 2-3 times throughout resume

QUICK WINS:
- Place "{job_title}" keywords in first paragraph
- Add percentage improvements to bullet points
- Use both acronyms and full terms (AI/Artificial Intelligence)
- Structure: SUMMARY → SKILLS → EXPERIENCE → EDUCATION"""
            
        except Exception as e:
            return f"Enhanced ATS Analysis Error: {str(e)}"

# Export tools for use in agents
def get_file_reader_tool():
    return FileReaderTool()

def get_text_processor_tool():
    return TextProcessorTool()

def get_ats_analyzer_tool():
    return ATSAnalyzerTool()
