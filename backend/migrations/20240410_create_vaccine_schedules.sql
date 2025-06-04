-- Migration: Create vaccine schedules table to store product insert information

-- Create vaccine_schedules table
CREATE TABLE IF NOT EXISTS vaccine_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vaccine_name VARCHAR(255) NOT NULL,
    brand_name VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(255) NOT NULL,
    dose_number INTEGER NOT NULL,
    min_age_weeks INTEGER,
    max_age_weeks INTEGER,
    interval_from_previous_weeks INTEGER,
    preferred_interval_weeks INTEGER,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(vaccine_name, brand_name, manufacturer, dose_number)
);

-- Create index for faster lookups by vaccine name and brand
CREATE INDEX idx_vaccine_schedules_vaccine ON vaccine_schedules(vaccine_name, brand_name);

-- Create update trigger for updated_at
CREATE OR REPLACE FUNCTION update_vaccine_schedules_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_vaccine_schedules_updated_at_trigger
BEFORE UPDATE ON vaccine_schedules
FOR EACH ROW
EXECUTE FUNCTION update_vaccine_schedules_updated_at();

-- Sample data for DTaP vaccine (Infanrix)
INSERT INTO vaccine_schedules (
    vaccine_name, 
    brand_name, 
    manufacturer, 
    dose_number, 
    min_age_weeks, 
    max_age_weeks, 
    interval_from_previous_weeks, 
    preferred_interval_weeks, 
    notes
) VALUES 
-- Dose 1: 2 months (8 weeks)
('DTaP (Diphtheria, Tetanus, and acellular Pertussis)', 'Infanrix', 'GlaxoSmithKline', 1, 6, 16, NULL, 8, 'First dose typically given at 2 months of age'),
-- Dose 2: 4 months (16 weeks) - 8 weeks after first dose
('DTaP (Diphtheria, Tetanus, and acellular Pertussis)', 'Infanrix', 'GlaxoSmithKline', 2, 16, 24, 8, 8, 'Second dose typically given at 4 months of age'),
-- Dose 3: 6 months (24 weeks) - 8 weeks after second dose
('DTaP (Diphtheria, Tetanus, and acellular Pertussis)', 'Infanrix', 'GlaxoSmithKline', 3, 24, 52, 8, 8, 'Third dose typically given at 6 months of age'),
-- Dose 4: 15-18 months (65-78 weeks) - 6 months after third dose
('DTaP (Diphtheria, Tetanus, and acellular Pertussis)', 'Infanrix', 'GlaxoSmithKline', 4, 65, 78, 24, 26, 'Fourth dose typically given at 15-18 months of age'),
-- Dose 5: 4-6 years (208-312 weeks) - final dose
('DTaP (Diphtheria, Tetanus, and acellular Pertussis)', 'Infanrix', 'GlaxoSmithKline', 5, 208, 312, 130, 156, 'Final dose typically given at 4-6 years of age');

-- Sample data for Influenza vaccine (Fluzone)
INSERT INTO vaccine_schedules (
    vaccine_name, 
    brand_name, 
    manufacturer, 
    dose_number, 
    min_age_weeks, 
    max_age_weeks, 
    interval_from_previous_weeks, 
    preferred_interval_weeks, 
    notes
) VALUES 
-- Annual dose
('Influenza (seasonal)', 'Fluzone Quadrivalent', 'Sanofi Pasteur', 1, 26, NULL, NULL, 52, 'Annual vaccination recommended'); 