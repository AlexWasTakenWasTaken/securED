# Course Manager with AI Feedback

This project is a comprehensive web-based application designed to manage courses, assignments, and submissions, integrated with AI-powered essay feedback and detection. It leverages modern web technologies, encryption, and AI services to provide a seamless and secure experience for instructors and students.

## Features
- **Course Management**: Create, enroll, and delete courses.
- **Assignment Management**: Add, view, delete, and submit assignments.
- **AI Feedback Integration**: 
  - **Essay Feedback**: Uses OpenAI's GPT-4 model to provide detailed feedback, including strengths, weaknesses, and a final grade.
  - **AI Detection**: Identifies whether an essay is likely AI-generated based on sentence structure, fluency, and other linguistic patterns.
- **File Encryption**: Ensures secure storage of user-uploaded files using the Fernet encryption algorithm.
- **User Management**:
  - User registration and login with hashed passwords.
  - Role-based features for instructors and students.
- **Real-Time Data Access**: View active courses, assignments, and user submissions with dynamic updates.

## Skills and Technologies
### Backend Development
- **Python**:
  - Flask framework for routing, templates, and user authentication.
  - SQLAlchemy for database management and ORM.
- **Encryption**:
  - Implemented Fernet encryption for secure file handling.
- **Integration with OpenAI API**:
  - AI feedback and detection using OpenAI's GPT-4 model.

### Database Management
- **SQLite**:
  - Lightweight, file-based relational database for storing users, courses, assignments, and submissions.

### Web Development
- **Flask Templates**: HTML templates for dynamic, user-friendly interfaces.
- **Session Management**: Secure handling of user sessions and authentication.

### Security
- **Password Hashing**: Ensures secure storage of user passwords using SHA-256.
- **Access Control**: Role-based permission system for secure interaction with courses and assignments.

### Software Design
- **Object-Oriented Design**: Modular and scalable design with well-defined models (`User`, `Course`, `Assignment`, etc.).
- **Reusable Components**: Encapsulation of common functionalities like user management and encryption.

## Highlights
- **AI-Powered Learning**: A unique integration of AI tools to assist in academic learning and evaluation.
- **End-to-End Encryption**: Robust security for user data and uploaded files.
- **Clean and Modular Codebase**: Promotes maintainability and scalability for future enhancements.

## Purpose
This project serves as a showcase of full-stack development skills, including backend architecture, database design, AI integration, and secure coding practices. It demonstrates expertise in Python programming, web frameworks, and the practical application of AI in education.

---

Thank you for exploring this project! Feedback and suggestions are always welcome.
