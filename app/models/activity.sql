CREATE TABLE IF NOT EXISTS activity (
    owner TEXT NOT NULL,
    repo TEXT NOT NULL,
    date DATE NOT NULL,
    commits INT NOT NULL,
    authors TEXT[] NOT NULL,
    PRIMARY KEY (owner, repo, date)
);
