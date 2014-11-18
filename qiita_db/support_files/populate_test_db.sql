-- Populate.sql sets the increment to begin at 10000, but all tests expect it to start at 1, so set it back to 1 for the test DB population
SELECT setval('qiita.study_study_id_seq', 1, false);

-- Insert some users in the system. Passwords are 'password' for all users
INSERT INTO qiita.qiita_user (email, user_level_id, password, name,
	affiliation, address, phone) VALUES
	('test@foo.bar', 4,
	'$2a$12$gnUi8Qg.0tvW243v889BhOBhWLIHyIJjjgaG6dxuRJkUM8nXG9Efe', 'Dude',
	'Nowhere University', '123 fake st, Apt 0, Faketown, CO 80302',
	'111-222-3344'),
	('shared@foo.bar', 3,
	'$2a$12$gnUi8Qg.0tvW243v889BhOBhWLIHyIJjjgaG6dxuRJkUM8nXG9Efe', 'Shared',
	'Nowhere University', '123 fake st, Apt 0, Faketown, CO 80302',
	'111-222-3344'),
	('admin@foo.bar', 1,
	'$2a$12$gnUi8Qg.0tvW243v889BhOBhWLIHyIJjjgaG6dxuRJkUM8nXG9Efe', 'Admin',
	'Owner University', '312 noname st, Apt K, Nonexistantown, CO 80302',
	'222-444-6789'),
	('demo@microbio.me', 4,
	'$2a$12$gnUi8Qg.0tvW243v889BhOBhWLIHyIJjjgaG6dxuRJkUM8nXG9Efe', 'Demo',
	'Qitta Dev', '1345 Colorado Avenue', '303-492-1984');

-- Insert some study persons
INSERT INTO qiita.study_person (name, email, affiliation, address, phone) VALUES
	('LabDude', 'lab_dude@foo.bar', 'knight lab', '123 lab street', '121-222-3333'),
	('empDude', 'emp_dude@foo.bar', 'broad', NULL, '444-222-3333'),
	('PIDude', 'PI_dude@foo.bar', 'Wash U', '123 PI street', NULL);

-- Insert a study: EMP 1001
INSERT INTO qiita.study (email, study_status_id, emp_person_id, first_contact,
	funding, timeseries_type_id, lab_person_id, metadata_complete,
	mixs_compliant, most_recent_contact, number_samples_collected,
	number_samples_promised, portal_type_id, principal_investigator_id, reprocess,
	spatial_series, study_title, study_alias, study_description,
	study_abstract, vamps_id) VALUES
	('test@foo.bar', 2, 2, '2014-05-19 16:10', NULL, 1, 1, TRUE, TRUE,
	'2014-05-19 16:11', 27, 27, 2, 3, FALSE, FALSE,
	'Identification of the Microbiomes for Cannabis Soils', 'Cannabis Soils', 'Analysis of the Cannabis Plant Microbiome',
	'This is a preliminary study to examine the microbiota associated with the Cannabis plant. Soils samples from the bulk soil, soil associated with the roots, and the rhizosphere were extracted and the DNA sequenced. Roots from three independent plants of different strains were examined. These roots were obtained November 11, 2011 from plants that had been harvested in the summer. Future studies will attempt to analyze the soils and rhizospheres from the same location at different time points in the plant lifecycle.',
	NULL);

-- Insert study_users (share study 1 with shared user)
INSERT INTO qiita.study_users (study_id, email) VALUES (1, 'shared@foo.bar');

-- Insert PMIDs for study
INSERT INTO qiita.study_pmid (study_id, pmid) VALUES (1, '123456'), (1, '7891011');

-- Insert an investigation
INSERT INTO qiita.investigation (name, description, contact_person_id) VALUES
	('TestInvestigation', 'An investigation for testing purposes', 3);

-- Insert investigation_study (link study 1 with investigation 1)
INSERT INTO qiita.investigation_study (investigation_id, study_id) VALUES (1, 1);

-- Insert the study experimental factor for study 1
INSERT INTO qiita.study_experimental_factor (study_id, efo_id) VALUES (1, 1);

-- Insert the raw data filepaths for study 1
INSERT INTO qiita.filepath (filepath, filepath_type_id, checksum, checksum_algorithm_id, data_directory_id) VALUES ('1_s_G1_L001_sequences.fastq.gz', 1, '852952723', 1, 5), ('1_s_G1_L001_sequences_barcodes.fastq.gz', 3, '852952723', 1, 5), ('2_sequences.fastq.gz', 1, '852952723', 1, 5), ('2_sequences_barcodes.fastq.gz', 3, '852952723', 1, 5);

-- Insert the raw data information for study 1
INSERT INTO qiita.raw_data (filetype_id) VALUES (3), (2);

-- Insert (link) the raw data with the raw filepaths
INSERT INTO qiita.raw_filepath (raw_data_id, filepath_id) VALUES (1, 1), (1, 2), (2, 3), (2, 4);

