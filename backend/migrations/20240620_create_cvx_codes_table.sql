-- Migration: Create CVX codes reference table for vaccines

-- Create table for storing CVX codes
CREATE TABLE IF NOT EXISTS cvx_codes (
    id SERIAL PRIMARY KEY,
    cvx_code VARCHAR(10) NOT NULL UNIQUE,
    vaccine_name VARCHAR(255) NOT NULL,
    short_description VARCHAR(100) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    notes TEXT,
    vaccine_status VARCHAR(20) DEFAULT 'Active',
    last_updated DATE DEFAULT CURRENT_DATE,
    UNIQUE(cvx_code)
);

-- Create index for faster lookups
CREATE INDEX idx_cvx_codes_vaccine_name ON cvx_codes(vaccine_name);

-- Insert some common CVX codes
INSERT INTO cvx_codes (
    cvx_code, vaccine_name, short_description, full_name, notes, vaccine_status
) VALUES
-- Common childhood vaccines
('01', 'DTP', 'DTP', 'Diphtheria, Tetanus, and Pertussis', 'Formulation(s): DTwP', 'Inactive'),
('10', 'IPV', 'IPV', 'Polio virus vaccine, inactivated', 'Injectable polio vaccine', 'Active'),
('20', 'DTaP', 'DTaP', 'Diphtheria, Tetanus, and acellular Pertussis', 'Generic DTaP formulation', 'Active'),
('31', 'Hep A, pediatric', 'Hep A-Ped', 'Hepatitis A pediatric', 'Pediatric formulation', 'Active'),
('33', 'Pneumococcal conjugate', 'PCV', 'Pneumococcal conjugate vaccine, 13 valent', 'PCV13', 'Active'),
('21', 'Varicella', 'Varicella', 'Varicella virus vaccine', 'Chickenpox vaccine', 'Active'),
('94', 'MMR', 'MMR', 'Measles, Mumps, Rubella', 'Combination MMR (live attenuated)', 'Active'),
('115', 'Tdap', 'Tdap', 'Tetanus, diphtheria, and acellular pertussis', 'Adolescent/Adult formulation', 'Active'),
('83', 'Hep A/Hep B', 'Hep A-Hep B', 'Hepatitis A and Hepatitis B', 'Combination vaccine, e.g., Twinrix', 'Active'),
('08', 'Hep B, adolescent', 'Hep B-Adol', 'Hepatitis B, adolescent', 'Adolescent formulation', 'Active'),
('42', 'Hep B, adolescent/high risk', 'Hep B-HighRisk', 'Hepatitis B, adolescent/high risk', 'Adolescent/high risk formulation', 'Active'),
('43', 'Hep B, adult', 'Hep B-Adult', 'Hepatitis B, adult', 'Adult formulation', 'Active'),
('45', 'Hep B, NOS', 'Hep B-NOS', 'Hepatitis B, Not Otherwise Specified', 'Generic Hepatitis B', 'Active'),
('111', 'Influenza, live, intranasal', 'Influenza-Live', 'Influenza, live, intranasal', 'FluMist', 'Active'),
('140', 'Influenza, seasonal, injectable', 'Influenza-Seas', 'Influenza, seasonal, injectable', 'Seasonal influenza', 'Active'),
('141', 'Influenza, seasonal, injectable, preservative free', 'Influenza-Seas-PF', 'Influenza, seasonal, injectable, preservative free', 'Seasonal influenza, preservative free', 'Active'),
('116', 'Rotavirus, pentavalent', 'Rotavirus-5', 'Rotavirus, pentavalent', 'RotaTeq', 'Active'),
('119', 'Rotavirus, monovalent', 'Rotavirus-1', 'Rotavirus, monovalent', 'Rotarix', 'Active'),
('150', 'COVID-19, mRNA', 'COVID-19, mRNA', 'COVID-19, mRNA, LNP-S, PF', 'mRNA COVID-19 vaccines', 'Active'),
('133', 'Pneumococcal conjugate, 13 valent', 'PCV13', 'Pneumococcal conjugate, 13 valent', '13-valent pneumococcal conjugate', 'Active'),
('106', 'DTaP, 5 pertussis antigens', 'DTaP-5', 'DTaP, 5 pertussis antigens', 'Infanrix', 'Active'),
('107', 'DTaP, NOS', 'DTaP-NOS', 'DTaP, Not Otherwise Specified', 'Generic DTaP', 'Active'),
('110', 'DTaP-Hep B-IPV', 'DTaP-Hep B-IPV', 'DTaP-Hepatitis B and Poliovirus', 'Pediarix', 'Active');

-- Create a function to get CVX code for a vaccine
CREATE OR REPLACE FUNCTION get_cvx_code(
    p_vaccine_name VARCHAR(255)
)
RETURNS VARCHAR(10) AS $$
DECLARE
    v_cvx_code VARCHAR(10);
BEGIN
    -- Try to find an exact match first
    SELECT cvx_code INTO v_cvx_code
    FROM cvx_codes
    WHERE LOWER(vaccine_name) = LOWER(p_vaccine_name)
    LIMIT 1;
    
    -- If no exact match, try a partial match
    IF v_cvx_code IS NULL THEN
        SELECT cvx_code INTO v_cvx_code
        FROM cvx_codes
        WHERE LOWER(p_vaccine_name) LIKE '%' || LOWER(vaccine_name) || '%'
           OR LOWER(vaccine_name) LIKE '%' || LOWER(p_vaccine_name) || '%'
        LIMIT 1;
    END IF;
    
    RETURN v_cvx_code;
END;
$$ LANGUAGE plpgsql;

-- Function to update vaccine records with CVX codes
CREATE OR REPLACE FUNCTION update_vaccine_cvx_code()
RETURNS TRIGGER AS $$
BEGIN
    -- Only update cvx_code if it wasn't explicitly set and we have the vaccine name
    IF (NEW.cvx_code IS NULL OR NEW.cvx_code = '') AND NEW.vaccine_name IS NOT NULL THEN
        NEW.cvx_code := get_cvx_code(NEW.vaccine_name);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger to automatically update CVX code
CREATE TRIGGER update_vaccine_cvx_code_trigger
BEFORE INSERT OR UPDATE ON vaccines
FOR EACH ROW
EXECUTE FUNCTION update_vaccine_cvx_code();

-- Backfill CVX codes for existing vaccine records
UPDATE vaccines
SET cvx_code = get_cvx_code(vaccine_name)
WHERE (cvx_code IS NULL OR cvx_code = '')
AND vaccine_name IS NOT NULL; 