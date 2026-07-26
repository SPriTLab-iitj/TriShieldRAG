# run_demo.ps1 - Start the Streamlit demo in Windows PowerShell
# Run from repository root

Write-Host "Starting RAG-Shield Streamlit App in DEMO Mode..." -ForegroundColor Green
$env:DEMO_MODE="1"
.\.venv\Scripts\python.exe -m streamlit run .\frontend\app.py --server.port 8502
