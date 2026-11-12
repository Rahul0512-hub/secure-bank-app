-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Table for storing transaction descriptions and banking FAQ embeddings
CREATE TABLE IF NOT EXISTS semantic_search_items (
    id SERIAL PRIMARY KEY,
    item_type VARCHAR(20) NOT NULL CHECK (item_type IN ('TRANSACTION', 'FAQ')),
    reference_id INT,
    category VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    amount NUMERIC(12, 2),
    embedding vector(4) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create HNSW vector index for fast cosine similarity search
CREATE INDEX IF NOT EXISTS idx_semantic_items_embedding
ON semantic_search_items USING hnsw (embedding vector_cosine_ops);

-- Seed sample transaction descriptions and FAQs with 4D semantic vectors:
-- Dimensions: [Food/Dining, Travel/Transport, Bills/Utilities, Security/Support]
INSERT INTO semantic_search_items (item_type, reference_id, category, title, description, amount, embedding)
VALUES
('TRANSACTION', 101, 'Food & Dining', 'Starbucks Coffee Indiranagar', 'Morning coffee and croissant purchase via UPI', 450.00, '[0.95, 0.05, 0.05, 0.02]'),
('TRANSACTION', 102, 'Food & Dining', 'Swiggy Dinner Order', 'Late night biryani and soft drinks delivery', 680.00, '[0.92, 0.08, 0.04, 0.01]'),
('TRANSACTION', 103, 'Travel', 'Uber Airport Ride', 'Cab trip to Kempegowda International Airport terminal', 1250.00, '[0.05, 0.96, 0.04, 0.02]'),
('TRANSACTION', 104, 'Travel', 'IndiGo Airlines Flight', 'Domestic flight ticket booking Bengaluru to Mumbai', 5400.00, '[0.04, 0.98, 0.05, 0.01]'),
('TRANSACTION', 105, 'Bills & Utilities', 'BESCOM Electricity Bill', 'Monthly home electricity utility bill payment', 2100.00, '[0.02, 0.03, 0.96, 0.05]'),
('FAQ', 1, 'Security', 'How to block a stolen or lost debit card?', 'Go to Security Settings > Freeze Card immediately or call our 24/7 fraud helpline.', NULL, '[0.01, 0.02, 0.05, 0.98]'),
('FAQ', 2, 'Security', 'Why was my high-value transfer flagged for fraud?', 'Transfers above 50,000 INR trigger real-time velocity and anomaly checks in our Fraud Engine.', NULL, '[0.01, 0.01, 0.10, 0.97]'),
('FAQ', 3, 'Payments', 'How do I increase my daily NEFT/IMPS transfer limit?', 'Navigate to Account Limits and verify with OTP to raise your daily transfer cap up to 5 Lakhs.', NULL, '[0.02, 0.05, 0.65, 0.75]')
ON CONFLICT DO NOTHING;