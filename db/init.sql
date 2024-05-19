CREATE ROLE repl_user WITH REPLICATION LOGIN PASSWORD 'kali';
SELECT pg_create_physical_replication_slot('replication_name');

-- Создаем таблицу для хранения email-адресов
CREATE TABLE email_table (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL
);

-- Создаем таблицу для хранения телефонных номеров
CREATE TABLE phone_table (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(255) UNIQUE NOT NULL
);
