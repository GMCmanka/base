ALTER TABLE "user" ADD COLUMN IF NOT EXISTS role_id INTEGER REFERENCES role(id);

UPDATE "user" SET role_id = (SELECT id FROM role WHERE name = 'Admin') WHERE user_type = 'Admin';
UPDATE "user" SET role_id = (SELECT id FROM role WHERE name = 'Viewer') WHERE user_type = 'Normal';
