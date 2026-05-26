CREATE TABLE transaction_statuses (
    id SERIAL PRIMARY KEY,
    status_name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO transaction_statuses (status_name) VALUES ('Успешный перевод!'), ('Недостаточно средств');