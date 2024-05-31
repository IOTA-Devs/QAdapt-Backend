-- Tables

CREATE TABLE Users (
    userId SERIAL PRIMARY KEY,
    fullName VARCHAR(150),
    username VARCHAR(32) NOT NULL,
    email TEXT NOT NULL UNIQUE,
    passwordHash TEXT NOT NULL,
    joinedAt DATE NOT NULL DEFAULT CURRENT_DATE,
    deletionTimestamp TIMESTAMPTZ,
    avatarURL TEXT
);

CREATE TABLE Collections (
    collectionId SERIAL PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    lastModified TIMESTAMPTZ NOT NULL,
    description VARCHAR(256) NOT NULL,
    tests INT NOT NULL DEFAULT 0,
    scripts INT NOT NULL DEFAULT 0,
    userId INT NOT NULL,
    FOREIGN KEY (userId) REFERENCES Users(userId) ON DELETE CASCADE
);

CREATE TABLE Scripts (
    scriptId SERIAL PRIMARY KEY,
    collectionId INT NOT NULL,
    userId INT NOT NULL,
    tests INT NOT NULL DEFAULT 0,
    name VARCHAR(32) NOT NULL,
    FOREIGN KEY (collectionId) REFERENCES Collections(collectionId) ON DELETE CASCADE,
    FOREIGN KEY (userId) REFERENCES Users(userId)
);

CREATE TABLE Tests (
    testId SERIAL PRIMARY KEY,
    scriptId INT NOT NULL,
    userId INT NOT NULL,
    name TEXT NOT NULL,
    startTimestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_DATE,
    endTimestamp TIMESTAMPTZ,
    status VARCHAR(7) NOT NULL,
    FOREIGN KEY (userId) REFERENCES Users(userId),
    FOREIGN KEY (scriptId) REFERENCES Scripts(scriptId) ON DELETE CASCADE
);

CREATE TABLE SelfHealingReports (
    reportId SERIAL PRIMARY KEY,
    testId INT NOT NULL,
    seleniumSelectorName TEXT NOT NULL,
    healingDescription TEXT NOT NULL,
    status VARCHAR(7) NOT NULL,
    screenshotUrl TEXT,
    FOREIGN KEY (testId) REFERENCES Tests(testId) ON DELETE CASCADE
);

CREATE TABLE UserSessions (
    sessionId VARCHAR(36) PRIMARY KEY,
    userId INT NOT NULL,
    expiresAt TIMESTAMPTZ NOT NULL,
    refreshTokenHash VARCHAR(64) NOT NULL,
    createdAt TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lastAccessed DATE NOT NULL,
    FOREIGN KEY (userId) REFERENCES Users(userId) ON DELETE CASCADE
);

CREATE TABLE PersonalAccessTokens (
    userId INT NOT NULL,
    Id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    accessTokenHash TEXT NOT NULL,
    expiresAt TIMESTAMPTZ,
    createdAt TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userId) REFERENCES Users(userId) ON DELETE CASCADE
);