-- Migration: Add example adult vaccine schedule

-- Insert example vaccine for adults (note: replace EXAMPLE_VACCINE with actual vaccine name)
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
-- Dose 1: First dose for adults 18-65 years
('EXAMPLE_VACCINE', 'EXAMPLE_BRAND', 'EXAMPLE_MANUFACTURER', 1, 
 52*18, -- min age: 18 years in weeks
 52*65, -- max age: 65 years in weeks
 NULL, -- no previous interval for first dose
 0, -- no wait time for first dose
 'First dose for adults 18-65 years of age. Intramuscular administration only. Dose amount: 0.5 mL'),

-- Dose 2: Second dose for adults 18-65 years (primary option - 7 days apart)
('EXAMPLE_VACCINE', 'EXAMPLE_BRAND', 'EXAMPLE_MANUFACTURER', 2, 
 52*18, -- min age: 18 years in weeks
 52*65, -- max age: 65 years in weeks
 1, -- 7 days = 1 week interval from previous dose
 1, -- preferred interval: 1 week
 'Second dose for adults 18-65 years of age. Intramuscular administration only. Dose amount: 0.5 mL. Administer 7 days after first dose.'),

-- Dose 1: First dose for adults over 65 years
('EXAMPLE_VACCINE', 'EXAMPLE_BRAND_SENIOR', 'EXAMPLE_MANUFACTURER', 1, 
 52*65+1, -- min age: just over 65 years in weeks
 NULL, -- no max age
 NULL, -- no previous interval for first dose
 0, -- no wait time for first dose
 'First dose for adults over 65 years of age. Intramuscular administration only. Dose amount: 0.5 mL'),

-- Dose 2: Second dose for adults over 65 years (28 days apart)
('EXAMPLE_VACCINE', 'EXAMPLE_BRAND_SENIOR', 'EXAMPLE_MANUFACTURER', 2, 
 52*65+1, -- min age: just over 65 years in weeks
 NULL, -- no max age
 4, -- 28 days = 4 weeks interval from previous dose
 4, -- preferred interval: 4 weeks
 'Second dose for adults over 65 years of age. Intramuscular administration only. Dose amount: 0.5 mL. Administer 28 days after first dose.');

-- Note: For adults 18-65, the alternative schedule (28 days apart) can be handled in the application 
-- logic by providing an option to choose between the two schedules when recording the first dose.
-- Alternatively, we could create another brand entry with the 28-day schedule. 