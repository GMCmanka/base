-- Database Schema for Flask User Management System

-- Create Role table
CREATE TABLE IF NOT EXISTS role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- Create User table
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    user_type VARCHAR(50) DEFAULT 'Normal',
    is_active BOOLEAN DEFAULT true,
    role_id INTEGER REFERENCES role(id) ON DELETE SET NULL,
    password_hash VARCHAR(255) NOT NULL DEFAULT ''
);

-- Insert default roles
INSERT INTO role (name) VALUES 
    ('Admin'),
    ('Editor'),
    ('Viewer')
ON CONFLICT (name) DO NOTHING;

-- Insert default admin user (password: admin123)
INSERT INTO "user" (username, full_name, email, user_type, is_active, role_id, password_hash)
SELECT 'admin', 'System Admin', 'admin@agriculture.com', 'Admin', true, 
       (SELECT id FROM role WHERE name = 'Admin'),
       'pbkdf2:sha256:600000$placeholder$placeholder'
WHERE NOT EXISTS (SELECT 1 FROM "user" WHERE username = 'admin');

-- Insert sample users
INSERT INTO "user" (username, full_name, email, user_type, is_active, role_id, password_hash)
SELECT 'john', 'John Doe', 'john@example.com', 'Normal', true,
       (SELECT id FROM role WHERE name = 'Editor'),
       'pbkdf2:sha256:600000$placeholder$placeholder'
WHERE NOT EXISTS (SELECT 1 FROM "user" WHERE username = 'john');

INSERT INTO "user" (username, full_name, email, user_type, is_active, role_id, password_hash)
SELECT 'jane', 'Jane Smith', 'jane@example.com', 'Normal', true,
       (SELECT id FROM role WHERE name = 'Viewer'),
       'pbkdf2:sha256:600000$placeholder$placeholder'
WHERE NOT EXISTS (SELECT 1 FROM "user" WHERE username = 'jane');

INSERT INTO "user" (username, full_name, email, user_type, is_active, role_id, password_hash)
SELECT 'bob', 'Bob Wilson', 'bob@example.com', 'Normal', false,
       (SELECT id FROM role WHERE name = 'Viewer'),
       'pbkdf2:sha256:600000$placeholder$placeholder'
WHERE NOT EXISTS (SELECT 1 FROM "user" WHERE username = 'bob');
