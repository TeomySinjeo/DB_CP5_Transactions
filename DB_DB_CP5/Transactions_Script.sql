CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    sender_account_id INT REFERENCES accounts(id),
    receiver_account_id INT REFERENCES accounts(id),
    amount NUMERIC(15, 2) NOT NULL,
    status_id INT REFERENCES transaction_statuses(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);