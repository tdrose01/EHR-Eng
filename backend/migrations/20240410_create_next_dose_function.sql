-- Migration: Create a function to calculate the next dose date based on vaccine schedules

-- Create function to calculate next dose date
CREATE OR REPLACE FUNCTION calculate_next_dose_date(
    p_vaccine_name VARCHAR(255),
    p_brand_name VARCHAR(255),
    p_manufacturer VARCHAR(255),
    p_current_dose_number INTEGER,
    p_administration_date DATE,
    p_patient_birthdate DATE DEFAULT NULL
)
RETURNS DATE AS $$
DECLARE
    next_dose_date DATE;
    next_dose_record RECORD;
    patient_age_weeks INTEGER;
BEGIN
    -- Check if there is a next dose in the schedule
    SELECT * INTO next_dose_record
    FROM vaccine_schedules
    WHERE vaccine_name = p_vaccine_name
    AND brand_name = p_brand_name
    AND manufacturer = p_manufacturer
    AND dose_number = p_current_dose_number + 1;
    
    -- If no next dose found, return NULL (no future dose needed)
    IF next_dose_record IS NULL THEN
        RETURN NULL;
    END IF;
    
    -- Calculate the next dose date based on schedule
    IF next_dose_record.interval_from_previous_weeks IS NOT NULL THEN
        -- Base calculation on interval from previous dose
        next_dose_date := p_administration_date + (next_dose_record.interval_from_previous_weeks * 7 * INTERVAL '1 day');
    ELSIF p_patient_birthdate IS NOT NULL AND next_dose_record.preferred_interval_weeks IS NOT NULL THEN
        -- If we have the patient's birth date, calculate based on age
        patient_age_weeks := EXTRACT(EPOCH FROM (p_administration_date - p_patient_birthdate)) / (60 * 60 * 24 * 7);
        
        -- Check if patient is already old enough for next dose
        IF patient_age_weeks >= next_dose_record.min_age_weeks THEN
            -- If patient is already old enough, use preferred interval
            next_dose_date := p_administration_date + (next_dose_record.preferred_interval_weeks * 7 * INTERVAL '1 day');
        ELSE
            -- Calculate date when patient reaches minimum age for next dose
            next_dose_date := p_patient_birthdate + (next_dose_record.min_age_weeks * 7 * INTERVAL '1 day');
        END IF;
    ELSE
        -- Fall back to preferred interval if we have it
        IF next_dose_record.preferred_interval_weeks IS NOT NULL THEN
            next_dose_date := p_administration_date + (next_dose_record.preferred_interval_weeks * 7 * INTERVAL '1 day');
        ELSE
            -- No usable interval information
            RETURN NULL;
        END IF;
    END IF;
    
    RETURN next_dose_date;
END;
$$ LANGUAGE plpgsql; 