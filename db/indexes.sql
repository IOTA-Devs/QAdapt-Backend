CREATE INDEX IF NOT EXISTS "IX_Collections_userId"
    ON public.collections USING btree
    (userid ASC NULLS LAST)
    INCLUDE(collectionid, name, description, tests, scripts, lastmodified)
    WITH (deduplicate_items=True)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS "IX_Collections_userId_lastModified"
    ON public.collections USING btree
    (userid ASC NULLS LAST, lastmodified ASC NULLS LAST)
    INCLUDE(collectionid, name, lastmodified, description, tests, scripts)
    WITH (deduplicate_items=True)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS "IX_PersonalAccessTokens_userId"
    ON public.personalaccesstokens USING btree
    (userid ASC NULLS LAST)
    INCLUDE(id, name, expiresat, createdat)
    WITH (deduplicate_items=True)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS "IX_Scripts_userId"
    ON public.scripts USING btree
    (userid ASC NULLS LAST)
    WITH (deduplicate_items=True)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS "IX_Scripts_userId_collectionId"
    ON public.scripts USING btree
    (userid ASC NULLS LAST, collectionid ASC NULLS LAST)
    INCLUDE(scriptid, name, tests)
    WITH (deduplicate_items=True)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS "IX_SelfHealingReports_testId"
    ON public.selfhealingreports USING btree
    (testid ASC NULLS LAST)
    INCLUDE(seleniumselectorname, healingdescription, status, screenshoturl)
    WITH (deduplicate_items=True)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS "IX_Tests_scriptId_userId_startTimestamp"
    ON public.tests USING btree
    (scriptid ASC NULLS LAST, userid ASC NULLS LAST, starttimestamp ASC NULLS LAST)
    INCLUDE(testid, scriptid, name, starttimestamp, endtimestamp, status)
    WITH (deduplicate_items=True)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS "IX_Tests_userId"
    ON public.tests USING btree
    (userid ASC NULLS LAST)
    WITH (deduplicate_items=True)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS "IX_Tests_userId_startTimestamp"
    ON public.tests USING btree
    (userid ASC NULLS LAST, starttimestamp ASC NULLS LAST)
    INCLUDE(testid, scriptid, name, starttimestamp, endtimestamp, status)
    WITH (deduplicate_items=True)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS "IX_UserSessions_userId"
    ON public.usersessions USING btree
    (userid ASC NULLS LAST)
    INCLUDE(sessionid, userid, expiresat, refreshtokenhash, createdat, lastaccessed)
    WITH (deduplicate_items=True)
    TABLESPACE pg_default;