import re
import requests
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Optional
import time
from dataclasses import dataclass

@dataclass
class ExtractedContent:
    url: str
    title: str
    content: str
    doc_type: str
    summary: str = ""

class GoogleContentExtractor:
    def __init__(self):
        self.session = requests.Session()
        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
    
    def identify_google_service(self, url: str) -> str:
        """Identify which Google service the URL belongs to"""
        if 'docs.google.com/document' in url:
            return 'docs'
        elif 'docs.google.com/spreadsheets' in url:
            return 'sheets'
        elif 'docs.google.com/presentation' in url:
            return 'slides'
        elif 'drive.google.com' in url:
            return 'drive'
        else:
            return 'unknown'
    
    def convert_to_export_url(self, url: str, service_type: str) -> str:
        """Convert Google service URLs to export/public URLs"""
        try:
            if '/d/' in url:
                doc_id = url.split('/d/')[1].split('/')[0]
            else:
                parsed = urlparse(url)
                if 'id=' in parsed.query:
                    doc_id = parse_qs(parsed.query)['id'][0]
                else:
                    return url
            
            if service_type == 'docs':
                return f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
            elif service_type == 'sheets':
                return f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv"
            elif service_type == 'slides':
                return f"https://docs.google.com/presentation/d/{doc_id}/export/txt"
            elif service_type == 'drive':
                return f"https://drive.google.com/file/d/{doc_id}/view"
        except Exception as e:
            print(f"Error converting URL: {e}")
            return url
        
        return url
    
    def extract_from_docs(self, url: str) -> Optional[ExtractedContent]:
        """Extract content from Google Docs"""
        try:
            doc_id = url.split('/d/')[1].split('/')[0]
            export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
            print(f"Export URL: {export_url}")
            response = self.session.get(export_url)
            print(f"Response status code: {response}")
            if response.status_code == 200:
                content = response.text
                title = f"Google Doc {doc_id[:8]}"
                return ExtractedContent(url, title, content, 'docs')
            else:
                html_url = f"https://docs.google.com/document/d/{doc_id}/export?format=html"
                response = self.session.get(html_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    content = soup.get_text(strip=True)
                    title = soup.find('title').text if soup.find('title') else f"Google Doc {doc_id[:8]}"
                    return ExtractedContent(url, title, content, 'docs')
        except Exception as e:
            print(f"Error extracting from Google Docs: {e}")
        return None
    
    def extract_from_sheets(self, url: str) -> Optional[ExtractedContent]:
        """Extract content from Google Sheets"""
        try:
            doc_id = url.split('/d/')[1].split('/')[0]
            export_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv"
            
            response = self.session.get(export_url)
            if response.status_code == 200:
                content = response.text
                title = f"Google Sheet {doc_id[:8]}"
                return ExtractedContent(url, title, content, 'sheets')
        except Exception as e:
            print(f"Error extracting from Google Sheets: {e}")
        return None
    
    def extract_from_slides(self, url: str) -> Optional[ExtractedContent]:
        """Extract content from Google Slides"""
        try:
            doc_id = url.split('/d/')[1].split('/')[0]
            export_url = f"https://docs.google.com/presentation/d/{doc_id}/export/txt"
            
            response = self.session.get(export_url)
            if response.status_code == 200:
                content = response.text
                title = f"Google Slides {doc_id[:8]}"
                return ExtractedContent(url, title, content, 'slides')
        except Exception as e:
            print(f"Error extracting from Google Slides: {e}")
        return None
    
    def extract_from_drive(self, url: str) -> Optional[ExtractedContent]:
        """Extract content from Google Drive files"""
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                content_div = soup.find('div', {'class': 'ndfHFb-c4YZDc-Wrql6b'})
                if content_div:
                    content = content_div.get_text(strip=True)
                else:
                    content = soup.get_text(strip=True)
                
                title = soup.find('title').text if soup.find('title') else "Google Drive File"
                return ExtractedContent(url, title, content, 'drive')
        except Exception as e:
            print(f"Error extracting from Google Drive: {e}")
        return None
    
    def extract_content(self, url: str) -> Optional[ExtractedContent]:
        """Main method to extract content from any Google service URL"""
        service_type = self.identify_google_service(url)
        print("Service type identified:", service_type)
        if service_type == 'docs':
            return self.extract_from_docs(url)
        elif service_type == 'sheets':
            return self.extract_from_sheets(url)
        elif service_type == 'slides':
            return self.extract_from_slides(url)
        elif service_type == 'drive':
            return self.extract_from_drive(url)
        else:
            print(f"Unsupported service type: {service_type}")
            return None
    
    def simple_summarize(self, text: str, max_sentences: int = 3) -> str:
        """Simple text summarization by extracting key sentences"""
        if not text.strip():
            return "No content to summarize."
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= max_sentences:
            return ' '.join(sentences)
        summary_sentences = []
        
        if sentences:
            summary_sentences.append(sentences[0])  
        
        if len(sentences) > 2:
            longest = max(sentences[1:-1], key=len, default="")
            if longest and longest not in summary_sentences:
                summary_sentences.append(longest)
        
        if len(sentences) > 1 and len(summary_sentences) < max_sentences:
            summary_sentences.append(sentences[-1])  
        
        return '. '.join(summary_sentences) + '.'
    
    def process_urls(self, urls: List[str]) -> List[ExtractedContent]:
        """Process multiple URLs and extract content"""
        results = []
        
        for url in urls:
            print(f"Processing: {url}")
            try:
                extracted = self.extract_content(url)
                if extracted:
                    extracted.summary = self.simple_summarize(extracted.content)
                    results.append(extracted)
                    print(f"✓ Successfully extracted from {extracted.doc_type}")
                else:
                    print(f"✗ Failed to extract content")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"✗ Error processing URL: {e}")
        
        return results

def main():
    # Example usage
    extractor = GoogleContentExtractor()
    
    # Example URLs (replace with your actual URLs)
    urls = [
        "https://docs.google.com/document/d/1dJjqOCX_plQwSfpR6b12yjJOxn_Wi4V3C3oOcO7ByTU/edit?usp=sharing",
        # "https://docs.google.com/spreadsheets/d/your-sheet-id/edit",
        # "https://docs.google.com/presentation/d/your-slides-id/edit",
        # "https://drive.google.com/file/d/your-file-id/view"
    ]
    
    results = extractor.process_urls(urls)
    
    print("\n" + "="*80)
    print("EXTRACTION RESULTS")
    print("="*80)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.title}")
        print(f"   Type: {result.doc_type.upper()}")
        print(f"   URL: {result.url}")
        print(f"   Content Length: {len(result.content)} characters")
        print(f"   Summary: {result.summary}")
        
        if len(result.content) > 500:
            print(f"   Preview: {result.content[:500]}...")
        else:
            print(f"   Full Content: {result.content}")
        print("-" * 80)
    
    results_dict = []
    for result in results:
        results_dict.append({
            'url': result.url,
            'title': result.title,
            'doc_type': result.doc_type,
            'content': result.content,
            'summary': result.summary,
            'content_length': len(result.content)
        })
    
    with open('extracted_content.json', 'w', encoding='utf-8') as f:
        json.dump(results_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to 'extracted_content.json'")
    print(f"Total documents processed: {len(results)}")

if __name__ == "__main__":
    main()