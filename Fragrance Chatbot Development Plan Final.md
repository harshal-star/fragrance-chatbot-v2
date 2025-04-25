# Fragrance Chatbot Development Plan

## Stage 1: Core Chat & Session Management (Week 1)
**Duration: 5-7 days**

### Testable Deliverables
1. **Basic Chat System**
   - Working chat interface
   - Basic conversation flow
   - Session management
   - Error handling

### Client Testing Points
- Can start a new chat session
- Can send and receive messages
- Session persists during conversation
- Basic error handling works

### API Endpoints Ready for Testing
```python
# POST /start-session
@app.post("/start-session")
async def start_session(request: StartSessionRequest):
    session_id = generate_session_id()
    initial_message = "Hey there! Ready to create a fragrance that totally fits your vibe?"
    return {
        "session_id": session_id,
        "message": initial_message
    }

# POST /chat
@app.post("/chat")
async def chat(request: ChatRequest):
    session_context = get_session_context(request.session_id)
    response = await generate_response(session_context, request.message)
    return {"bot_message": response}
```

## Stage 2: User Profile & Basic Information Extraction (Week 2)
**Duration: 5-7 days**

### Testable Deliverables
1. **Enhanced Chat with Profile Extraction**
   - Working profile extraction
   - Personality detection
   - Style preference analysis
   - Basic scent preference mapping

### Client Testing Points
- Can extract user name
- Can detect personality traits
- Can identify style preferences
- Can track basic scent preferences
- All Stage 1 features still work

### New API Endpoints Ready for Testing
```python
# POST /parse-user-profile
@app.post("/parse-user-profile")
async def parse_profile(request: ParseProfileRequest):
    profile = extract_profile(request.conversation_history)
    return {
        "vibe": profile.vibe,
        "likes": profile.likes,
        "dislikes": profile.dislikes,
        "branding_goal": profile.branding_goal
    }
```

## Stage 3: Image Analysis Integration (Week 3)
**Duration: 5-7 days**

### Testable Deliverables
1. **Image Upload and Analysis System**
   - Image upload functionality
   - Image processing and analysis
   - Visual style detection
   - Makeup and appearance analysis
   - Integration with user profile

### Client Testing Points
- Can upload user photos
- Can analyze clothing style
- Can detect makeup preferences
- Can extract visual personality cues
- Can integrate visual analysis with fragrance recommendations
- All Stage 1 & 2 features still work

### New API Endpoints Ready for Testing
```python
# POST /upload-image
@app.post("/upload-image")
async def upload_image(request: UploadImageRequest):
    image_data = await process_image(request.image_file)
    analysis = await analyze_image(image_data)
    return {
        "style_analysis": analysis.style,
        "makeup_analysis": analysis.makeup,
        "appearance_insights": analysis.insights,
        "confidence_score": analysis.confidence
    }

# POST /integrate-visual-profile
@app.post("/integrate-visual-profile")
async def integrate_visual_profile(request: VisualProfileRequest):
    combined_profile = combine_visual_and_textual_profile(
        request.visual_analysis,
        request.text_profile
    )
    return {
        "enhanced_profile": combined_profile,
        "visual_insights": request.visual_analysis.insights
    }
```

## Stage 4: Web Search Integration (Week 4)
**Duration: 5-7 days**

### Testable Deliverables
1. **Enhanced Chat with Web Search**
   - Working web search functionality
   - Search result processing
   - Context-aware responses
   - Search caching system

### Client Testing Points
- Can search for recent fragrance information
- Can get current market trends
- Can find product availability
- Can get price comparisons
- All previous features still work

### New API Endpoints Ready for Testing
```python
# POST /web-search
@app.post("/web-search")
async def web_search(request: WebSearchRequest):
    search_results = await perform_web_search(request.query, request.session_id)
    return {
        "results": search_results,
        "context": request.context
    }
```

## Stage 5: Fragrance Recommendation System (Week 5)
**Duration: 5-7 days**

### Testable Deliverables
1. **Complete System with Recommendations**
   - Working recommendation system
   - Fragrance mapping
   - Name generation
   - Description system
   - Profile integration
   - Visual profile integration

### Client Testing Points
- Can get personalized fragrance recommendations
- Can see fragrance names and descriptions
- Can get scent profiles
- Visual analysis influences recommendations
- All previous features still work

### New API Endpoints Ready for Testing
```python
# POST /recommend-fragrance
@app.post("/recommend-fragrance")
async def recommend_fragrance(request: RecommendRequest):
    recommendation = generate_recommendation(
        request.vibe,
        request.likes,
        request.dislikes,
        request.branding_goal,
        request.visual_profile
    )
    return {
        "fragrance_concept": {
            "name": recommendation.name,
            "notes": recommendation.notes,
            "description": recommendation.description,
            "visual_influence": recommendation.visual_influence
        }
    }

# POST /save-user-profile
@app.post("/save-user-profile")
async def save_profile(request: SaveProfileRequest):
    save_user_data(request.user_id, request.profile, request.fragrance_concept)
    return {"message": "Profile saved successfully"}
```

## Testing Strategy for Each Stage

### Stage 1 Testing
```python
# Test cases for basic chat
async def test_basic_chat():
    # Start session
    session = await start_session()
    
    # Send messages
    response1 = await chat(session.id, "Hello")
    assert "Lila" in response1.message
    
    response2 = await chat(session.id, "My name is Alex")
    assert "Alex" in response2.message
```

### Stage 2 Testing
```python
# Test cases for profile extraction
async def test_profile_extraction():
    # Continue from previous session
    response = await chat(session.id, "I love fresh scents and have a casual style")
    
    # Check profile extraction
    profile = await parse_profile(session.id)
    assert "fresh" in profile.likes
    assert "casual" in profile.style
```

### Stage 3 Testing
```python
# Test cases for image analysis
async def test_image_analysis():
    # Test image upload and analysis
    with open("test_image.jpg", "rb") as image_file:
        analysis = await upload_image(session.id, image_file)
        assert analysis.style
        assert analysis.makeup
        assert analysis.insights
        
    # Test profile integration
    combined_profile = await integrate_visual_profile(session.id)
    assert combined_profile.enhanced_profile
    assert combined_profile.visual_insights
```

### Stage 4 Testing
```python
# Test cases for web search
async def test_web_search():
    # Test search functionality
    response = await chat(session.id, "What are the latest releases from Chanel?")
    assert "Chanel" in response.message
    assert "recent" in response.message.lower()
```

### Stage 5 Testing
```python
# Test cases for recommendations
async def test_recommendations():
    # Get recommendation
    recommendation = await recommend_fragrance(session.id)
    assert recommendation.name
    assert recommendation.notes
    assert recommendation.description
    assert recommendation.visual_influence
```

## Documentation for Each Stage

### Stage 1 Documentation
- Basic API usage
- Session management
- Error handling
- Testing instructions

### Stage 2 Documentation
- Profile extraction
- Personality detection
- Style analysis
- Testing new features

### Stage 3 Documentation
- Image upload and processing
- Visual analysis capabilities
- Privacy and security measures
- Testing image features

### Stage 4 Documentation
- Web search functionality
- Search triggers
- Result formatting
- Testing search features

### Stage 5 Documentation
- Recommendation system
- Fragrance mapping
- Profile integration
- Visual influence on recommendations
- Complete system testing

## Key Features of This Plan
- Each stage is independently testable
- Features build upon previous stages
- Client can test progress incrementally
- Documentation is updated at each stage
- Testing is comprehensive and clear
- Visual analysis enhances personalization
- Privacy-focused image handling