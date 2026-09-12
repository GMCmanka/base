-- Add new columns to user table
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS avatar VARCHAR(255) DEFAULT 'avatar-19.jpg';
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS dark_mode BOOLEAN DEFAULT false;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

-- Create activity_log table
CREATE TABLE IF NOT EXISTS activity_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON activity_log(created_at);
