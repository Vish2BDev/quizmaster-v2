# API Endpoints Documentation

## Authentication Endpoints

### POST /api/auth/login
Authenticate user and return JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "firstName": "John",
    "lastName": "Doe",
    "email": "user@example.com",
    "role": "user"
  }
}
```

### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "user@example.com",
  "password": "password123"
}
```

### POST /api/auth/logout
Logout user and invalidate token.

### GET /api/auth/profile
Get current user profile information.

## Quiz Endpoints

### GET /api/user/available-quizzes
Get list of available quizzes for the user.

**Response:**
```json
{
  "quizzes": [
    {
      "id": 1,
      "title": "JavaScript Fundamentals",
      "description": "Test your JavaScript knowledge",
      "questionCount": 20,
      "timeLimit": 30,
      "difficulty": "beginner"
    }
  ]
}
```

### GET /api/user/quiz/{id}
Get quiz details and questions.

**Response:**
```json
{
  "id": 1,
  "title": "JavaScript Fundamentals",
  "description": "Test your JavaScript knowledge",
  "timeLimit": 30,
  "questions": [
    {
      "id": 1,
      "text": "What is JavaScript?",
      "options": ["A programming language", "A markup language", "A styling language"],
      "image": null
    }
  ]
}
```

### POST /api/user/quiz/{id}/submit
Submit quiz answers.

**Request Body:**
```json
{
  "answers": {
    "0": 0,
    "1": 2,
    "2": 1
  }
}
```

### GET /api/user/quiz/{id}/results
Get quiz results and analysis.

### GET /api/user/quiz-history
Get user's quiz history.

## Admin Endpoints

### GET /api/admin/analytics/overview
Get system overview analytics.

### GET /api/admin/quizzes
Get all quizzes for management.

### POST /api/admin/quizzes
Create a new quiz.

### PUT /api/admin/quizzes/{id}
Update quiz details.

### DELETE /api/admin/quizzes/{id}
Delete a quiz.

### GET /api/admin/users
Get all users for management.

### PUT /api/admin/users/{id}
Update user details.

### POST /api/admin/notifications
Send notification to users.

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "status": 400,
  "details": "Additional error details"
}
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <token>
``` 