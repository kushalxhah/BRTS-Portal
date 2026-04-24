-- BRTS Portal Database Schema
-- Run this in phpMyAdmin to create the database structure

CREATE DATABASE IF NOT EXISTS brts_portal;
USE brts_portal;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    password VARCHAR(64) NOT NULL, -- SHA256 hash
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- OTP verification table
CREATE TABLE otps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    otp VARCHAR(6) NOT NULL,
    attempts INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    INDEX idx_email (email),
    INDEX idx_expires (expires_at)
);

-- Tickets table
CREATE TABLE tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    route_name VARCHAR(100) NOT NULL,
    bus_name VARCHAR(50) NOT NULL,
    start_station_id INT NOT NULL,
    end_station_id INT NOT NULL,
    stations_path TEXT NOT NULL,
    quantity INT NOT NULL,
    distance_km INT NOT NULL,
    fare_per_ticket DECIMAL(10,2) NOT NULL,
    total_fare DECIMAL(10,2) NOT NULL,
    payment_method ENUM('UPI', 'Card') NOT NULL,
    payment_details JSON,
    transaction_id VARCHAR(20) UNIQUE NOT NULL,
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_booking_time (booking_time)
);

-- Stations reference table (static data)
CREATE TABLE stations (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8)
);

-- Routes reference table (static data)
CREATE TABLE routes (
    id INT PRIMARY KEY,
    route_name VARCHAR(100) NOT NULL,
    bus_name VARCHAR(50) NOT NULL,
    stations JSON NOT NULL, -- Array of station IDs
    distances JSON NOT NULL, -- Distance mapping
    color VARCHAR(7) DEFAULT '#007bff'
);

-- Insert static station data
INSERT INTO stations (id, name, latitude, longitude) VALUES
(1, 'RTO Circle', 23.0225, 72.5714),
(2, 'Central Bus Stand', 23.0352, 72.5661),
(3, 'City Gold', 23.0395, 72.5758),
(4, 'Nehrunagar', 23.0458, 72.5892),
(5, 'Iskon', 23.0225, 72.5114),
(6, 'Satellite', 23.0265, 72.5060),
(7, 'Maninagar', 23.0103, 72.5992),
(8, 'Vastral', 23.0458, 72.6525),
(9, 'Jivraj Park', 23.0103, 72.6158),
(10, 'Memnagar', 23.0525, 72.5392),
(11, 'Ranip', 23.0703, 72.5514),
(12, 'Gota', 23.1125, 72.5758),
(13, 'Vaishnodevi', 23.0847, 72.5647),
(14, 'Sola', 23.0925, 72.5525),
(15, 'Ghuma Gam', 23.1103, 72.5192),
(16, 'Bhadaj', 23.0758, 72.4892),
(17, 'Thaltej', 23.0547, 72.5092),
(18, 'CTM', 23.0225, 72.6058),
(19, 'Odhav', 23.0558, 72.6625),
(20, 'Hansol', 23.0792, 72.6292),
(21, 'Tragad', 23.1025, 72.6158),
(22, 'Airport', 23.0725, 72.6358),
(23, 'Naroda Gam', 23.0892, 72.6625),
(24, 'Saijpur Bogha', 23.1225, 72.6858),
(25, 'Narol', 22.9758, 72.6525);

-- Insert static route data
INSERT INTO routes (id, route_name, bus_name, stations, distances, color) VALUES
(1, 'RTO to Iskon', 'Bus 101', '[1,2,3,4,5]', '{"1-2":2,"2-3":3,"3-4":2,"4-5":4}', '#28a745'),
(2, 'Central to Vastral', 'Bus 202', '[2,7,8]', '{"2-7":5,"7-8":4}', '#dc3545'),
(3, 'Iskcon to Memnagar', 'Bus 303', '[5,6,9,10]', '{"5-6":3,"6-9":4,"9-10":3}', '#007bff'),
(4, 'Maninagar to Ghuma Gam', 'Bus 404', '[11,12,13,14,15]', '{"11-12":3,"12-13":4,"13-14":2,"14-15":5}', '#fd7e14'),
(5, 'Bhadaj to Odhav', 'Bus 505', '[16,17,2,18,19]', '{"16-17":4,"17-2":3,"2-18":5,"18-19":2}', '#6f42c1'),
(6, 'RTO Circle to Airport', 'Bus 606', '[1,20,21,22]', '{"1-20":6,"20-21":4,"21-22":3}', '#ffc107'),
(7, 'Naroda Gam to Narol', 'Bus 707', '[23,24,25,11]', '{"23-24":3,"24-25":5,"25-11":4}', '#6c757d');

-- Create indexes for better performance
CREATE INDEX idx_otps_cleanup ON otps(expires_at, is_used);
CREATE INDEX idx_tickets_user_date ON tickets(user_id, booking_time);

-- Clean up expired OTPs (run periodically)
-- DELETE FROM otps WHERE expires_at < NOW() OR is_used = TRUE;