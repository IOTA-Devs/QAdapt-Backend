CREATE TABLE Users (
    userId INT PRIMARY KEY,
    username VARCHAR(32),
    firstName TEXT,
    lastName TEXT,
    email TEXT,
    passwordHash TEXT,
    passwordSalt TEXT,
    joinedAt DATE
);

CREATE TABLE Collections (
    collectionId INT PRIMARY KEY,
    name VARCHAR(32),
    lastModified Date,
    description TEXT,
    tests INT,
    userId INT,
    FOREIGN KEY (userId) REFERENCES Users(userId)
);

CREATE TABLE Tests (
    testId INT PRIMARY KEY,
    collectionId INT,
    userId INT,
    name TEXT,
    startTimestamp TIMESTAMP,
    endTimestamp TIMESTAMP,
    status VARCHAR(7),
    FOREIGN KEY (collectionId) REFERENCES Collections(collectionId),
    FOREIGN KEY (userId) REFERENCES Users(userId)
);

CREATE TABLE SelfHealingReports (
    reportId INT PRIMARY KEY,
    testId INT,
    seleniumSelectorName TEXT,
    healingDescription TEXT,
    status VARCHAR(7),
    screenshotPath TEXT,
    FOREIGN KEY (testId) REFERENCES Tests(testId)
);

CREATE TABLE TestLogs (
    logId INT PRIMARY KEY,
    testId INT,
    logName TEXT,
    logDescription TEXT,
    timestamp TIMESTAMP,
    FOREIGN KEY (testId) REFERENCES Tests(testId)
);

CREATE TABLE UserSessions (
    sessionId TEXT,
    userId INT,
    expiresAt DATE,
    refreshTokenHash VARCHAR(64),
    createdAt DATE,
    lastAccessed DATE,
    FOREIGN KEY (userId) REFERENCES Users(userId)
);