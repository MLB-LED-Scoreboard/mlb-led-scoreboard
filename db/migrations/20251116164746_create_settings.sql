-- migrate:up
CREATE TABLE IF NOT EXISTS schemas (
    id INTEGER PRIMARY KEY,
    directory TEXT NOT NULL,
    filename TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type in ("global", "coordinates", "colors")),
    UNIQUE(directory, filename)
);

CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY,
    schema_id INTEGER NOT NULL REFERENCES schemas(id) ON DELETE CASCADE,
    namespace TEXT,
    key TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type in ('string', 'integer', 'float', 'boolean', 'json')),
    value TEXT,
    is_default BOOLEAN NOT NULL DEFAULT 0,
    UNIQUE(schema_id, namespace, key)
);

-- migrate:down
DROP TABLE IF EXISTS schemas;
DROP TABLE IF EXISTS settings;
