CREATE TABLE IF NOT EXISTS top100 (
    repo TEXT NOT NULL,
    owner TEXT NOT NULL,
    position_cur INT NOT NULL,
    position_prev INT,
    stars INT NOT NULL,
    watchers INT NOT NULL,
    forks INT NOT NULL,
    open_issues INT NOT NULL,
    language TEXT,
    PRIMARY KEY (owner, repo)
);
