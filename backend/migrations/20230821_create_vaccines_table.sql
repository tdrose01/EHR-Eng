-- Migration for vaccines table

-- Create vaccines table
CREATE TABLE IF NOT EXISTS vaccines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_id UUID NOT NULL REFERENCES records(id) ON DELETE CASCADE,
    vaccine_name VARCHAR(255) NOT NULL,
    brand_name VARCHAR(255),
    manufacturer VARCHAR(255),
    cvx_code VARCHAR(50),
    ndc_code VARCHAR(50),
    lot_number VARCHAR(50),
    dose_amount VARCHAR(50),
    route VARCHAR(20),
    site VARCHAR(20),
    dose_number INTEGER,
    total_doses INTEGER,
    next_dose_date DATE,
    contraindications TEXT,
    storage_requirements TEXT,
    additional_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add index for faster lookups by record_id
CREATE INDEX idx_vaccines_record_id ON vaccines(record_id);

-- Add vaccine_id column to records table with a foreign key
ALTER TABLE records 
ADD COLUMN IF NOT EXISTS vaccine_id UUID REFERENCES vaccines(id) ON DELETE SET NULL;

-- Create update trigger for updated_at
CREATE OR REPLACE FUNCTION update_vaccines_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_vaccines_updated_at_trigger
BEFORE UPDATE ON vaccines
FOR EACH ROW
EXECUTE FUNCTION update_vaccines_updated_at(); 