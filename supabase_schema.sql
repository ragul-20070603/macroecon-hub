create table if not exists timeseries (
    id bigserial primary key,
    indicator text not null,
    source text not null,
    country text not null default 'US',
    date text not null,
    value float not null,
    created_at timestamp default now(),
    unique(indicator, source, country, date)
);

create table if not exists warm_chunks (
    id bigserial primary key,
    chunk_id text unique not null,
    url_hash text,
    url text,
    text text,
    source text,
    title text,
    topic text,
    type text,
    published_at text,
    ingested_at text,
    status text default 'stale'
);

create table if not exists url_hashes (
    hash text primary key,
    created_at timestamp default now()
);

create index if not exists idx_timeseries_indicator on timeseries(indicator);
create index if not exists idx_timeseries_country on timeseries(country);
create index if not exists idx_timeseries_date on timeseries(date);
create index if not exists idx_warm_chunks_status on warm_chunks(status);
