from flask import Flask, Response, request, render_template_string
import requests
import io
from PyPDF2 import PdfMerger
import time

app = Flask(__name__)

# Token yahan fix hai
FIXED_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY5NWI0MmJjNzQwZGFkMjQzN2I1NzhlYiIsInJvbGUiOiJzdHVkZW50IiwiaXAiOiIxNTIuNTkuMTguMTM4IiwiZGV2aWNlIjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0NS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiaWF0IjoxNzcyMjY2NTU3LCJleHAiOjE4MzUzMzg1NTd9.vBUp5SWekeBxGy-oIqslR2IRzTpfXxcUqcojVyr5boM"

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'origin': 'https://ebooks.ssccglpinnacle.com',
    'referer': 'https://ebooks.ssccglpinnacle.com/'
}

# --- FRONTEND HTML ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Pinnacle Downloader</title>
    <style>
        body { font-family: sans-serif; text-align: center; margin-top: 50px; background: #f4f4f4; }
        .box { background: white; padding: 30px; display: inline-block; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input { padding: 10px; width: 250px; margin: 10px; border: 1px solid #ddd; }
        button { padding: 10px 20px; background: #28a745; color: white; border: none; cursor: pointer; border-radius: 5px; }
        p { color: red; font-size: 12px; }
    </style>
</head>
<body>
    <div class="box">
        <h2>📚 Pinnacle Book Downloader</h2>
        <input type="text" id="bid" placeholder="Enter Book ID (e.g. 698053...)">
        <br>
        <button onclick="dl()">Download Full PDF</button>
        <p>Note: 200+ chapters wali book Vercel par timeout ho sakti hai.</p>
    </div>
    <script>
        function dl() {
            var id = document.getElementById('bid').value;
            if(!id) return alert("ID dalo bhai!");
            window.location.href = "/fullbook/" + id;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/fullbook/<book_id>')
def full_book(book_id):
    auth_headers = {**HEADERS, 'authorization': f'Bearer {FIXED_TOKEN}'}
    chapters_url = f"https://auth.ssccglpinnacle.com/api/chapters-ebook/{book_id}"
    
    try:
        r = requests.get(chapters_url, headers=auth_headers, timeout=10)
        chapters = r.json()
        merger = PdfMerger()

        # Merge limit for Vercel (Timeout se bachne ke liye)
        for i, chap in enumerate(chapters[:80]): 
            c_id = chap['_id']
            res = requests.get(f'https://auth.ssccglpinnacle.com/api/content-ebook/{c_id}', headers=HEADERS)
            if res.status_code == 200:
                merger.append(io.BytesIO(res.content))
            time.sleep(0.05)

        output = io.BytesIO()
        merger.write(output)
        output.seek(0)
        
        return Response(
            output.read(),
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename=Book_{book_id[-5:]}.pdf'}
        )
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)




