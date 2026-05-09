-- Database: SQLite 

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS movies (
    movie_id        TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    genre           TEXT NOT NULL,
    release_date    DATE NOT NULL,
    budget_inr      BIGINT,
    revenue_inr     BIGINT,
    rating          REAL,
    director        TEXT,
    language        TEXT DEFAULT 'Hindi',
    release_year    INTEGER GENERATED ALWAYS AS
                        (CAST(strftime('%Y', release_date) AS INTEGER)) VIRTUAL,
    roi             REAL GENERATED ALWAYS AS (
                        CASE WHEN budget_inr > 0
                        THEN ROUND((revenue_inr - budget_inr) * 1.0 / budget_inr, 2)
                        ELSE NULL END
                    ) VIRTUAL
);

-- ── Table 2: Viewers 
CREATE TABLE IF NOT EXISTS viewers (
    viewer_id           TEXT PRIMARY KEY,
    age                 INTEGER NOT NULL,
    region              TEXT NOT NULL,
    city                TEXT NOT NULL,
    subscription_tier   TEXT NOT NULL
                        CHECK(subscription_tier IN ('Free', 'Standard', 'Premium')),
    gender              TEXT,
    language_preference TEXT DEFAULT 'Hindi'
);

-- ── Table 3: Watch Activity 
CREATE TABLE IF NOT EXISTS watch_activity (
    activity_id      TEXT PRIMARY KEY,
    viewer_id        TEXT NOT NULL REFERENCES viewers(viewer_id),
    movie_id         TEXT NOT NULL REFERENCES movies(movie_id),
    watch_date       DATE NOT NULL,
    duration_mins    INTEGER,
    completion_rate  REAL CHECK(completion_rate BETWEEN 0 AND 1),
    device           TEXT,
    rewatched        TEXT DEFAULT 'No'
);

-- ── Table 4: Reviews 
CREATE TABLE IF NOT EXISTS reviews (
    review_id       TEXT PRIMARY KEY,
    movie_id        TEXT NOT NULL REFERENCES movies(movie_id),
    rating          REAL CHECK(rating BETWEEN 0 AND 10),
    sentiment       TEXT CHECK(sentiment IN ('positive', 'mixed', 'negative')),
    review_text     TEXT,
    review_date     DATE,
    platform        TEXT,
    helpful_votes   INTEGER DEFAULT 0
);

-- ── Table 5: Marketing Spend
CREATE TABLE IF NOT EXISTS marketing_spend (
    spend_id        TEXT PRIMARY KEY,
    movie_id        TEXT NOT NULL REFERENCES movies(movie_id),
    channel         TEXT NOT NULL,
    spend_inr       BIGINT,
    impressions     BIGINT,
    clicks          BIGINT,
    conversions     INTEGER,
    campaign_date   DATE,
    roi             REAL
);

-- ── Table 6: Regional Performance
CREATE TABLE IF NOT EXISTS regional_performance (
    perf_id             TEXT PRIMARY KEY,
    city                TEXT NOT NULL,
    region              TEXT NOT NULL,
    movie_id            TEXT NOT NULL REFERENCES movies(movie_id),
    month               TEXT NOT NULL,
    year                INTEGER NOT NULL,
    views               INTEGER,
    engagement_score    REAL CHECK(engagement_score BETWEEN 0 AND 10),
    avg_watch_time_mins INTEGER,
    repeat_views        INTEGER
);

-- Indexes

