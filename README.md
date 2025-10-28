# coursemology-py

A Python client library for interacting with the [Coursemology](https://coursemology.org). This library provides a convenient, type-safe interface for managing courses, assessments, submissions, and other Coursemology resources programmatically.

## Features

- 🔐 **OAuth 2.0 Authentication** with PKCE flow support
- 📝 **Type-safe API** using Pydantic models
- 🎯 **Comprehensive Coverage** of Coursemology API endpoints
- 🔄 **Automatic Token Refresh** for seamless long-running sessions
- 📦 **Course Management** - Create, update, and manage courses
- 📊 **Assessment Tools** - Handle assessments, submissions, and grading
- 👥 **User Management** - Manage course users, groups, and invitations
- 💬 **Communication** - Work with announcements, forums, and comments
- 📈 **Analytics** - Access course statistics and experience points

## Installation

Download or clone from GitHub and install:

```bash
pip install .
```

For development:

```bash
pip install .[dev]
```

## Quick Start

```python
from coursemology_py import CoursemologyClient

# Initialize the client
client = CoursemologyClient(host="https://coursemology.org")

# Login
client.login("your_username", "your_password")

# List all courses
courses = client.courses.index()
for course in courses.courses:
    print(f"{course.id}: {course.title}")

# Work with a specific course
course_api = client.course(course_id=123)

# Get course assessments
assessments = course_api.assessments.index()

# Get course users
users = course_api.users.index()
```

## API Coverage

### Core Client

- **CoursemologyClient** - Main client for authentication and API access
  - `login(username, password)` - Authenticate with Coursemology
  - `courses` - Access courses API
  - `course(course_id)` - Access specific course API
  - `jobs` - Check background job statuses
  - `download_file(url, local_path)` - Download files with authentication

### Courses API

```python
# List all courses
courses = client.courses.index()

# Get a specific course
course_api = client.course(course_id=123)
```

### Course-Level APIs

Each course provides access to the following resources:

#### Assessments

```python
course = client.course(123)

# List assessments
assessments = course.assessments.index()

# Get assessment details
assessment = course.assessments.show(assessment_id=456)

# Create assessment
from coursemology_py.models.course.assessments import AssessmentCreatePayload
payload = AssessmentCreatePayload(title="New Assessment", ...)
new_assessment = course.assessments.create(payload)
```

#### Submissions

```python
# List submissions
submissions = course.submissions.index()

# Get pending submissions
pending = course.submissions.pending(my_students=True)

# Filter submissions
filtered = course.submissions.filter(
    category_id=1,
    assessment_id=2,
    group_id=3
)

# Get submission details
submission = course.submissions.show(submission_id=789)

# Submit answers
course.submissions.submit(submission_id=789)

# Unsubmit
course.submissions.unsubmit(submission_id=789)

# Publish grades
course.submissions.publish(submission_id=789)
```

#### Users & Groups

```python
# List course users
users = course.users.index()

# Get user details
user = course.users.show(user_id=100)

# Update user
from coursemology_py.models.course.users import CourseUserUpdatePayload
payload = CourseUserUpdatePayload(name="New Name", role="teaching_assistant")
course.users.update(user_id=100, payload=payload)

# Manage groups
groups = course.groups.index()
group = course.groups.show(group_id=1)
```

#### Announcements

```python
# List announcements
announcements = course.announcements.index()

# Create announcement
from coursemology_py.models.course.announcements import AnnouncementPayload
payload = AnnouncementPayload(title="Important!", content="...")
new_announcement = course.announcements.create(payload)

# Update announcement
course.announcements.update(announcement_id=1, payload=payload)

# Delete announcement
course.announcements.delete(announcement_id=1)
```

#### Forums & Posts

```python
# List forums
forums = course.forums.index()

# Get forum details
forum = course.forums.show(forum_id=1)

# Work with posts
posts = course.posts.index(forum_id=1, topic_id=2)
post = course.posts.show(forum_id=1, topic_id=2, post_id=3)
```

#### Comments

```python
# Fetch comments
comments = course.comments.fetch_comment_data(tab_value="all", page_num=1)

# Create comment
from coursemology_py.models.course.comments import CommentPostPayload
payload = CommentPostPayload(text="Great work!")
course.comments.create(topic_id=1, payload=payload)

# Update/delete comments
course.comments.update(topic_id=1, post_id=2, payload=payload)
course.comments.delete(topic_id=1, post_id=2)
```

#### Experience Points & Statistics

```python
# Get experience points records
exp = course.experience_points.index()

# Download experience points data
course.experience_points.download()

# Get course statistics
stats = course.statistics.index()

# Get specific statistics
user_stats = course.statistics.users()
staff_stats = course.statistics.staff()
assessment_stats = course.statistics.assessments()
```

#### Assessment Categories & Questions

```python
# List assessment categories
categories = course.assessments.categories.index()

# Get category details
category = course.assessments.categories.show(category_id=1)

# Work with questions
questions = course.assessments.questions.index(assessment_id=1)
question = course.assessments.questions.show(assessment_id=1, question_id=2)
```

#### Answer Management

```python
# Get answers for a submission question
answers = course.answers.index(submission_id=1, question_id=2)

# Create/update answers
from coursemology_py.models.course.assessment.answer_payloads import ProgrammingAnswerPayload
payload = ProgrammingAnswerPayload(answer_text="print('Hello')")
answer = course.answers.create_answer(submission_id=1, answer=payload)
```

## Authentication

The library uses OAuth 2.0 with PKCE (Proof Key for Code Exchange) for secure authentication:

```python
client = CoursemologyClient(host="https://coursemology.org")
client.login("username", "password")
```

The client automatically:
- Handles the OAuth flow
- Manages access and refresh tokens
- Refreshes expired tokens automatically
- Maintains authenticated sessions

## Error Handling

```python
from coursemology_py.exceptions import CoursemologyAPIError

try:
    client.login("username", "password")
    courses = client.courses.index()
except CoursemologyAPIError as e:
    print(f"API Error: {e}")
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/coursemology-py.git
cd coursemology-py

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format and lint
ruff check .
ruff format .

# Type checking
mypy .
```

## Project Structure

```
coursemology_py/
├── __init__.py           # Main exports
├── client.py             # CoursemologyClient
├── auth.py               # OAuth authentication
├── exceptions.py         # Custom exceptions
├── utils.py              # Utility functions
├── api/                  # API handlers
│   ├── base.py
│   ├── courses.py
│   ├── jobs.py
│   └── course/           # Course-specific APIs
│       ├── assessments.py
│       ├── submissions.py
│       ├── users.py
│       ├── announcements.py
│       ├── forums.py
│       ├── comments.py
│       └── ...
└── models/               # Pydantic models
    ├── courses.py
    ├── jobs.py
    └── course/
        ├── assessments.py
        ├── submissions.py
        ├── users.py
        └── ...
```

## Requirements

- Python >= 3.13
- requests >= 2.32
- pydantic >= 2.12
- polars >= 1.34

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.