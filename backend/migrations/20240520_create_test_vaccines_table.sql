-- Create test_vaccines table for API demonstration
-- This table is specifically for the /api/vaccines/simple endpoint

CREATE TABLE IF NOT EXISTS test_vaccines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert some example data
INSERT INTO test_vaccines (name, manufacturer, description)
VALUES 
    ('Flu Vaccine', 'BioPharm', 'Annual influenza vaccine for seasonal flu protection'),
    ('COVID-19 Vaccine', 'ModernTech', 'mRNA-based vaccine against SARS-CoV-2'),
    ('Tdap Vaccine', 'ImmuneCorp', 'Tetanus, diphtheria, and pertussis vaccine for adults'),
    ('Hepatitis B Vaccine', 'LiverShield', 'Vaccine to prevent hepatitis B viral infection'),
    ('HPV Vaccine', 'CancerGuard', 'Human papillomavirus vaccine to prevent certain cancers');

-- Create a view to demonstrate the vaccines API
CREATE OR REPLACE VIEW vw_test_vaccines AS
SELECT 
    id,
    name,
    manufacturer,
    description,
    created_at,
    'Simple API demonstration record' AS note
FROM test_vaccines;

-- Add function to retrieve test vaccines in JSON format
CREATE OR REPLACE FUNCTION get_test_vaccines()
RETURNS JSON AS $$
BEGIN
    RETURN (
        SELECT json_agg(
            json_build_object(
                'id', id,
                'name', name,
                'manufacturer', manufacturer,
                'description', description,
                'created', created_at
            )
        )
        FROM test_vaccines
    );
END;
$$ LANGUAGE plpgsql; 