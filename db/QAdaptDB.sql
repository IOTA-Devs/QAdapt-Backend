CREATE TABLE Users (
    userId SERIAL PRIMARY KEY,
    username VARCHAR(32) NOT NULL UNIQUE,
    firstName TEXT,
    lastName TEXT,
    email TEXT NOT NULL UNIQUE,
    passwordHash TEXT NOT NULL,
    joinedAt DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE Collections (
    collectionId SERIAL PRIMARY KEY,
    name VARCHAR(32)  NOT NULL,
    lastModified Date NOT NULL,
    description TEXT NOT NULL,
    tests INT NOT NULL DEFAULT 0,
    userId INT NOT NULL,
    FOREIGN KEY (userId) REFERENCES Users(userId)
);

CREATE TABLE Tests (
    testId SERIAL PRIMARY KEY,
    collectionId INT NOT NULL,
    userId INT NOT NULL,
    name TEXT NOT NULL,
    startTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_DATE,
    endTimestamp TIMESTAMP,
    status VARCHAR(7) NOT NULL,
    FOREIGN KEY (collectionId) REFERENCES Collections(collectionId),
    FOREIGN KEY (userId) REFERENCES Users(userId)
);

CREATE TABLE SelfHealingReports (
    reportId SERIAL PRIMARY KEY,
    testId INT NOT NULL,
    seleniumSelectorName TEXT NOT NULL,
    healingDescription TEXT NOT NULL,
    status VARCHAR(7) NOT NULL,
    screenshotPath TEXT,
    FOREIGN KEY (testId) REFERENCES Tests(testId)
);

CREATE TABLE TestLogs (
    logId SERIAL PRIMARY KEY,
    testId INT NOT NULL,
    logName TEXT NOT NULL,
    logDescription TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY (testId) REFERENCES Tests(testId)
);

CREATE TABLE UserSessions (
    sessionId TEXT PRIMARY KEY,
    userId INT NOT NULL,
    expiresAt DATE NOT NULL,
    refreshTokenHash VARCHAR(64) NOT NULL,
    createdAt DATE NOT NULL DEFAULT CURRENT_DATE,
    lastAccessed DATE NOT NULL,
    FOREIGN KEY (userId) REFERENCES Users(userId)
);