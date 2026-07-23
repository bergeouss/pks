# PKS Real Issues Diagnosis

## Issues Found

### 1. Settings Save Validation Error 🔴

**File:** `backend/app/api/routes/settings.py:11`

**Problem:** `embedding_provider` only allows `"openai"` and `"gemini"` in Literal type, but frontend allows `"ollama"`.

```python
# CURRENT (WRONG):
embedding_provider: Literal["openai", "gemini"] = "gemini"

# SHOULD BE:
embedding_provider: Literal["openai", "gemini", "ollama"] = "gemini"
```

**Impact:** Clicking "Save Settings" returns 422 validation error when trying to save embedding_provider=ollama.

---

### 2. Z.ai Models Not Showing (glm-4.7-flash missing) 🟡

**Root Cause:** Docker serialization issue in backend response.

**Backend returns:**
```
{
  models:
  {
    zai:
    [string] (6)  # Docker serialization format
  }
}
```

**Frontend needs to parse this format** and the models include: glm-5, glm-4.7, glm-4.6, etc. (6 models total from backend).

**Frontend fallback** only has: glm-4.5, glm-4.5-air, glm-4.6, glm-4.7, glm-5, glm-5-turbo (6 models) - but backend filtering excludes some.

**Fix needed:** Ensure backend returns actual model names, not just the Docker-serialized array.

---

### 3. Documents Show "Untitled Document" 🟡

**Root Cause:** Ingestion is not properly extracting or passing document title.

**Evidence:** All ingested documents have empty title field.

**Need to check:**
- Ingestion service metadata handling
- Parser service title extraction
- Qdrant payload structure

---

### 4. Ollama Embedding Dropdown Not Showing Models 🟡

**Backend IS returning correct models:**
```
Ollama embedding models: ['mxbai-embed-large:latest', 'DC1LEX/nomic-embed-text-v1.5-multimodal:latest']
```

**But frontend dropdown might not be:**
- Filtering by provider correctly
- Showing models after selection
- Handling the "ollama" provider in dropdown rendering

---

## Root Cause Summary

| Issue | Severity | Root Cause |
|-------|----------|------------|
| Settings save validation error | 🔴 Critical | `embedding_provider` Literal type missing "ollama" |
| Z.ai models not showing | 🟡 Medium | Docker serialization parsing in frontend |
| Documents show "Untitled" | 🟡 Medium | Missing title extraction in ingestion |
| Ollama embeddings not showing | 🟡 Medium | Frontend dropdown rendering/filtering issue |

---

## Files Needing Fixes

1. `backend/app/api/routes/settings.py` - Add "ollama" to embedding_provider Literal
2. `frontend/src/app/settings/page.tsx` - Fix Docker serialization parsing
3. `backend/app/services/ingestion_service.py` - Add title extraction
4. `frontend/src/app/documents/page.tsx` - Display title if available, fallback to "Untitled"

---

## Priority Fixes

1. **Fix settings validation** (line 11 of settings.py) - Blocks settings save completely
2. **Fix document titles** - Improves user experience
3. **Fix dropdown rendering** - Make Ollama models visible
4. **Fix Z.ai serialization** - Show all 6 models correctly