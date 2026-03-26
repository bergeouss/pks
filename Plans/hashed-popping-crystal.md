---
task: Add Document Ingestion UI with File Upload
slug: add-ingestion-ui
effort: medium
phase: plan
---

## Context

PKS (Personal Knowledge Synthesizer) has a complete backend ingestion pipeline but **no frontend UI to use it**. Users cannot ingest documents (PDF, TXT, DOCX, images) through the web interface - only through the browser extension or file watcher. This is a critical missing feature for a document chat application.

**Problem**: No way to upload documents through the web UI
**Solution**: Add an Ingest page with URL, text, and file upload capabilities
**Outcome**: Users can ingest PDF, DOCX, TXT, images, and URLs through the web interface

## Implementation Plan

### Phase 1: Backend File Upload Endpoint

**File**: `/home/fr33m1nd/dev/pks/backend/app/api/routes/ingestion.py`

Add file upload endpoint:
```python
@router.post("/upload", response_model=IngestResponse)
async def upload_file(
    file: UploadFile = File(...),
    metadata: Optional[str] = None  # JSON string
):
    """Upload and ingest a file (PDF, DOCX, TXT, images)"""
```

- Use `tempfile.NamedTemporaryFile` to save uploaded file
- Call existing `ingestion_service.ingest_file(tmp_path, metadata)`
- Clean up temp file after processing
- Support file types: `.pdf`, `.docx`, `.txt`, `.md`, `.png`, `.jpg`, `.jpeg`

### Phase 2: Image OCR Support

**File**: `/home/fr33m1nd/dev/pks/backend/app/services/parser_service.py`

Add image OCR using Gemini Vision (already have API key):
```python
async def _parse_image(self, file_path: str) -> str:
    """Extract text from image using Gemini Vision"""
    import google.generativeai as genai
    from PIL import Image

    model = genai.GenerativeModel('gemini-1.5-flash')
    image = Image.open(file_path)
    response = await model.generate_content_async(
        ["Extract all text from this image:", image]
    )
    return response.text
```

**File**: `/home/fr33m1nd/dev/pks/backend/requirements.txt`
Add: `pillow==10.4.0`

### Phase 3: Frontend Ingest Page

**New File**: `/home/fr33m1nd/dev/pks/frontend/src/app/ingest/page.tsx`

Create page with three ingestion methods:
1. **URL Input**: For web pages and YouTube videos
2. **Text Input**: For direct text/paste
3. **File Upload**: Drag & drop or click to upload

UI Components:
- Tabs for switching between methods
- File drop zone with supported formats
- Progress indicator during upload
- Success/error feedback
- Recent ingestions list

**File**: `/home/fr33m1nd/dev/pks/frontend/src/lib/api.ts`
Add file upload method:
```typescript
uploadFile: async (file: File, metadata?: Record<string, any>) => {
  const formData = new FormData()
  formData.append('file', file)
  if (metadata) formData.append('metadata', JSON.stringify(metadata))
  return request<IngestResponse>('/api/v1/ingest/upload', {
    method: 'POST',
    body: formData,
    headers: {} // Let browser set Content-Type for FormData
  })
}
```

### Phase 4: Navigation Updates

**Files**: All page.tsx files in `/home/fr33m1nd/dev/pks/frontend/src/app/`

Add "Ingest" link to navigation bar:
- `/` home page: Add button for Ingest
- `/chat`, `/documents`, `/settings`: Add nav link

## Files to Modify

| File | Change |
|------|--------|
| `backend/app/api/routes/ingestion.py` | Add `POST /upload` endpoint |
| `backend/app/services/parser_service.py` | Add `_parse_image()` method |
| `backend/requirements.txt` | Add `pillow==10.4.0` |
| `frontend/src/app/ingest/page.tsx` | **NEW** Ingestion page |
| `frontend/src/lib/api.ts` | Add `uploadFile()` method |
| `frontend/src/app/page.tsx` | Add Ingest button |
| `frontend/src/app/chat/page.tsx` | Add Ingest nav link |
| `frontend/src/app/documents/page.tsx` | Add Ingest nav link |
| `frontend/src/app/settings/page.tsx` | Add Ingest nav link |

## Verification

1. **Backend**: `curl -X POST http://localhost:8000/api/v1/ingest/upload -F "file=@test.pdf"`
2. **Frontend**: Navigate to `http://localhost:3100/ingest`
3. **E2E**: Upload a PDF → verify in Documents page → chat about it

## Dependencies

- `pillow` for image processing (lightweight, already widely used)
- Gemini Vision API (already configured with GEMINI_API_KEY)
