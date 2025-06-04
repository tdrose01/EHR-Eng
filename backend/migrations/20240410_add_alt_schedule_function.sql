-- Migration: Add function to get alternative vaccine schedules

-- Function to check for alternative schedules
CREATE OR REPLACE FUNCTION get_vaccine_alternative_schedules(
    p_vaccine_name VARCHAR(255),
    p_brand_name VARCHAR(255),
    p_manufacturer VARCHAR(255),
    p_dose_number INTEGER
)
RETURNS TABLE (
    interval_weeks INTEGER,
    description TEXT
) AS $$
BEGIN
    -- Check if this is the specific vaccine with alternative schedules
    -- Note: Replace 'EXAMPLE_VACCINE' and 'EXAMPLE_BRAND' with actual values when implementing
    IF p_vaccine_name = 'EXAMPLE_VACCINE' AND 
       p_brand_name = 'EXAMPLE_BRAND' AND 
       p_manufacturer = 'EXAMPLE_MANUFACTURER' AND
       p_dose_number = 2 THEN
        
        -- Return both schedule options for dose 2 of this vaccine
        RETURN QUERY SELECT 1::INTEGER, 'Standard schedule: 7 days after first dose'::TEXT
        UNION ALL
        SELECT 4::INTEGER, 'Alternative schedule: 28 days after first dose'::TEXT;
    ELSE
        -- For all other vaccines, check if there's a schedule in the main table
        RETURN QUERY
        SELECT 
            vs.interval_from_previous_weeks,
            'Standard schedule: ' || vs.notes
        FROM vaccine_schedules vs
        WHERE vs.vaccine_name = p_vaccine_name
        AND vs.brand_name = p_brand_name
        AND vs.manufacturer = p_manufacturer
        AND vs.dose_number = p_dose_number
        AND vs.interval_from_previous_weeks IS NOT NULL
        LIMIT 1;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Update the API to provide information about alternative schedules
-- This allows the frontend to present options to the user when applicable 