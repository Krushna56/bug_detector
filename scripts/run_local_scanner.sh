curl -X POST http://localhost:8000/webhook/pr \
     -H "Content-Type: application/json" \
     -d '{
            "repository": { "full_name": "Krushna56/genai-detector" },
            "pull_request": { "number": 4 }
            }'

uvicorn app.main:app --reload