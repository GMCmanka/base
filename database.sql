-- Drop table if exists to avoid conflicts
DROP TABLE IF EXISTS public."user";

-- Create User table
CREATE TABLE public."user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,   -- Limited size for performance
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL DEFAULT 'Normal', -- Consistent with form options: 'Admin' or 'Normal'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Audit fields
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Auto-update with trigger if needed
);

-- Optional: Indexes for faster lookup
CREATE INDEX idx_user_email ON public."user"(email);
CREATE INDEX idx_user_type ON public."user"(user_type);
CREATE INDEX idx_user_status ON public."user"(is_active);`

ALTER TABLE role ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
ALTER TABLE permission ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
ALTER TABLE "user" ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