CREATE INDEX IF NOT EXISTS idx_movies_genre        ON movies(genre);
CREATE INDEX IF NOT EXISTS idx_movies_release_date ON movies(release_date);
CREATE INDEX IF NOT EXISTS idx_movies_rating       ON movies(rating DESC);
CREATE INDEX IF NOT EXISTS idx_watch_movie_id      ON watch_activity(movie_id);
CREATE INDEX IF NOT EXISTS idx_watch_viewer_id     ON watch_activity(viewer_id);
CREATE INDEX IF NOT EXISTS idx_watch_date          ON watch_activity(watch_date);
CREATE INDEX IF NOT EXISTS idx_reviews_movie_id    ON reviews(movie_id);
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment   ON reviews(sentiment);
CREATE INDEX IF NOT EXISTS idx_marketing_movie_id  ON marketing_spend(movie_id);
CREATE INDEX IF NOT EXISTS idx_marketing_channel   ON marketing_spend(channel);
CREATE INDEX IF NOT EXISTS idx_regional_city       ON regional_performance(city);
CREATE INDEX IF NOT EXISTS idx_regional_movie_id   ON regional_performance(movie_id);
CREATE INDEX IF NOT EXISTS idx_regional_year_month ON regional_performance(year, month);


-- might need views for AI based queries, but let's keep it simple for now. We can always add them later as needed.

CREATE VIEW IF NOT EXISTS vw_movie_performance AS
SELECT
    m.movie_id,
    m.title,
    m.genre,
    m.release_date,
    m.release_year,
    m.director,
    m.budget_inr,
    m.revenue_inr,
    m.roi,
    m.rating                                AS imdb_rating,
    COUNT(DISTINCT wa.activity_id)          AS total_watches,
    ROUND(AVG(wa.completion_rate)*100, 1)   AS avg_completion_pct,
    ROUND(AVG(r.rating), 2)                 AS avg_review_rating,
    COUNT(DISTINCT r.review_id)             AS total_reviews,
    SUM(CASE WHEN r.sentiment='positive' THEN 1 ELSE 0 END) AS positive_reviews,
    SUM(CASE WHEN r.sentiment='negative' THEN 1 ELSE 0 END) AS negative_reviews
FROM movies m
LEFT JOIN watch_activity wa ON m.movie_id = wa.movie_id
LEFT JOIN reviews r         ON m.movie_id = r.movie_id
GROUP BY m.movie_id;

-- City engagement leaderboard
CREATE VIEW IF NOT EXISTS vw_city_engagement AS
SELECT
    rp.city,
    rp.region,
    rp.month,
    rp.year,
    m.title,
    m.genre,
    rp.views,
    rp.engagement_score,
    rp.avg_watch_time_mins,
    rp.repeat_views,
    ROUND(rp.repeat_views * 100.0 / NULLIF(rp.views,0), 1) AS repeat_view_pct
FROM regional_performance rp
JOIN movies m ON rp.movie_id = m.movie_id;

-- Marketing ROI by title + channel
CREATE VIEW IF NOT EXISTS vw_marketing_performance AS
SELECT
    m.title,
    m.genre,
    ms.channel,
    ms.spend_inr,
    ms.impressions,
    ms.clicks,
    ms.conversions,
    ms.roi,
    ROUND(ms.clicks * 100.0 / NULLIF(ms.impressions,0), 2) AS ctr_pct
FROM marketing_spend ms
JOIN movies m ON ms.movie_id = m.movie_id;

-- Genre health summary
CREATE VIEW IF NOT EXISTS vw_genre_summary AS
SELECT
    m.genre,
    COUNT(DISTINCT m.movie_id)              AS total_titles,
    ROUND(AVG(m.rating), 2)                 AS avg_rating,
    ROUND(AVG(wa.completion_rate)*100, 1)   AS avg_completion_pct,
    SUM(m.revenue_inr)                      AS total_revenue_inr,
    ROUND(AVG(ms.roi), 2)                   AS avg_marketing_roi,
    SUM(CASE WHEN r.sentiment='positive' THEN 1 ELSE 0 END) AS positive_reviews,
    SUM(CASE WHEN r.sentiment='negative' THEN 1 ELSE 0 END) AS negative_reviews
FROM movies m
LEFT JOIN watch_activity wa ON m.movie_id = wa.movie_id
LEFT JOIN marketing_spend ms ON m.movie_id = ms.movie_id
LEFT JOIN reviews r          ON m.movie_id = r.movie_id
GROUP BY m.genre;