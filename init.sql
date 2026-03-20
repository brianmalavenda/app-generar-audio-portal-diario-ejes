CREATE DATABASE IF NOT EXISTS ejes_db;
USE ejes_db;

CREATE TABLE IF NOT EXISTS file_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_filename VARCHAR(255) NOT NULL,
    original_path VARCHAR(512) NOT NULL,
    processed_word VARCHAR(255),
    processed_word_path VARCHAR(512),
    processed_word_count INT, -- hace regerencia a la cantidad de palabras del archivo word procesado, no del original
    processed_char_count INT,-- hace regerencia a la cantidad de caracteres del archivo word procesado, no del original
    processed_file_size_mb FLOAT,
    audio_path VARCHAR(512),
    status ENUM('uploaded', 'processed', 'audio_generated', 'error') DEFAULT 'uploaded',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    session_id VARCHAR(255),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_session_id (session_id)
);

