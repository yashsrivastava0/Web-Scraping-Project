from flask import Flask, request, jsonify, render_template_string
from bs4 import BeautifulSoup
import requests
import pandas as pd

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Patent Scraper</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
            color: #333;
        }
        .container {
            margin-top: 50px;
        }
        .spinner-border {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center">Patent Data Scraper</h1>
        <form id="patent-form">
            <div class="mb-3">
                <label for="patent-number" class="form-label">Enter Patent Numbers (comma-separated):</label>
                <input type="text" class="form-control" id="patent-number" name="patent-number" required>
            </div>
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        <table class="table table-bordered table-striped mt-5" id="result-table">
            <thead>
                <tr>
                    <th>Patent Number</th>
                    <th>Title</th>
                    <th>Inventor</th>
                    <th>Assignee</th>
                    <th>Current Assignee</th>
                    <th>Priority Date</th>
                    <th>Application Date</th>
                    <th>Publication Date</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>

    <script>
        document.getElementById('patent-form').addEventListener('submit', async function(event) {
            event.preventDefault();
            const spinner = document.querySelector('.spinner-border');
            const tableBody = document.querySelector('#result-table tbody');
            tableBody.innerHTML = ''; // Clear previous results
            spinner.style.display = 'inline-block';
            const patentNumbers = document.getElementById('patent-number').value;
            const response = await fetch('/get_patent_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ patents: patentNumbers.split(',') }),
            });
            const results = await response.json();
            spinner.style.display = 'none';
            results.forEach(result => {
                const row = `<tr>
                    <td>${result[0]}</td>
                    <td>${result[1]}</td>
                    <td>${result[2]}</td>
                    <td>${result[3]}</td>
                    <td>${result[4]}</td>
                    <td>${result[5]}</td>
                    <td>${result[6]}</td>
                    <td>${result[7]}</td>
                </tr>`;
                tableBody.innerHTML += row;
            });
        });
    </script>
</body>
</html>
'''

def get_patent_data(patent):
    url = "https://patents.google.com/patent/" + str(patent)
    r = requests.get(url)
    data = r.content
    soup = BeautifulSoup(data, 'html.parser')

    title = soup.find('span', attrs={'itemprop': "title"}).text if soup.find('span', attrs={'itemprop': "title"}) else 'N/A'
    prd = soup.find('time', attrs={'itemprop': "priorityDate"}).text if soup.find('time', attrs={'itemprop': "priorityDate"}) else 'N/A'
    flgdate = soup.find('time', attrs={'itemprop': "filingDate"}).text if soup.find('time', attrs={'itemprop': "filingDate"}) else 'N/A'
    pubdate = soup.find('time', attrs={'itemprop': "publicationDate"}).text if soup.find('time', attrs={'itemprop': "publicationDate"}) else 'N/A'
    
    inventor = []
    inv = soup.find_all('dd', attrs={'itemprop': "inventor"})
    for c in range(len(inv)):
        inventor.append(inv[c].string)
    inventors = " | ".join(inventor) if inventor else 'N/A'
    
    assignee = soup.find('dd', attrs={'itemprop': "assigneeOriginal"}).text if soup.find('dd', attrs={'itemprop': "assigneeOriginal"}) else 'N/A'
    current_assignee = soup.find('dd', attrs={'itemprop': "assigneeCurrent"}).text.strip() if soup.find('dd', attrs={'itemprop': "assigneeCurrent"}) else 'N/A'

    data = [patent, title, inventors, assignee, current_assignee, prd, flgdate, pubdate]
    return data

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_patent_data', methods=['POST'])
def get_patent_data_endpoint():
    patents = request.json['patents']
    results = []
    for patent in patents:
        data = get_patent_data(patent)
        results.append(data)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
