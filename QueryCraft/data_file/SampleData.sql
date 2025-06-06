-- Create Authors table
CREATE TABLE Authors (
    author_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    birth_date DATE,
    nationality TEXT
);

-- Create Books table
CREATE TABLE Books (
    book_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author_id INTEGER,
    publication_year INTEGER,
    isbn TEXT UNIQUE,
    genre TEXT,
    FOREIGN KEY (author_id) REFERENCES Authors(author_id)
);

-- Create Loans table
CREATE TABLE Loans (
    loan_id INTEGER PRIMARY KEY,
    book_id INTEGER,
    borrower_name TEXT NOT NULL,
    loan_date DATE NOT NULL,
    return_date DATE,
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);

-- Insert sample data for Authors (25 rows)
INSERT INTO Authors (first_name, last_name, birth_date, nationality) VALUES
('Jane', 'Austen', '1775-12-16', 'British'),
('George', 'Orwell', '1903-06-25', 'British'),
('Gabriel', 'García Márquez', '1927-03-06', 'Colombian'),
('Agatha', 'Christie', '1890-09-15', 'British'),
('Haruki', 'Murakami', '1949-01-12', 'Japanese'),
('Virginia', 'Woolf', '1882-01-25', 'British'),
('Leo', 'Tolstoy', '1828-09-09', 'Russian'),
('Chimamanda', 'Ngozi Adichie', '1977-09-15', 'Nigerian'),
('Mark', 'Twain', '1835-11-30', 'American'),
('Isabel', 'Allende', '1942-08-02', 'Chilean'),
('Franz', 'Kafka', '1883-07-03', 'Czech'),
('Toni', 'Morrison', '1931-02-18', 'American'),
('Jorge Luis', 'Borges', '1899-08-24', 'Argentine'),
('Margaret', 'Atwood', '1939-11-18', 'Canadian'),
('Albert', 'Camus', '1913-11-07', 'French'),
('Kazuo', 'Ishiguro', '1954-11-08', 'British'),
('Italo', 'Calvino', '1923-10-15', 'Italian'),
('Ursula K.', 'Le Guin', '1929-10-21', 'American'),
('Milan', 'Kundera', '1929-04-01', 'Czech'),
('Salman', 'Rushdie', '1947-06-19', 'British-Indian'),
('Fyodor', 'Dostoevsky', '1821-11-11', 'Russian'),
('Umberto', 'Eco', '1932-01-05', 'Italian'),
('Alice', 'Munro', '1931-07-10', 'Canadian'),
('J.K.', 'Rowling', '1965-07-31', 'British'),
('Stephen', 'King', '1947-09-21', 'American');

-- Insert sample data for Books (25 rows)
INSERT INTO Books (title, author_id, publication_year, isbn, genre) VALUES
('Pride and Prejudice', 1, 1813, '9780141439518', 'Romance'),
('1984', 2, 1949, '9780451524935', 'Dystopian'),
('One Hundred Years of Solitude', 3, 1967, '9780060883287', 'Magical Realism'),
('Murder on the Orient Express', 4, 1934, '9780062693662', 'Mystery'),
('Norwegian Wood', 5, 1987, '9780375704024', 'Contemporary Fiction'),
('Mrs Dalloway', 6, 1925, '9780156628709', 'Modernist'),
('War and Peace', 7, 1869, '9781400079988', 'Historical Fiction'),
('Americanah', 8, 2013, '9780307455925', 'Contemporary Fiction'),
('The Adventures of Huckleberry Finn', 9, 1884, '9780142437179', 'Adventure'),
('The House of the Spirits', 10, 1982, '9780553383809', 'Magical Realism'),
('The Metamorphosis', 11, 1915, '9780553213690', 'Absurdist Fiction'),
('Beloved', 12, 1987, '9781400033416', 'Historical Fiction'),
('The Aleph', 13, 1949, '9780142437889', 'Short Stories'),
('The Handmaid''s Tale', 14, 1985, '9780385490818', 'Dystopian'),
('The Stranger', 15, 1942, '9780679720201', 'Philosophical Fiction'),
('Never Let Me Go', 16, 2005, '9781400078776', 'Science Fiction'),
('Invisible Cities', 17, 1972, '9780156453806', 'Speculative Fiction'),
('The Left Hand of Darkness', 18, 1969, '9780441007318', 'Science Fiction'),
('The Unbearable Lightness of Being', 19, 1984, '9780060932138', 'Philosophical Fiction'),
('Midnight''s Children', 20, 1981, '9780812976533', 'Magical Realism'),
('Crime and Punishment', 21, 1866, '9780143058144', 'Psychological Fiction'),
('The Name of the Rose', 22, 1980, '9780156001311', 'Historical Mystery'),
('Dear Life', 23, 2012, '9780307743725', 'Short Stories'),
('Harry Potter and the Philosopher''s Stone', 24, 1997, '9780747532699', 'Fantasy'),
('The Shining', 25, 1977, '9780307743657', 'Horror');

-- Insert sample data for Loans (100 rows)
INSERT INTO Loans (book_id, borrower_name, loan_date, return_date)
SELECT 
    CASE 
        WHEN RANDOM() < 0.2 THEN 24 -- Harry Potter (20% chance)
        WHEN RANDOM() < 0.25 THEN 25 -- The Shining (15% chance)
        WHEN RANDOM() < 0.33 THEN 2 -- 1984 (10% chance)
        ELSE (ABS(RANDOM()) % 25) + 1 -- Other books (55% chance)
    END AS book_id,
    'Borrower ' || (ROW_NUMBER() OVER ()) AS borrower_name,
    DATE('2023-01-01', '+' || (ABS(RANDOM()) % 365) || ' days') AS loan_date,
    CASE WHEN RANDOM() < 0.8 THEN DATE('2023-01-01', '+' || (ABS(RANDOM()) % 365 + 14) || ' days') ELSE NULL END AS return_date
FROM (SELECT 1 UNION ALL SELECT 1 UNION ALL SELECT 1 UNION ALL SELECT 1)
CROSS JOIN (SELECT 1 UNION ALL SELECT 1 UNION ALL SELECT 1 UNION ALL SELECT 1 UNION ALL SELECT 1)
LIMIT 100;