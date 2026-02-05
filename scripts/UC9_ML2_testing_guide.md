"""
UC9_ML2 UI Testing Guide
Tests for the new Streamlit UI enhancements
"""

# Manual Testing Checklist for UC9_ML2

## Prerequisites
1. Backend API must be running: `uvicorn main:app --reload`
2. Database must be initialized
3. Streamlit app running: `streamlit run streamlit.py`

## Test Scenarios

### Test 1: Create Campaign with Text and Image Display
**Steps**:
1. Navigate to "Create Campaign" page
2. Fill in campaign details:
   - Campaign Name: "Summer Fitness Challenge"
   - Brand Name: "FitNow"
   - Objective: "Promote summer wellness activities"
   - Target Audience: "Health-conscious individuals"  
3. Click "Create Campaign"

**Expected Results**:
- ✅ Success message appears
- ✅ "Generated Content" section displays
- ✅ Left column shows "📝 Generated Text" with content
- ✅ Right column shows "🖼️ Generated Image"
- ✅ Regenerate and Save buttons appear
- ✅ Generation Details expandable section appears

**Edge Case**: If text or image missing:
- Shows "No text/image available" message
- Optional checkbox to "Show raw data" for debugging

---

### Test 2: Regenerate Functionality
**Steps**:
1. After creating a campaign (Test 1)
2. Click "🔄 Regenerate" button

**Expected Results**:
- ✅ Spinner shows "Regenerating content..."
- ✅ API called with same campaign inputs
- ✅ New campaign ID generated
- ✅ Display updates with new text and image
- ✅ Success message: "✨ Content regenerated successfully!"
- ✅ Page refreshes to show new content

**Error Handling**:
- If API call fails: Error message shown
- If session state missing: Graceful handling

---

### Test 3: Save & Accept Functionality
**Steps**:
1. After creating/regenerating a campaign
2. Click "✅ Save & Accept" button

**Expected Results**:
- ✅ Success message: "✅ Campaign {ID} approved and saved!"
- ✅ Balloons animation appears
- ✅ Content remains on screen (not cleared)

**Note**: ML Engineer 1 will add actual API endpoint later.
Currently shows confirmation only.

---

### Test 4: Session State Persistence
**Steps**:
1. Create a campaign
2. View generated content
3. Click browser back/forward or navigate to "View Campaigns"
4. Return to "Create Campaign"

**Expected Results**:
- ✅ Last generated content still visible
- ✅ Can still regenerate or save
- ✅ Form can be filled again for new campaign

---

### Test 5: Generation Details Expander
**Steps**:
1. After creating campaign
2. Click "📋 Generation Details" expander

**Expected Results**:
- ✅ Campaign ID displayed
- ✅ Campaign Name displayed
- ✅ Brand displayed
- ✅ Full JSON response shown
- ✅ Can collapse/expand

---

### Test 6: Error Handling
**Scenario A: Backend not running**
1. Stop backend API
2. Try to create campaign

**Expected**:
- ✅ Error: "Failed to connect to backend API. Is the server running?"

**Scenario B: Invalid image URL**
1. Mock response with invalid image URL
2. View results

**Expected**:
- ✅ Error message: "Failed to load image"
- ✅ Image URL shown for debugging

**Scenario C: Empty response**
1. Mock empty response from API
2. View results

**Expected**:
- ✅ Info message: "No text/image available"
- ✅ Option to show raw data

---

## Automated Testing

Since this is UI-focused (Streamlit), automated testing is limited.
However, we can test the logic:

```python
# Test session state structure
def test_session_state():
    # After campaign creation
    assert 'current_campaign' in st.session_state
    assert 'last_payload' in st.session_state
    
    # Current campaign structure
    campaign = st.session_state.current_campaign
    assert 'campaign_id' in campaign
    assert 'campaign_name' in campaign
    assert 'brand' in campaign
    assert 'data' in campaign

# Test payload structure
def test_payload():
    payload = st.session_state.last_payload
    assert 'campaign_name' in payload
    assert 'brand' in payload
    assert 'objective' in payload
    assert 'inputs' in payload
```

---

## Visual Verification

### Layout Check
- [ ] Side-by-side columns are equal width
- [ ] Text column on left, image on right
- [ ] Buttons centered and properly spaced
- [ ] Emojis render correctly

### Responsiveness
- [ ] Works on wide screen (laptop)
- [ ] Works on medium screen (tablet)
- [ ] Content wraps gracefully

---

## Known Limitations

1. **ML Engineer 1's Endpoints Not Yet Available**:
   - No dedicated `/regenerate` endpoint
   - No `/approve` endpoint
   - Workaround: Using `/start_campaign` for both create and regenerate

2. **API Response Format**:
   - Assuming response has `text_content` and `image_url`
   - Falls back to `generated_text` and `generated_image_url`
   - May need adjustment based on actual API response

3. **Image Loading**:
   - Requires valid URL (local files won't work unless served)
   - External URLs must be accessible

---

## Success Criteria Verification

✅ All features implemented:
- [x] Side-by-side text and image display
- [x] st.image() for image rendering
- [x] Regenerate button with same inputs
- [x] Save & Accept button with confirmation
- [x] Session state management
- [x] Error handling
- [x] Generation details

**UC9_ML2 Complete** - Ready for user testing!
