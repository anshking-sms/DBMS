CREATE DATABASE IF NOT EXISTS food_donation_db;
USE food_donation_db;

CREATE TABLE IF NOT EXISTS donors (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(120),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recipients (
    recipient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    organization VARCHAR(120),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS donations (
    donation_id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    recipient_id INT NULL,
    food_name VARCHAR(120) NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    unit ENUM('kg','boxes','plates','litres','packets') NOT NULL DEFAULT 'kg',
    expiry_time DATETIME NULL,
    status ENUM('Available','Distributed','Expired') NOT NULL DEFAULT 'Available',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_donation_donor FOREIGN KEY (donor_id)
        REFERENCES donors(donor_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_donation_recipient FOREIGN KEY (recipient_id)
        REFERENCES recipients(recipient_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

INSERT INTO donors (name, phone, email, address) VALUES
('Green Leaf Restaurant', '9876543210', 'hello@example.com', 'Pune'),
('Campus Canteen', '9876501234', 'canteen@example.com', 'College Campus');

INSERT INTO recipients (name, phone, organization, address) VALUES
('Hope Shelter', '9898989898', 'Hope Shelter NGO', 'Pune'),
('Community Kitchen', '9765432109', 'Community Kitchen', 'Pune');

INSERT INTO donations (donor_id, food_name, quantity, unit, expiry_time, status, notes) VALUES
(1, 'Fresh vegetable meals', 25, 'plates', DATE_ADD(NOW(), INTERVAL 5 HOUR), 'Available', 'Prepared today'),
(2, 'Bread packets', 12, 'packets', DATE_ADD(NOW(), INTERVAL 8 HOUR), 'Distributed', 'Sample demo record');
