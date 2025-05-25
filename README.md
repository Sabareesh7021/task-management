# Task Management System - Django REST API

## Project Overview
A comprehensive Django-based REST API for task management with:
- JWT authentication
- User management (CRUD operations)
- Task management with workflow controls
- Role-based permissions (super admin, admin, regular user)

## Key Features
- **User Roles**:
  - Super Admin: Full access
  - Admin: Can create tasks and manage their assigned users
  - Regular User: Can only manage their own tasks

- **Task Workflow**:
  - Status transitions (pending → in_progress → completed)
  - Validation for task assignments
  - Work hour tracking

## API Endpoints

### Authentication (`/auth/`)
- `POST /login/` - User login
- `POST /logout/` - User logout
- `POST /create-user/` - Create user (admin only)
- `GET /get-users/` - List users
- `GET /user/<id>/` - Get user by ID
- `PATCH /update-user/<id>/` - Update user
- `DELETE /delete-user/<id>/` - Delete user (super admin only)

### Task Management (`/api/`)
- `GET /get-tasks/` - List tasks (filterable by status, assignee, search)
- `GET /get-task/<id>/` - Get task details
- `POST /create-task/` - Create new task (admin only)
- `PATCH /update-task/<id>/` - Update task
- `DELETE /delete-task/<id>/` - Delete task (super admin only)
- `POST /start-task/<id>/` - Start a task (user-specific)

## Setup with Docker

### Prerequisites
- Docker installed
- Docker Compose installed

### Quick Start
1. **Build and deploy**:
   ```bash
   docker-compose build
   docker stack deploy -c docker-compose.yml task_stack
   ```
   or for non-swarm environments:
   ```bash
   docker-compose up -d
   ```

2. **Configuration**:
   - Copy `.env.example` to `.env`
   - Configure database settings (SQLite by default)
   - Set `APP_URL` and `FRONTEND_URLS`
   - Adjust other environment variables as needed

## Database Models

### User Model
- Standard Django user model extended with:
  - Role differentiation (super_admin, admin, user)
  - User creation tracking

### Task Model
- Fields:
  - Title, description
  - Assigned_to, assigned_by (User FK)
  - Due date
  - Status (pending, in_progress, completed, etc.)
  - Completion report
  - Worked hours
  - Timestamps

## Permissions
- **Task Access**:
  - Super Admins: All tasks
  - Admins: Their tasks + tasks they assigned
  - Users: Only their tasks

- **Task Operations**:
  - Creation: Admin+
  - Deletion: Super Admin only
  - Updates: Owner or admin

## Validation Rules
- Status transitions (e.g., can't revert from completed)
- One active task per user at a time
- Required fields for completion (report, hours)
- Positive worked hours validation

## Technical Stack
- Django REST Framework
- JWT Authentication
- MySQL/SQLite support
- Dockerized deployment
- Pagination support
- Comprehensive error handling

## Usage Notes
- All task endpoints require authentication
- Filter tasks using query params:
  - `?status=<status>`
  - `?assignedTo=<user_id>`
  - `?search=<text>`
- Task status changes are validated according to workflow rules