-- Insert (link) the study with the raw data
INSERT INTO qiita.study_raw_data (study_id, raw_data_id) VALUES (1, 1), (1, 2);

-- Add the required_sample_info for study 1
INSERT INTO qiita.required_sample_info (study_id, sample_id, physical_location, has_physical_specimen, has_extracted_data, sample_type, required_sample_info_status_id, collection_timestamp, host_subject_id, description, latitude, longitude) VALUES
	(1, '1.SKB8.640193', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:M7', 'Cannabis Soil Microbiome', 74.0894932572, 65.3283470202),
	(1, '1.SKD8.640184', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:D9', 'Cannabis Soil Microbiome', 57.571893782, 32.5563076447),
	(1, '1.SKB7.640196', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:M8', 'Cannabis Soil Microbiome', 13.089194595, 92.5274472082),
	(1, '1.SKM9.640192', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:B8', 'Cannabis Soil Microbiome', 12.7065957714, 84.9722975792),
	(1, '1.SKM4.640180', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:D2', 'Cannabis Soil Microbiome', 31.7167821863, 95.5088566087),
	(1, '1.SKM5.640177', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:M3', 'Cannabis Soil Microbiome', 44.9725384282, 66.1920014699),
	(1, '1.SKB5.640181', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:M4', 'Cannabis Soil Microbiome', 10.6655599093, 70.784770579),
	(1, '1.SKD6.640190', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:B9', 'Cannabis Soil Microbiome', 29.1499460692, 82.1270418227),
	(1, '1.SKB2.640194', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:B4', 'Cannabis Soil Microbiome', 35.2374368957, 68.5041623253),
	(1, '1.SKD2.640178', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:B5', 'Cannabis Soil Microbiome', 53.5050692395, 31.6056761814),
	(1, '1.SKM7.640188', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:B6', 'Cannabis Soil Microbiome', 60.1102854322, 74.7123248382),
	(1, '1.SKB1.640202', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:M2', 'Cannabis Soil Microbiome', 4.59216095574, 63.5115213108),
	(1, '1.SKD1.640179', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:M5', 'Cannabis Soil Microbiome', 68.0991287718, 34.8360987059),
	(1, '1.SKD3.640198', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:B1', 'Cannabis Soil Microbiome', 84.0030227585, 66.8954849864),
	(1, '1.SKM8.640201', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:D8', 'Cannabis Soil Microbiome', 3.21190859967, 26.8138925876),
	(1, '1.SKM2.640199', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:D4', 'Cannabis Soil Microbiome', 82.8302905615, 86.3615778099),
	(1, '1.SKB9.640200', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:B3', 'Cannabis Soil Microbiome', 12.6245524972, 96.0693176066),
	(1, '1.SKD5.640186', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:M1', 'Cannabis Soil Microbiome', 85.4121476399, 15.6526750776),
	(1, '1.SKM3.640197', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:B7', 'Cannabis Soil Microbiome', 63.6505562766, 31.2003474585),
	(1, '1.SKD9.640182', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:D3', 'Cannabis Soil Microbiome', 23.1218032799, 42.838497795),
	(1, '1.SKB4.640189', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:D7', 'Cannabis Soil Microbiome', 43.9614715197, 82.8516734159),
	(1, '1.SKD7.640191', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:D6', 'Cannabis Soil Microbiome', 68.51099627, 2.35063674718),
	(1, '1.SKM6.640187', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:B2', 'Cannabis Soil Microbiome', 0.291867635913, 68.5945325743),
	(1, '1.SKD4.640185', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:M9', 'Cannabis Soil Microbiome', 40.8623799474, 6.66444220187),
	(1, '1.SKB3.640195', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:M6', 'Cannabis Soil Microbiome', 95.2060749748, 27.3592668624),
	(1, '1.SKB6.640176', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:D5', 'Cannabis Soil Microbiome', 78.3634273709, 74.423907894),
	(1, '1.SKM1.640183', 'ANL', TRUE, TRUE, 'ENVO:soil', 4, '2011-11-11 13:00', '1001:D1', 'Cannabis Soil Microbiome', 38.2627021402, 3.48274264219);

-- Add the study sample columns for study 1
INSERT INTO qiita.study_sample_columns (study_id, column_name, column_type) VALUES
	(1, 'sample_id', 'varchar'),
	(1, 'SEASON_ENVIRONMENT', 'varchar'),
	(1, 'ASSIGNED_FROM_GEO', 'varchar'),
	(1, 'TEXTURE', 'varchar'),
	(1, 'TAXON_ID', 'varchar'),
	(1, 'DEPTH', 'float8'),
	(1, 'HOST_TAXID', 'varchar'),
	(1, 'COMMON_NAME', 'varchar'),
	(1, 'WATER_CONTENT_SOIL', 'float8'),
	(1, 'ELEVATION', 'float8'),
	(1, 'TEMP', 'float8'),
	(1, 'TOT_NITRO', 'float8'),
	(1, 'SAMP_SALINITY', 'float8'),
	(1, 'ALTITUDE', 'float8'),
	(1, 'ENV_BIOME', 'varchar'),
	(1, 'COUNTRY', 'varchar'),
	(1, 'PH', 'float8'),
	(1, 'ANONYMIZED_NAME', 'varchar'),
	(1, 'TOT_ORG_CARB', 'float8'),
	(1, 'Description_duplicate', 'varchar'),
	(1, 'ENV_FEATURE', 'varchar');

-- Crate the sample_1 dynamic table
CREATE TABLE qiita.sample_1 (
	sample_id				varchar,
	SEASON_ENVIRONMENT		varchar,
	ASSIGNED_FROM_GEO		varchar,
	TEXTURE					varchar,
	TAXON_ID				varchar,
	DEPTH					float8,
	HOST_TAXID				varchar,
	COMMON_NAME				varchar,
	WATER_CONTENT_SOIL		float8,
	ELEVATION				float8,
	TEMP					float8,
	TOT_NITRO				float8,
	SAMP_SALINITY			float8,
	ALTITUDE				float8,
	ENV_BIOME				varchar,
	COUNTRY					varchar,
	PH						float8,
	ANONYMIZED_NAME			varchar,
	TOT_ORG_CARB			float8,
	Description_duplicate	varchar,
	ENV_FEATURE				varchar,
	CONSTRAINT pk_sample_1 PRIMARY KEY ( sample_id )
);

-- Populates the sample_1 dynamic table
INSERT INTO qiita.sample_1 (sample_id, SEASON_ENVIRONMENT, ASSIGNED_FROM_GEO, TEXTURE, TAXON_ID, DEPTH, HOST_TAXID, COMMON_NAME, WATER_CONTENT_SOIL, ELEVATION, TEMP, TOT_NITRO, SAMP_SALINITY, ALTITUDE, ENV_BIOME, COUNTRY, PH, ANONYMIZED_NAME, TOT_ORG_CARB, Description_duplicate, ENV_FEATURE) VALUES
	('1.SKM7.640188', 'winter', 'n', '63.1 sand, 17.7 silt, 19.2 clay', '1118232', 0.15, '3483', 'root metagenome', 0.101, 114, 15, 1.3, 7.44, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.82, 'SKM7', 3.31, 'Bucu Roots', 'ENVO:plant-associated habitat'),
	('1.SKD9.640182', 'winter', 'n', '66 sand, 16.3 silt, 17.7 clay', '1118232', 0.15, '3483', 'root metagenome', 0.178, 114, 15, 1.51, 7.1, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.82, 'SKD9', 4.32, 'Diesel Root', 'ENVO:plant-associated habitat'),
	('1.SKM8.640201', 'winter', 'n', '63.1 sand, 17.7 silt, 19.2 clay', '1118232', 0.15, '3483', 'root metagenome', 0.101, 114, 15, 1.3, 7.44, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.82, 'SKM8', 3.31, 'Bucu Roots', 'ENVO:plant-associated habitat'),
	('1.SKB8.640193', 'winter', 'n', '64.6 sand, 17.6 silt, 17.8 clay', '1118232', 0.15, '3483', 'root metagenome', 0.164, 114, 15, 1.41, 7.15, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.94, 'SKB8', 5, 'Burmese root', 'ENVO:plant-associated habitat'),
	('1.SKD2.640178', 'winter', 'n', '66 sand, 16.3 silt, 17.7 clay', '410658', 0.15, '3483', 'soil metagenome', 0.178, 114, 15, 1.51, 7.1, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.8, 'SKD2', 4.32, 'Diesel bulk', 'ENVO:plant-associated habitat'),
	('1.SKM3.640197', 'winter', 'n', '63.1 sand, 17.7 silt, 19.2 clay', '410658', 0.15, '3483', 'soil metagenome', 0.101, 114, 15, 1.3, 7.44, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.82, 'SKM3', 3.31, 'Bucu bulk', 'ENVO:plant-associated habitat'),
	('1.SKM4.640180', 'winter', 'n', '63.1 sand, 17.7 silt, 19.2 clay', '939928', 0.15, '3483', 'rhizosphere metagenome', 0.101, 114, 15, 1.3, 7.44, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.82, 'SKM4', 3.31, 'Bucu Rhizo', 'ENVO:plant-associated habitat'),
	('1.SKB9.640200', 'winter', 'n', '64.6 sand, 17.6 silt, 17.8 clay', '1118232', 0.15, '3483', 'root metagenome', 0.164, 114, 15, 1.41, 7.15, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.8, 'SKB9', 5, 'Burmese root', 'ENVO:plant-associated habitat'),
	('1.SKB4.640189', 'winter', 'n', '64.6 sand, 17.6 silt, 17.8 clay', '939928', 0.15, '3483', 'rhizosphere metagenome', 0.164, 114, 15, 1.41, 7.15, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.94, 'SKB4', 5, 'Burmese Rhizo', 'ENVO:plant-associated habitat'),
	('1.SKB5.640181', 'winter', 'n', '64.6 sand, 17.6 silt, 17.8 clay', '939928', 0.15, '3483', 'rhizosphere metagenome', 0.164, 114, 15, 1.41, 7.15, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.94, 'SKB5', 5, 'Burmese Rhizo', 'ENVO:plant-associated habitat'),
	('1.SKB6.640176', 'winter', 'n', '64.6 sand, 17.6 silt, 17.8 clay', '939928', 0.15, '3483', 'rhizosphere metagenome', 0.164, 114, 15, 1.41, 7.15, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.94, 'SKB6', 5, 'Burmese Rhizo', 'ENVO:plant-associated habitat'),
	('1.SKM2.640199', 'winter', 'n', '63.1 sand, 17.7 silt, 19.2 clay', '410658', 0.15, '3483', 'soil metagenome', 0.101, 114, 15, 1.3, 7.44, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.82, 'SKM2', 3.31, 'Bucu bulk', 'ENVO:plant-associated habitat'),
	('1.SKM5.640177', 'winter', 'n', '63.1 sand, 17.7 silt, 19.2 clay', '939928', 0.15, '3483', 'rhizosphere metagenome', 0.101, 114, 15, 1.3, 7.44, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.82, 'SKM5', 3.31, 'Bucu Rhizo', 'ENVO:plant-associated habitat'),
	('1.SKB1.640202', 'winter', 'n', '64.6 sand, 17.6 silt, 17.8 clay', '410658', 0.15, '3483', 'soil metagenome', 0.164, 114, 15, 1.41, 7.15, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.94, 'SKB1', 5, 'Burmese bulk', 'ENVO:plant-associated habitat'),
	('1.SKD8.640184', 'winter', 'n', '66 sand, 16.3 silt, 17.7 clay', '1118232', 0.15, '3483', 'root metagenome', 0.178, 114, 15, 1.51, 7.1, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.8, 'SKD8', 4.32, 'Diesel Root', 'ENVO:plant-associated habitat'),
	('1.SKD4.640185', 'winter', 'n', '66 sand, 16.3 silt, 17.7 clay', '939928', 0.15, '3483', 'rhizosphere metagenome', 0.178, 114, 15, 1.51, 7.1, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.8, 'SKD4', 4.32, 'Diesel Rhizo', 'ENVO:plant-associated habitat'),
	('1.SKB3.640195', 'winter', 'n', '64.6 sand, 17.6 silt, 17.8 clay', '410658', 0.15, '3483', 'soil metagenome', 0.164, 114, 15, 1.41, 7.15, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.94, 'SKB3', 5, 'Burmese bulk', 'ENVO:plant-associated habitat'),
	('1.SKM1.640183', 'winter', 'n', '63.1 sand, 17.7 silt, 19.2 clay', '410658', 0.15, '3483', 'soil metagenome', 0.101, 114, 15, 1.3, 7.44, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.82, 'SKM1', 3.31, 'Bucu bulk', 'ENVO:plant-associated habitat'),
	('1.SKB7.640196', 'winter', 'n', '64.6 sand, 17.6 silt, 17.8 clay', '1118232', 0.15, '3483', 'root metagenome', 0.164, 114, 15, 1.41, 7.15, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.94, 'SKB7', 5, 'Burmese root', 'ENVO:plant-associated habitat'),
	('1.SKD3.640198', 'winter', 'n', '66 sand, 16.3 silt, 17.7 clay', '410658', 0.15, '3483', 'soil metagenome', 0.178, 114, 15, 1.51, 7.1, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.8, 'SKD3', 4.32, 'Diesel bulk', 'ENVO:plant-associated habitat'),
	('1.SKD7.640191', 'winter', 'n', '66 sand, 16.3 silt, 17.7 clay', '1118232', 0.15, '3483', 'root metagenome', 0.178, 114, 15, 1.51, 7.1, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.8, 'SKD7', 4.32, 'Diesel Root', 'ENVO:plant-associated habitat'),
	('1.SKD6.640190', 'winter', 'n', '66 sand, 16.3 silt, 17.7 clay', '939928', 0.15, '3483', 'rhizosphere metagenome', 0.178, 114, 15, 1.51, 7.1, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.8, 'SKD6', 4.32, 'Diesel Rhizo', 'ENVO:plant-associated habitat'),
	('1.SKB2.640194', 'winter', 'n', '64.6 sand, 17.6 silt, 17.8 clay', '410658', 0.15, '3483', 'soil metagenome', 0.164, 114, 15, 1.41, 7.15, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.94, 'SKB2', 5, 'Burmese bulk', 'ENVO:plant-associated habitat'),
	('1.SKM9.640192', 'winter', 'n', '63.1 sand, 17.7 silt, 19.2 clay', '1118232', 0.15, '3483', 'root metagenome', 0.101, 114, 15, 1.3, 7.44, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.82, 'SKM9', 3.31, 'Bucu Roots', 'ENVO:plant-associated habitat'),
	('1.SKM6.640187', 'winter', 'n', '63.1 sand, 17.7 silt, 19.2 clay', '939928', 0.15, '3483', 'rhizosphere metagenome', 0.101, 114, 15, 1.3, 7.44, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.82, 'SKM6', 3.31, 'Bucu Rhizo', 'ENVO:plant-associated habitat'),
	('1.SKD5.640186', 'winter', 'n', '66 sand, 16.3 silt, 17.7 clay', '939928', 0.15, '3483', 'rhizosphere metagenome', 0.178, 114, 15, 1.51, 7.1, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.8, 'SKD5', 4.32, 'Diesel Rhizo', 'ENVO:plant-associated habitat'),
	('1.SKD1.640179', 'winter', 'n', '66 sand, 16.3 silt, 17.7 clay', '410658', 0.15, '3483', 'soil metagenome', 0.178, 114, 15, 1.51, 7.1, 0, 'ENVO:Temperate grasslands, savannas, and shrubland biome', 'GAZ:United States of America', 6.8, 'SKD1', 4.32, 'Diesel bulk', 'ENVO:plant-associated habitat');

-- Create a new prep template for the added raw data
INSERT INTO qiita.prep_template (data_type_id, raw_data_id, preprocessing_status, investigation_type) VALUES (2, 1, 'success', 'Metagenomics');

-- Add the common prep info for study 1
INSERT INTO qiita.common_prep_info (prep_template_id, sample_id, center_name, center_project_name, emp_status_id) VALUES
	(1, '1.SKB8.640193', 'ANL', NULL, 1),
	(1, '1.SKD8.640184', 'ANL', NULL, 1),
	(1, '1.SKB7.640196', 'ANL', NULL, 1),
	(1, '1.SKM9.640192', 'ANL', NULL, 1),
	(1, '1.SKM4.640180', 'ANL', NULL, 1),
	(1, '1.SKM5.640177', 'ANL', NULL, 1),
	(1, '1.SKB5.640181', 'ANL', NULL, 1),
	(1, '1.SKD6.640190', 'ANL', NULL, 1),
	(1, '1.SKB2.640194', 'ANL', NULL, 1),
	(1, '1.SKD2.640178', 'ANL', NULL, 1),
	(1, '1.SKM7.640188', 'ANL', NULL, 1),
	(1, '1.SKB1.640202', 'ANL', NULL, 1),
	(1, '1.SKD1.640179', 'ANL', NULL, 1),
	(1, '1.SKD3.640198', 'ANL', NULL, 1),
	(1, '1.SKM8.640201', 'ANL', NULL, 1),
	(1, '1.SKM2.640199', 'ANL', NULL, 1),
	(1, '1.SKB9.640200', 'ANL', NULL, 1),
	(1, '1.SKD5.640186', 'ANL', NULL, 1),
	(1, '1.SKM3.640197', 'ANL', NULL, 1),
	(1, '1.SKD9.640182', 'ANL', NULL, 1),
	(1, '1.SKB4.640189', 'ANL', NULL, 1),
	(1, '1.SKD7.640191', 'ANL', NULL, 1),
	(1, '1.SKM6.640187', 'ANL', NULL, 1),
	(1, '1.SKD4.640185', 'ANL', NULL, 1),
	(1, '1.SKB3.640195', 'ANL', NULL, 1),
	(1, '1.SKB6.640176', 'ANL', NULL, 1),
	(1, '1.SKM1.640183', 'ANL', NULL, 1);

-- Add raw data prep columns
INSERT INTO qiita.prep_columns (prep_template_id, column_name, column_type) VALUES
	(1, 'sample_id', 'varchar'),
	(1, 'BarcodeSequence', 'varchar'),
	(1, 'LIBRARY_CONSTRUCTION_PROTOCOL', 'varchar'),
	(1, 'LinkerPrimerSequence', 'varchar'),
	(1, 'TARGET_SUBFRAGMENT', 'varchar'),
	(1, 'target_gene', 'varchar'),
	(1, 'RUN_CENTER', 'varchar'),
	(1, 'RUN_PREFIX', 'varchar'),
	(1, 'RUN_DATE', 'varchar'),
	(1, 'EXPERIMENT_CENTER', 'varchar'),
	(1, 'EXPERIMENT_DESIGN_DESCRIPTION', 'varchar'),
	(1, 'EXPERIMENT_TITLE', 'varchar'),
	(1, 'PLATFORM', 'varchar'),
	(1, 'SAMP_SIZE', 'varchar'),
	(1, 'SEQUENCING_METH', 'varchar'),
	(1, 'illumina_technology', 'varchar'),
	(1, 'SAMPLE_CENTER', 'varchar'),
	(1, 'pcr_primers', 'varchar'),
	(1, 'STUDY_CENTER', 'varchar');

-- Crate the prep_1 dynamic table
CREATE TABLE qiita.prep_1 (
	sample_id						varchar,
	BarcodeSequence					varchar,
	LIBRARY_CONSTRUCTION_PROTOCOL	varchar,
	LinkerPrimerSequence			varchar,
	TARGET_SUBFRAGMENT				varchar,
	target_gene						varchar,
	RUN_CENTER						varchar,
	RUN_PREFIX						varchar,
	RUN_DATE						varchar,
	EXPERIMENT_CENTER				varchar,
	EXPERIMENT_DESIGN_DESCRIPTION	varchar,
	EXPERIMENT_TITLE				varchar,
	PLATFORM						varchar,
	SAMP_SIZE						varchar,
	SEQUENCING_METH					varchar,
	illumina_technology				varchar,
	SAMPLE_CENTER					varchar,
	pcr_primers						varchar,
	STUDY_CENTER					varchar,
	CONSTRAINT pk_prep_1 PRIMARY KEY ( sample_id )
);

-- Populates the prep_1 dynamic table
INSERT INTO qiita.prep_1 (sample_id, BarcodeSequence, LIBRARY_CONSTRUCTION_PROTOCOL, LinkerPrimerSequence, TARGET_SUBFRAGMENT, target_gene, RUN_CENTER, RUN_PREFIX, RUN_DATE, EXPERIMENT_CENTER, EXPERIMENT_DESIGN_DESCRIPTION, EXPERIMENT_TITLE, PLATFORM, SAMP_SIZE, SEQUENCING_METH, illumina_technology, SAMPLE_CENTER, pcr_primers, STUDY_CENTER) VALUES
	('1.SKB1.640202', 'GTCCGCAAGTTA', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKB2.640194', 'CGTAGAGCTCTC', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKB3.640195', 'CCTCTGAGAGCT', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKB4.640189', 'CCTCGATGCAGT', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKB5.640181', 'GCGGACTATTCA', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKB6.640176', 'CGTGCACAATTG', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKB7.640196', 'CGGCCTAAGTTC', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKB8.640193', 'AGCGCTCACATC', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKB9.640200', 'TGGTTATGGCAC', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKD1.640179', 'CGAGGTTCTGAT', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKD2.640178', 'AACTCCTGTGGA', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKD3.640198', 'TAATGGTCGTAG', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKD4.640185', 'TTGCACCGTCGA', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKD5.640186', 'TGCTACAGACGT', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKD6.640190', 'ATGGCCTGACTA', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKD7.640191', 'ACGCACATACAA', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKD8.640184', 'TGAGTGGTCTGT', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKD9.640182', 'GATAGCACTCGT', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKM1.640183', 'TAGCGCGAACTT', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKM2.640199', 'CATACACGCACC', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKM3.640197', 'ACCTCAGTCAAG', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKM4.640180', 'TCGACCAAACAC', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKM5.640177', 'CCACCCAGTAAC', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKM6.640187', 'ATATCGCGATGA', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKM7.640188', 'CGCCGGTAATCT', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKM8.640201', 'CCGATGCCTTGA', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME'),
	('1.SKM9.640192', 'AGCAGGCACGAA', 'This analysis was done as in Caporaso et al 2011 Genome research. The PCR primers (F515/R806) were developed against the V4 region of the 16S rRNA (both bacteria and archaea), which we determined would yield optimal community clustering with reads of this length using a procedure similar to that of ref. 15. [For reference, this primer pair amplifies the region 533_786 in the Escherichia coli strain 83972 sequence (greengenes accession no. prokMSA_id:470367).] The reverse PCR primer is barcoded with a 12-base error-correcting Golay code to facilitate multiplexing of up to 1,500 samples per lane, and both PCR primers contain sequencer adapter regions.', 'GTGCCAGCMGCCGCGGTAA', 'V4', '16S rRNA', 'ANL', 's_G1_L001_sequences', '8/1/12', 'ANL', 'micro biome of soil and rhizosphere of cannabis plants from CA', 'Cannabis Soil Microbiome', 'Illumina', '.25,g', 'Sequencing by synthesis', 'MiSeq', 'ANL', 'FWD:GTGCCAGCMGCCGCGGTAA; REV:GGACTACHVGGGTWTCTAAT', 'CCME');

-- Insert preprocessed information for raw data 1
INSERT INTO qiita.preprocessed_data (preprocessed_params_table, preprocessed_params_id, submitted_to_insdc_status, ebi_submission_accession, ebi_study_accession, data_type_id) VALUES ('preprocessed_sequence_illumina_params', 1, 'submitting', 'EBI123456-AA', 'EBI123456-BB', 2), ('preprocessed_sequence_illumina_params', 2, 'not submitted', NULL, NULL, 2);

-- Link the new preprocessed data with the raw data
INSERT INTO qiita.prep_template_preprocessed_data (prep_template_id, preprocessed_data_id) VALUES (1, 1), (1, 2);

-- Insert (link) preprocessed information to study 1
INSERT INTO qiita.study_preprocessed_data (preprocessed_data_id, study_id) VALUES (1, 1), (2, 1);

-- Insert the preprocessed filepath for raw data 1
INSERT INTO qiita.filepath (filepath, filepath_type_id, checksum, checksum_algorithm_id, data_directory_id) VALUES ('1_seqs.fna', 4, '852952723', 1, 3), ('1_seqs.qual', 5, '852952723', 1, 3), ('1_seqs.demux', 6, 852952723, 1, 3);

-- Insert (link) the preprocessed data with the preprocessed filepaths
INSERT INTO qiita.preprocessed_filepath (preprocessed_data_id, filepath_id) VALUES (1, 5), (1, 6), (1, 7);

-- Insert processed information for study 0 and processed data 1
INSERT INTO qiita.processed_data (processed_params_table, processed_params_id, processed_date, data_type_id) VALUES ('processed_params_uclust', 1, 'Mon Oct 1 09:30:27 2012', 2);

-- Insert (link) processed information to study 1
INSERT INTO qiita.study_processed_data (processed_data_id, study_id) VALUES (1, 1);

-- Link the processed data with the preprocessed data
INSERT INTO qiita.preprocessed_processed_data (preprocessed_data_id, processed_data_id) VALUES (1, 1);

-- Insert the reference files for reference 1
INSERT INTO qiita.filepath (filepath, filepath_type_id, checksum, checksum_algorithm_id, data_directory_id) VALUES ('GreenGenes_13_8_97_otus.fasta', 10, '852952723', 1, 6), ('GreenGenes_13_8_97_otu_taxonomy.txt', 11, '852952723', 1, 6), ('GreenGenes_13_8_97_otus.tree', 12, '852952723', 1, 6);

-- Populate the reference table
INSERT INTO qiita.reference (reference_name, reference_version, sequence_filepath, taxonomy_filepath, tree_filepath) VALUES ('Greengenes', '13_8', 8, 9, 10);

-- Insert the processed params uclust used for preprocessed data 1
INSERT INTO qiita.processed_params_uclust (similarity, enable_rev_strand_match, suppress_new_clusters, reference_id) VALUES (0.97, TRUE, TRUE, 1);

-- Insert the biom table filepath for processed data 1
INSERT INTO qiita.filepath (filepath, filepath_type_id, checksum, checksum_algorithm_id, data_directory_id) VALUES ('1_study_1001_closed_reference_otu_table.biom', 7, '852952723', 1, 4);

-- Insert (link) the processed data with the processed filepath
INSERT INTO qiita.processed_filepath (processed_data_id, filepath_id) VALUES (1, 11);

-- Insert filepath for job results files
INSERT INTO qiita.filepath (filepath, filepath_type_id, checksum, checksum_algorithm_id, data_directory_id) VALUES ('1_job_result.txt', 9, '852952723', 1, 2), ('2_test_folder', 8, '852952723', 1, 2);

-- Insert jobs
INSERT INTO qiita.job (data_type_id, job_status_id, command_id, options) VALUES (2, 1, 1, '{"--otu_table_fp":1}'), (2, 3, 2, '{"--mapping_fp":1,"--otu_table_fp":1}'), (2, 1, 2, '{"--mapping_fp":1,"--otu_table_fp":1}');

-- Insert Analysis
INSERT INTO qiita.analysis (email, name, description, analysis_status_id, pmid) VALUES ('test@foo.bar', 'SomeAnalysis', 'A test analysis', 1, '121112'), ('test@foo.bar', 'SomeSecondAnalysis', 'Another test analysis', 1, '22221112');

-- Insert Analysis Workflow
INSERT INTO qiita.analysis_workflow (analysis_id, step) VALUES (1, 3), (2, 3);

-- Attach jobs to analysis
INSERT INTO qiita.analysis_job (analysis_id, job_id) VALUES (1, 1), (1, 2), (2, 3);

-- Insert filepath for analysis biom files
INSERT INTO qiita.filepath (filepath, filepath_type_id, checksum, checksum_algorithm_id, data_directory_id) VALUES ('1_analysis_18S.biom', 7, '852952723', 1, 1), ('1_analysis_mapping.txt', 9, '852952723', 1, 1);

-- Attach filepath to analysis
INSERT INTO qiita.analysis_filepath (analysis_id, filepath_id, data_type_id) VALUES (1, 14, 2), (1, 15, NULL);

-- Attach samples to analysis
INSERT INTO qiita.analysis_sample (analysis_id, processed_data_id, sample_id) VALUES (1,1,'1.SKB8.640193'), (1,1,'1.SKD8.640184'), (1,1,'1.SKB7.640196'), (1,1,'1.SKM9.640192'), (1,1,'1.SKM4.640180'), (2,1,'1.SKB8.640193'), (2,1,'1.SKD8.640184'), (2,1,'1.SKB7.640196'), (2,1,'1.SKM3.640197');

--Share analysis with shared user
INSERT INTO qiita.analysis_users (analysis_id, email) VALUES (1, 'shared@foo.bar');

-- Add job results
INSERT INTO qiita.job_results_filepath (job_id, filepath_id) VALUES (1, 12), (2, 13);

-- Add an ontology
INSERT INTO qiita.ontology (ontology_id, ontology, fully_loaded, fullname, query_url, source_url, definition, load_date) VALUES (999999999, E'ENA', E'1', E'European Nucleotide Archive Submission Ontology', NULL, E'http://www.ebi.ac.uk/embl/Documentation/ENA-Reads.html', E'The ENA CV is to be used to annotate XML submissions to the ENA.', '2009-02-23 00:00:00');

-- Add some ontology values
INSERT INTO qiita.term (term_id, ontology_id, term, identifier, definition, namespace, is_obsolete, is_root_term, is_leaf) VALUES (2052508974, 999999999, E'Whole Genome Sequencing', E'ENA:0000059', NULL, NULL, NULL, NULL, NULL);
INSERT INTO qiita.term (term_id, ontology_id, term, identifier, definition, namespace, is_obsolete, is_root_term, is_leaf) VALUES (2052508975, 999999999, E'Metagenomics', E'ENA:0000060', NULL, NULL, NULL, NULL, NULL);
INSERT INTO qiita.term (term_id, ontology_id, term, identifier, definition, namespace, is_obsolete, is_root_term, is_leaf) VALUES (2052508976, 999999999, E'Transcriptome Analysis', E'ENA:0000061', NULL, NULL, NULL, NULL, NULL);
INSERT INTO qiita.term (term_id, ontology_id, term, identifier, definition, namespace, is_obsolete, is_root_term, is_leaf) VALUES (2052508977, 999999999, E'Resequencing', E'ENA:0000062', NULL, NULL, NULL, NULL, NULL);
INSERT INTO qiita.term (term_id, ontology_id, term, identifier, definition, namespace, is_obsolete, is_root_term, is_leaf) VALUES (2052508978, 999999999, E'Epigenetics', E'ENA:0000066', NULL, NULL, NULL, NULL, NULL);
INSERT INTO qiita.term (term_id, ontology_id, term, identifier, definition, namespace, is_obsolete, is_root_term, is_leaf) VALUES (2052508979, 999999999, E'Synthetic Genomics', E'ENA:0000067', NULL, NULL, NULL, NULL, NULL);
INSERT INTO qiita.term (term_id, ontology_id, term, identifier, definition, namespace, is_obsolete, is_root_term, is_leaf) VALUES (2052508980, 999999999, E'Forensic or Paleo-genomics', E'ENA:0000065', NULL, NULL, NULL, NULL, NULL);
INSERT INTO qiita.term (term_id, ontology_id, term, identifier, definition, namespace, is_obsolete, is_root_term, is_leaf) VALUES (2052508981, 999999999, E'Gene Regulation Study', E'ENA:0000068', NULL, NULL, NULL, NULL, NULL);
INSERT INTO qiita.term (term_id, ontology_id, term, identifier, definition, namespace, is_obsolete, is_root_term, is_leaf) VALUES (2052508982, 999999999, E'Cancer Genomics', E'ENA:0000063', NULL, NULL, NULL, NULL, NULL);
INSERT INTO qiita.term (term_id, ontology_id, term, identifier, definition, namespace, is_obsolete, is_root_term, is_leaf) VALUES (2052508983, 999999999, E'Population Genomics', E'ENA:0000064', NULL, NULL, NULL, NULL, NULL);
INSERT INTO qiita.term (term_id, ontology_id, term, identifier, definition, namespace, is_obsolete, is_root_term, is_leaf) VALUES (2052508984, 999999999, E'RNASeq', E'ENA:0000070', NULL, NULL, NULL, NULL, NULL);
INSERT INTO qiita.term (term_id, ontology_id, term, identifier, definition, namespace, is_obsolete, is_root_term, is_leaf) VALUES (2052508985, 999999999, E'Exome Sequencing', E'ENA:0000071', NULL, NULL, NULL, NULL, NULL);
INSERT INTO qiita.term (term_id, ontology_id, term, identifier, definition, namespace, is_obsolete, is_root_term, is_leaf) VALUES (2052508986, 999999999, E'Pooled Clone Sequencing', E'ENA:0000072', NULL, NULL, NULL, NULL, NULL);
INSERT INTO qiita.term (term_id, ontology_id, term, identifier, definition, namespace, is_obsolete, is_root_term, is_leaf) VALUES (2052508987, 999999999, E'Other', E'ENA:0000069', NULL, NULL, NULL, NULL, NULL);
