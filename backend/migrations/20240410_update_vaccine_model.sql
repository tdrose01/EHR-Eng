-- Migration: Update vaccine model to handle route, site, and adjusted dose amounts by age

-- Create a table for standard administration routes
CREATE TABLE IF NOT EXISTS vaccine_routes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    UNIQUE(code)
);

-- Create a table for standard administration sites
CREATE TABLE IF NOT EXISTS vaccine_sites (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    UNIQUE(code)
);

-- Insert standard routes
INSERT INTO vaccine_routes (code, name, description)
VALUES 
('IM', 'Intramuscular', 'Injection into a muscle'),
('SC', 'Subcutaneous', 'Injection under the skin'),
('ID', 'Intradermal', 'Injection into the dermis layer of skin'),
('PO', 'Oral', 'Administration by mouth'),
('IN', 'Intranasal', 'Administration into the nose')
ON CONFLICT (code) DO NOTHING;

-- Insert standard sites
INSERT INTO vaccine_sites (code, name, description)
VALUES 
('RA', 'Right Arm', 'Right deltoid muscle'),
('LA', 'Left Arm', 'Left deltoid muscle'),
('RT', 'Right Thigh', 'Right anterolateral thigh muscle'),
('LT', 'Left Thigh', 'Left anterolateral thigh muscle'),
('RG', 'Right Gluteal', 'Right gluteal muscle'),
('LG', 'Left Gluteal', 'Left gluteal muscle'),
('AB', 'Abdomen', 'Abdominal area'),
('OR', 'Oral', 'By mouth'),
('IN', 'Intranasal', 'Into the nose')
ON CONFLICT (code) DO NOTHING;

-- Create a table for age-specific dosing
CREATE TABLE IF NOT EXISTS vaccine_age_specific_dosing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vaccine_name VARCHAR(255) NOT NULL,
    brand_name VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(255) NOT NULL,
    min_age_weeks INTEGER,
    max_age_weeks INTEGER,
    dose_amount VARCHAR(20) NOT NULL,
    preferred_route VARCHAR(10) REFERENCES vaccine_routes(code),
    preferred_site VARCHAR(10) REFERENCES vaccine_sites(code),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX idx_vaccine_age_dosing ON vaccine_age_specific_dosing(vaccine_name, brand_name, manufacturer);

-- Insert example data for the provided example vaccine
INSERT INTO vaccine_age_specific_dosing (
    vaccine_name,
    brand_name,
    manufacturer,
    min_age_weeks,
    max_age_weeks,
    dose_amount,
    preferred_route,
    preferred_site,
    notes
) VALUES
-- Adults 18-65 years: 0.5mL
('EXAMPLE_VACCINE', 'EXAMPLE_BRAND', 'EXAMPLE_MANUFACTURER',
 52*18, 52*65, '0.5 mL', 'IM', 'RA',
 'Standard adult dose, administered intramuscularly'),

-- Adults >65 years: 0.5mL
('EXAMPLE_VACCINE', 'EXAMPLE_BRAND_SENIOR', 'EXAMPLE_MANUFACTURER',
 52*65+1, NULL, '0.5 mL', 'IM', 'RA',
 'Standard senior dose, administered intramuscularly');

-- Function to get the appropriate dose amount for a vaccine based on patient age
CREATE OR REPLACE FUNCTION get_vaccine_dose_by_age(
    p_vaccine_name VARCHAR(255),
    p_brand_name VARCHAR(255),
    p_manufacturer VARCHAR(255),
    p_patient_birthdate DATE,
    p_administration_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    dose_amount VARCHAR(20),
    preferred_route VARCHAR(10),
    preferred_site VARCHAR(10),
    route_name VARCHAR(100),
    site_name VARCHAR(100),
    notes TEXT
) AS $$
DECLARE
    patient_age_weeks INTEGER;
BEGIN
    -- Calculate patient age in weeks
    patient_age_weeks := EXTRACT(EPOCH FROM (p_administration_date - p_patient_birthdate)) / (60 * 60 * 24 * 7);
    
    RETURN QUERY
    SELECT 
        d.dose_amount,
        d.preferred_route,
        d.preferred_site,
        r.name AS route_name,
        s.name AS site_name,
        d.notes
    FROM vaccine_age_specific_dosing d
    LEFT JOIN vaccine_routes r ON d.preferred_route = r.code
    LEFT JOIN vaccine_sites s ON d.preferred_site = s.code
    WHERE d.vaccine_name = p_vaccine_name
      AND d.brand_name = p_brand_name
      AND d.manufacturer = p_manufacturer
      AND (d.min_age_weeks IS NULL OR patient_age_weeks >= d.min_age_weeks)
      AND (d.max_age_weeks IS NULL OR patient_age_weeks <= d.max_age_weeks)
    ORDER BY 
        CASE WHEN d.min_age_weeks IS NULL THEN 1 ELSE 0 END,
        CASE WHEN d.max_age_weeks IS NULL THEN 1 ELSE 0 END,
        d.min_age_weeks DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql; 