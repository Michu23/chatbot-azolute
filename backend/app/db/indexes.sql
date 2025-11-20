-- Performance optimization indexes for Azolute AI Chatbot

-- Users table indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);

-- Organizations table indexes
CREATE INDEX IF NOT EXISTS idx_organizations_owner_id ON organizations(owner_id);
CREATE INDEX IF NOT EXISTS idx_organizations_slug ON organizations(slug);
CREATE INDEX IF NOT EXISTS idx_organizations_is_active ON organizations(is_active);

-- Bots table indexes
CREATE INDEX IF NOT EXISTS idx_bots_organization_id ON bots(organization_id);
CREATE INDEX IF NOT EXISTS idx_bots_bot_id ON bots(bot_id);
CREATE INDEX IF NOT EXISTS idx_bots_is_active ON bots(is_active);

-- Chat sessions table indexes
CREATE INDEX IF NOT EXISTS idx_chat_sessions_bot_id ON chat_sessions(bot_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_visitor_id ON chat_sessions(visitor_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_visitor_email ON chat_sessions(visitor_email);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_last_message_at ON chat_sessions(last_message_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_status ON chat_sessions(status);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_is_lead ON chat_sessions(is_lead);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_chat_sessions_bot_status ON chat_sessions(bot_id, status, last_message_at DESC);

-- Chat messages table indexes
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_role ON chat_messages(role);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_messages_used_rag ON chat_messages(used_rag);

-- Composite index for message history queries
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created ON chat_messages(session_id, created_at DESC);

-- Leads table indexes
CREATE INDEX IF NOT EXISTS idx_leads_session_id ON leads(session_id);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_leads_is_qualified ON leads(is_qualified);
CREATE INDEX IF NOT EXISTS idx_leads_is_contacted ON leads(is_contacted);

-- Knowledge sources table indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_sources_bot_id ON knowledge_sources(bot_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_sources_source_type ON knowledge_sources(source_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_sources_status ON knowledge_sources(status);

-- Documents table indexes
CREATE INDEX IF NOT EXISTS idx_documents_source_id ON documents(source_id);
CREATE INDEX IF NOT EXISTS idx_documents_url ON documents(url);

-- Document chunks table indexes
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_chunk_index ON document_chunks(chunk_index);

-- Vector similarity search index (IVFFlat for better performance on larger datasets)
-- Adjust 'lists' parameter based on dataset size (typically sqrt of number of rows)
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding
ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Alternatively, use HNSW for even better query performance (requires pgvector 0.5.0+)
-- CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_hnsw
-- ON document_chunks
-- USING hnsw (embedding vector_cosine_ops);

-- API keys table indexes
CREATE INDEX IF NOT EXISTS idx_api_keys_organization_id ON api_keys(organization_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_key ON api_keys(key);
CREATE INDEX IF NOT EXISTS idx_api_keys_is_active ON api_keys(is_active);

-- Refresh tokens table indexes
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

-- Performance monitoring queries
-- Use these to analyze index usage and query performance

-- Check index usage
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
-- FROM pg_stat_user_indexes
-- ORDER BY idx_scan DESC;

-- Check table sizes
-- SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
-- FROM pg_tables
-- WHERE schemaname = 'public'
-- ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check slow queries (requires pg_stat_statements extension)
-- SELECT query, calls, mean_exec_time, total_exec_time
-- FROM pg_stat_statements
-- ORDER BY mean_exec_time DESC
-- LIMIT 10;
