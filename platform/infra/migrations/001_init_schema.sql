-- =============================================================================
-- 001_init_schema.sql — EMP 初始库表（PostgreSQL）
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    device_code VARCHAR(64) NOT NULL,
    name VARCHAR(128) NOT NULL,
    device_type VARCHAR(32) NOT NULL DEFAULT 'edge',
    platform VARCHAR(32) NOT NULL DEFAULT 'wsl',
    status VARCHAR(32) NOT NULL DEFAULT 'offline',
    last_seen_at TIMESTAMPTZ,
    meta_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, device_code)
);
CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status);
CREATE INDEX IF NOT EXISTS idx_devices_last_seen ON devices(last_seen_at DESC);

CREATE TABLE IF NOT EXISTS channels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    channel_code VARCHAR(64) NOT NULL,
    name VARCHAR(128) NOT NULL,
    media_kind VARCHAR(32) NOT NULL DEFAULT 'video',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    config_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (device_id, channel_code)
);

CREATE TABLE IF NOT EXISTS record_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL REFERENCES devices(id),
    session_code VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'created',
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    storage_root TEXT,
    note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (device_id, session_code)
);
CREATE INDEX IF NOT EXISTS idx_sessions_device_started ON record_sessions(device_id, started_at DESC);

CREATE TABLE IF NOT EXISTS media_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES record_sessions(id) ON DELETE CASCADE,
    channel_id UUID REFERENCES channels(id),
    asset_type VARCHAR(32) NOT NULL,
    relative_path TEXT NOT NULL,
    byte_size BIGINT NOT NULL DEFAULT 0,
    duration_ms BIGINT,
    checksum_sha1 CHAR(40),
    meta_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_assets_session ON media_assets(session_id);

CREATE TABLE IF NOT EXISTS alarm_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID REFERENCES devices(id),
    severity VARCHAR(16) NOT NULL DEFAULT 'info',
    code VARCHAR(64) NOT NULL,
    message TEXT NOT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acked BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX IF NOT EXISTS idx_alarms_occurred ON alarm_events(occurred_at DESC);

CREATE TABLE IF NOT EXISTS command_audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID REFERENCES devices(id),
    operator VARCHAR(64) NOT NULL DEFAULT 'system',
    command VARCHAR(64) NOT NULL,
    request_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    result_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic VARCHAR(128) NOT NULL,
    payload_json JSONB NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sent_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_outbox_pending ON outbox_events(status, created_at) WHERE status = 'pending';
