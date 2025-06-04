"""
# Create records table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id SERIAL PRIMARY KEY,
        patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
        type VARCHAR(100) NOT NULL,
        provider VARCHAR(100) NOT NULL,
        date DATE NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'Draft',
        notes TEXT,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    )
''')
print("Records table created or already exists")

# Add any missing columns
cursor.execute('''
    DO $$
    BEGIN
        BEGIN
            ALTER TABLE records ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'Draft';
        EXCEPTION WHEN duplicate_column THEN
            -- Do nothing, column already exists
        END;
        
        BEGIN
            ALTER TABLE records ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
        EXCEPTION WHEN duplicate_column THEN
            -- Do nothing, column already exists
        END;
        
        BEGIN
            ALTER TABLE records ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
        EXCEPTION WHEN duplicate_column THEN
            -- Do nothing, column already exists
        END;
    END $$;
''')
print("Added any missing columns to records table")

# Insert sample records if table is empty
cursor.execute('SELECT COUNT(*) FROM records')
if cursor.fetchone()[0] == 0:
    cursor.execute('''
        INSERT INTO records (patient_id, type, provider, date, status, notes)
        VALUES 
            (1, 'Annual Physical', 'Dr. Smith', '2024-01-15', 'Completed', 'Regular checkup, all vitals normal'),
            (1, 'Lab Work', 'Dr. Johnson', '2024-02-20', 'Pending', 'Blood work for routine checkup'),
            (2, 'Vaccination', 'Dr. Williams', '2024-03-01', 'Completed', 'Flu vaccine administered'),
            (2, 'Consultation', 'Dr. Brown', '2024-03-15', 'Draft', 'Initial consultation for knee pain')
    ''')
    print("Sample records inserted")
""" 