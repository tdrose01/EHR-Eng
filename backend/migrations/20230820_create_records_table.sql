-- Migration to create a simplified records table for testing

-- Create records table
CREATE TABLE IF NOT EXISTS records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(20),
    contact_number VARCHAR(30),
    email VARCHAR(255),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add test records
INSERT INTO records (patient_name, date_of_birth, gender, email)
VALUES 
    ('John Doe', '1980-01-01', 'Male', 'john.doe@example.com'),
    ('Jane Smith', '1985-05-15', 'Female', 'jane.smith@example.com'),
    ('Michael Johnson', '1975-10-20', 'Male', 'michael.johnson@example.com');

-- Create update trigger for updated_at
CREATE OR REPLACE FUNCTION update_records_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_records_updated_at_trigger
BEFORE UPDATE ON records
FOR EACH ROW
EXECUTE FUNCTION update_records_updated_at(); 