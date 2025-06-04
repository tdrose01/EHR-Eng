-- Sample data for vaccines table

-- Create a sample DTaP vaccination record
WITH new_record AS (
    INSERT INTO records (
        "patientId", 
        type, 
        provider, 
        date, 
        status, 
        notes
    ) 
    VALUES (
        (SELECT patient_id FROM patients ORDER BY RANDOM() LIMIT 1), -- Random patient
        'Vaccination',
        'Dr. Elizabeth Chen',
        CURRENT_DATE - INTERVAL '2 months',
        'Completed',
        'Patient received DTaP vaccine as part of routine childhood immunization schedule. No immediate adverse reactions observed.'
    )
    RETURNING id
),
new_vaccine AS (
    INSERT INTO vaccines (
        record_id,
        vaccine_name,
        brand_name,
        manufacturer,
        cvx_code,
        ndc_code,
        lot_number,
        dose_amount,
        route,
        site,
        dose_number,
        total_doses,
        -- next_dose_date will be automatically calculated by the trigger
        contraindications,
        storage_requirements,
        additional_notes
    )
    VALUES (
        (SELECT id FROM new_record),
        'DTaP (Diphtheria, Tetanus, and acellular Pertussis)',
        'Infanrix',
        'GlaxoSmithKline',
        '106',
        '58160-810-11',
        'AC52B278',
        '0.5 mL',
        'IM',
        'RA',
        2,
        5,
        'Severe allergic reaction to previous dose or any vaccine component. Encephalopathy within 7 days of a previous pertussis-containing vaccine.',
        'Store refrigerated at 2°C to 8°C (36°F to 46°F). Do not freeze. Discard if the vaccine has been frozen.',
        'Infanrix contains aluminum as an adjuvant. The tip caps of the prefilled syringes contain natural rubber latex which may cause allergic reactions in latex-sensitive individuals.'
    )
    RETURNING id
)
UPDATE records 
SET vaccine_id = (SELECT id FROM new_vaccine) 
WHERE id = (SELECT id FROM new_record);

-- Create another sample vaccination record (Influenza)
WITH new_record AS (
    INSERT INTO records (
        "patientId", 
        type, 
        provider, 
        date, 
        status, 
        notes
    ) 
    VALUES (
        (SELECT patient_id FROM patients ORDER BY RANDOM() LIMIT 1), -- Random patient
        'Vaccination',
        'Dr. James Wilson',
        CURRENT_DATE - INTERVAL '3 weeks',
        'Completed',
        'Annual influenza vaccination administered. Patient tolerated procedure well.'
    )
    RETURNING id
),
new_vaccine AS (
    INSERT INTO vaccines (
        record_id,
        vaccine_name,
        brand_name,
        manufacturer,
        cvx_code,
        ndc_code,
        lot_number,
        dose_amount,
        route,
        site,
        dose_number,
        total_doses,
        -- next_dose_date will be automatically calculated by the trigger
        contraindications,
        storage_requirements,
        additional_notes
    )
    VALUES (
        (SELECT id FROM new_record),
        'Influenza (seasonal)',
        'Fluzone Quadrivalent',
        'Sanofi Pasteur',
        '158',
        '49281-0421-50',
        'D8877456A',
        '0.5 mL',
        'IM',
        'LD',
        1,
        1,
        'Severe allergic reaction to any component of the vaccine, including egg protein, or after previous dose of any influenza vaccine.',
        'Store refrigerated at 2°C to 8°C (36°F to 46°F). Do not freeze. Discard if product has been frozen.',
        'Contains inactivated influenza viruses, covering four strains: two influenza A viruses and two influenza B viruses.'
    )
    RETURNING id
)
UPDATE records 
SET vaccine_id = (SELECT id FROM new_vaccine) 
WHERE id = (SELECT id FROM new_record); 