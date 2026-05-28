USE ecommerce;

-- Insert Sample Customers
INSERT INTO customers (first_name, last_name, email, registration_date) VALUES
('Alex', 'Johnson', 'alex.j@example.com', '2023-01-15'),
('Maria', 'Garcia', 'maria.g@example.com', '2023-03-22'),
('James', 'Smith', 'james.s@example.com', '2023-06-10'),
('Linda', 'Brown', 'linda.b@example.com', '2023-08-05'),
('Michael', 'Davis', 'michael.d@example.com', '2023-11-20');

-- Insert Sample Products
INSERT INTO products (name, category, price, stock_quantity) VALUES
('Wireless Headphones', 'Electronics', 150.00, 50),
('Mechanical Keyboard', 'Electronics', 120.00, 30),
('Ergonomic Chair', 'Furniture', 250.00, 20),
('Coffee Maker', 'Appliances', 85.00, 40),
('Running Shoes', 'Apparel', 95.00, 60);

-- Insert Sample Orders
INSERT INTO orders (customer_id, order_date, total_amount) VALUES
(1, '2023-02-10', 270.00), -- Alex bought Headphones and Keyboard
(2, '2023-04-15', 250.00), -- Maria bought Chair
(3, '2023-07-01', 190.00), -- James bought Shoes and Shoes
(1, '2023-09-12', 85.00),  -- Alex bought Coffee Maker
(4, '2023-10-05', 400.00), -- Linda bought Chair and Headphones
(5, '2023-12-01', 120.00); -- Michael bought Keyboard

-- Insert Sample Order Items
-- order_id 1 (Alex: Headphones & Keyboard)
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 150.00),
(1, 2, 1, 120.00);

-- order_id 2 (Maria: Chair)
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(2, 3, 1, 250.00);

-- order_id 3 (James: 2x Running Shoes)
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(3, 5, 2, 95.00);

-- order_id 4 (Alex: Coffee Maker)
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(4, 4, 1, 85.00);

-- order_id 5 (Linda: Chair & Headphones)
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(5, 3, 1, 250.00),
(5, 1, 1, 150.00);

-- order_id 6 (Michael: Keyboard)
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(6, 2, 1, 120.00);