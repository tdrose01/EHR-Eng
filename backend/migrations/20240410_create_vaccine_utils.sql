-- Migration: Create utility functions for vaccine operations

-- Function to automatically update next_dose_date in vaccines table
CREATE OR REPLACE FUNCTION update_vaccine_next_dose_date()
RETURNS TRIGGER AS $$
DECLARE
    patient_birthdate DATE;
    administration_date DATE;
BEGIN
    -- Get the administration date (record date)
    SELECT date INTO administration_date
    FROM records
    WHERE id = NEW.record_id;
    
    -- Get patient birthdate
    SELECT birth_date INTO patient_birthdate
    FROM patients
    JOIN records ON patients.patient_id = records."patientId"
    WHERE records.id = NEW.record_id;
    
    -- Only update next_dose_date if it wasn't explicitly set and we have all needed data
    IF NEW.next_dose_date IS NULL AND NEW.vaccine_name IS NOT NULL AND NEW.brand_name IS NOT NULL 
       AND NEW.manufacturer IS NOT NULL AND NEW.dose_number IS NOT NULL THEN
       
        NEW.next_dose_date := calculate_next_dose_date(
            NEW.vaccine_name,
            NEW.brand_name,
            NEW.manufacturer,
            NEW.dose_number,
            administration_date,
            patient_birthdate
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger to automatically update next_dose_date
CREATE TRIGGER update_vaccine_next_dose_date_trigger
BEFORE INSERT OR UPDATE ON vaccines
FOR EACH ROW
EXECUTE FUNCTION update_vaccine_next_dose_date();

-- Function to get vaccine schedule information
CREATE OR REPLACE FUNCTION get_vaccine_schedule(
    p_vaccine_name VARCHAR(255),
    p_brand_name VARCHAR(255) DEFAULT NULL,
    p_manufacturer VARCHAR(255) DEFAULT NULL
)
RETURNS TABLE (
    vaccine_name VARCHAR(255),
    brand_name VARCHAR(255),
    manufacturer VARCHAR(255),
    dose_number INTEGER,
    min_age_weeks INTEGER,
    max_age_weeks INTEGER,
    interval_from_previous_weeks INTEGER,
    preferred_interval_weeks INTEGER,
    notes TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        vs.vaccine_name,
        vs.brand_name,
        vs.manufacturer,
        vs.dose_number,
        vs.min_age_weeks,
        vs.max_age_weeks,
        vs.interval_from_previous_weeks,
        vs.preferred_interval_weeks,
        vs.notes
    FROM vaccine_schedules vs
    WHERE vs.vaccine_name = p_vaccine_name
      AND (p_brand_name IS NULL OR vs.brand_name = p_brand_name)
      AND (p_manufacturer IS NULL OR vs.manufacturer = p_manufacturer)
    ORDER BY vs.dose_number;
END;
$$ LANGUAGE plpgsql; 