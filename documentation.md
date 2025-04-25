# Fragrance Chatbot - Stage 1 Documentation

## Overview
Stage 1 of the Fragrance Chatbot implementation focuses on the core chat and session management functionality. This document provides detailed information about the implemented features, architecture, and technical specifications.

## Table of Contents
1. [Core Features](#core-features)
2. [API Endpoints](#api-endpoints)
3. [Session Management](#session-management)
4. [Error Handling](#error-handling)
5. [Logging System](#logging-system)
6. [Database Schema](#database-schema)
7. [Configuration](#configuration)

## Core Features

### 1. Basic Chat System
- **Chat Interface**: A web-based interface for user interaction
- **Conversation Flow**: Real-time chat with streaming responses
- **Session Management**: Persistent chat sessions with user context
- **Error Handling**: Comprehensive error handling and user feedback

### 2. Session Management
- **Session Creation**: Automatic session creation for new users
- **Session Recovery**: Ability to recover existing sessions
- **Session Expiration**: Automatic session cleanup after 24 hours of inactivity
- **Session Cleanup**: Background task for removing expired sessions

## API Endpoints

### 1. Start Session
- **Endpoint**: `POST /api/v1/start-session`
- **Purpose**: Initialize a new chat session or recover an existing one
- **Request Body**:
  ```json
  {
    "user_id": "optional_user_id",
    "is_new_chat": false
  }
  ```
- **Response**:
  ```json
  {
    "session_id": "unique_session_id",
    "message": "Welcome message"
  }
  ```

### 2. Chat
- **Endpoint**: `POST /api/v1/chat`
- **Purpose**: Handle chat messages with streaming response
- **Request Body**:
  ```json
  {
    "session_id": "session_id",
    "message": "user_message"
  }
  ```
- **Response**: Server-Sent Events (SSE) stream of chat responses

### 3. Health Check
- **Endpoint**: `GET /api/v1/health`
- **Purpose**: Check API health status
- **Response**:
  ```json
  {
    "status": "healthy"
  }
  ```

## Session Management

### Session Configuration
- **Timeout**: 24 hours of inactivity
- **Cleanup Interval**: Every hour
- **Storage**: SQLite database with in-memory caching

### Session States
1. **Initial**: New session created
2. **Active**: Session with ongoing conversation
3. **Expired**: Session past timeout period
4. **Deleted**: Cleaned up session

### Session Cleanup Process
1. Background task runs every hour
2. Identifies sessions older than 24 hours
3. Removes expired sessions from database
4. Logs cleanup operations

## Error Handling

### Error Types
1. **Session Errors**
   - Session not found
   - Session expired
   - Invalid session ID

2. **API Errors**
   - Invalid request format
   - Missing required fields
   - Server errors

3. **Database Errors**
   - Connection issues
   - Query failures
   - Data integrity issues

### Error Responses
```json
{
  "detail": "Error message",
  "status_code": 400/404/500
}
```

## Logging System

### Log Configuration
- **Log Levels**: INFO, DEBUG, ERROR
- **Log Rotation**: 10MB file size limit
- **Backup Count**: 5 rotated files
- **Output**: Both file and console

### Log Format
```
File Logs:
%(asctime)s - %(name)s - %(levelname)s - %(message)s

Console Logs:
%(levelname)s - %(message)s
```

### Log Categories
1. **Session Logs**
   - Session creation
   - Session updates
   - Session deletion
   - Session expiration

2. **API Logs**
   - Request processing
   - Response generation
   - Error handling

3. **System Logs**
   - Application startup
   - Application shutdown
   - Background tasks

## Database Schema

### Sessions Table
```sql
CREATE TABLE sessions (
    session_id VARCHAR PRIMARY KEY,
    user_id VARCHAR,
    conversation_history JSON,
    last_interaction DATETIME,
    conversation_stage VARCHAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Configuration

### Environment Variables
- `DATABASE_URL`: Database connection string
- `OPENAI_API_KEY`: OpenAI API key
- `SESSION_TIMEOUT`: Session expiration time (default: 24 hours)
- `CLEANUP_INTERVAL`: Session cleanup interval (default: 1 hour)

### System Requirements
- Python 3.8+
- FastAPI
- SQLite
- OpenAI API access

## Testing Points
1. **Session Management**
   - [x] Can start a new chat session
   - [x] Can recover existing session
   - [x] Session persists during conversation
   - [x] Session expires after timeout

2. **Chat Functionality**
   - [x] Can send messages
   - [x] Can receive streaming responses
   - [x] Conversation history maintained
   - [x] Error handling works

3. **System Features**
   - [x] Logging system operational
   - [x] Session cleanup working
   - [x] Error handling functional
   - [x] Health check endpoint working 