# 🔧 Troubleshooting Guide - AI Tour System

## Common Issues and Solutions

### Issue 1: "500 Internal Server Error" on /plan endpoint

**Symptoms:**
- Browser console shows: `POST http://127.0.0.1:5000/plan 500 (INTERNAL SERVER ERROR)`
- Error: `SyntaxError: Unexpected token '<'`

**Causes:**
1. Server crashed and returned HTML error page instead of JSON
2. Missing dependencies or import errors
3. Database connection timeout
4. Unhandled exception in the agent code

**Solutions:**

#### Solution 1: Restart the Flask Server
```bash
# Stop the current server (Ctrl+C)
# Then restart:
cd ui
python app.py
```

#### Solution 2: Check Server Console
Look at the terminal where Flask is running. You should see detailed error messages with stack traces.

#### Solution 3: Run System Check
```bash
python check_system.py
```

This will verify all dependencies and connections.

#### Solution 4: Check MongoDB Connection
If MongoDB is timing out:
- Verify internet connection
- Check if MongoDB Atlas IP whitelist includes your IP
- Try the connection string directly:
```python
python -c "from pymongo import MongoClient; import certifi; client = MongoClient('your-uri', tlsCAFile=certifi.where()); print('OK')"
```

#### Solution 5: Clear Browser Cache
Sometimes old JavaScript is cached:
1. Open DevTools (F12)
2. Right-click refresh button → "Empty Cache and Hard Reload"

---

### Issue 2: "TypeError: ... is not JSON serializable"

**Cause:** Python objects (like datetime, ObjectId) can't be directly converted to JSON.

**Solution:** Already fixed in the updated code. Make sure you have the latest version.

---

### Issue 3: No Results Generated

**Symptoms:**
- Request succeeds but no tour packages shown
- Empty results

**Solutions:**

1. **Check Database:**
```bash
python -c "from pymongo import MongoClient; import certifi; client = MongoClient('your-uri', tlsCAFile=certifi.where()); print(client.AITourReccomendation.tour_packages.count_documents({}))"
```

2. **Check Console Output:**
Look for warnings like "⚠️ Generating custom plan..."

3. **Try Simpler Query:**
- Budget: 1000
- Days: 5
- Text: "beach"

---

### Issue 4: Slow Response Times

**Causes:**
- ML model initialization
- Database queries without caching
- Heavy NLP processing

**Solutions:**

1. **Already Optimized:**
   - Caching enabled for packages (5-minute cache)
   - ML model optional (disabled for speed)
   - Fast fallback planning

2. **Further Optimization:**
```python
# In advanced_agent.py, ensure these are None for speed:
self.ml_model = None  
self.reasoning_engine = None
self.personalizer = None
```

---

### Issue 5: Import Errors

**Error:** `ModuleNotFoundError: No module named 'agent'`

**Solution:**
```bash
# Ensure you're in the correct directory
cd "d:\AI\New folder\tour_ai_final"

# Run from ui directory:
cd ui
python app.py
```

The app.py has path fixes to import from parent directory.

---

## Quick Restart Guide

### Method 1: Clean Restart
```bash
# 1. Stop server (Ctrl+C in the terminal)

# 2. Navigate to UI folder
cd "d:\AI\New folder\tour_ai_final\ui"

# 3. Start Flask
python app.py

# 4. Open browser
# Go to: http://127.0.0.1:5000
```

### Method 2: With System Check
```bash
# 1. Run system check first
cd "d:\AI\New folder\tour_ai_final"
python check_system.py

# 2. If all checks pass, start server
cd ui
python app.py
```

---

## Debugging Steps

### Step 1: Enable Debug Mode
In `ui/app.py`, at the bottom:
```python
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
```

This shows detailed error messages in browser.

### Step 2: Check Terminal Output
The Flask terminal will show:
- Request details
- Error stack traces
- Print statements from the code

### Step 3: Browser DevTools
1. Open DevTools (F12)
2. Go to "Network" tab
3. Try the action that fails
4. Click on the failed request
5. Check:
   - **Headers:** Request payload
   - **Response:** Server response
   - **Console:** JavaScript errors

### Step 4: Test Backend Directly
```bash
# Test the agent in isolation
python test_plan.py
```

This bypasses Flask and tests the AI agent directly.

---

## Error Messages Explained

### "Database connection error"
- MongoDB is unreachable
- Check internet connection
- Verify connection string

### "Invalid request data"
- Frontend sent malformed JSON
- Check browser console for details

### "No X-day tour found under $Y"
- Database has no matching packages
- Fallback generator will create custom tour
- Check if the days/budget combination is reasonable

---

## Performance Benchmarks

**Expected Response Times:**
- Simple query: < 500ms
- Complex query: < 1 second
- With ML prediction: < 2 seconds

**If slower:**
- Check CPU usage
- Verify caching is working
- Ensure ML model is disabled for speed

---

## Contact & Support

If issues persist:

1. **Check the code version:**
   - Updated `/plan` endpoint with try-catch
   - Updated frontend with better error handling

2. **Review these files:**
   - `ui/app.py` - Backend logic
   - `ui/templates/index.html` - Frontend code
   - `agent/advanced_agent.py` - AI agent

3. **Test components individually:**
   - Run `check_system.py`
   - Run `test_plan.py`
   - Check MongoDB connection

---

## Recent Fixes Applied

### ✅ Fix 1: Proper Error Handling in /plan Endpoint
**Before:** Server returned HTML error page  
**After:** Returns JSON with error details

**Location:** `ui/app.py` line 86-118

### ✅ Fix 2: Frontend Error Handling
**Before:** JavaScript crashed on HTML response  
**After:** Gracefully handles errors and shows user-friendly messages

**Location:** `ui/templates/index.html` line 119-132

### ✅ Fix 3: Request Validation
**Added:** Checks for valid request.json before processing

---

## Testing Checklist

After restart, test these scenarios:

- [ ] Homepage loads
- [ ] Login works
- [ ] Simple query: "beach, $1000, 5 days"
- [ ] Complex query: "adventure and culture, $2000, 7 days"
- [ ] Reject and regenerate
- [ ] Map displays correctly
- [ ] Day-by-day itinerary shows
- [ ] Booking works
- [ ] PDF download works

---

## Log Files

Check these for errors:
- Flask console output (where you ran `python app.py`)
- Browser console (F12 → Console tab)
- Network tab (F12 → Network tab)

---

**Last Updated:** January 2026  
**System Status:** ✅ All checks passing
