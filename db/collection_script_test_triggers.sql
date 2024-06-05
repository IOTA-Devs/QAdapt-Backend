CREATE OR REPLACE FUNCTION update_collection_counts()
    RETURNS TRIGGER
    LANGUAGE plpgsql
AS $$
DECLARE
    script_count INTEGER;
    test_count INTEGER;
BEGIN
    -- Get the number of scripts for the collection
    SELECT COUNT(*) INTO script_count
    FROM Scripts
    WHERE collectionId = CASE WHEN TG_OP = 'DELETE' THEN OLD.collectionId ELSE NEW.collectionId END;

    -- Get the number of tests for the collection
    SELECT SUM(tests) INTO test_count
    FROM Scripts
    WHERE collectionId = CASE WHEN TG_OP = 'DELETE' THEN OLD.collectionId ELSE NEW.collectionId END;

    -- Update the collection with the new counts
    UPDATE Collections
    SET scripts = script_count, tests = test_count, lastModified = CURRENT_TIMESTAMP
    WHERE collectionId = CASE WHEN TG_OP = 'DELETE' THEN OLD.collectionId ELSE NEW.collectionId END;

    RETURN NULL;
END;
$$;

CREATE TRIGGER update_collection_counts_trigger
    AFTER INSERT OR UPDATE OR DELETE ON Scripts
                                  FOR EACH ROW
EXECUTE FUNCTION update_collection_counts();

CREATE OR REPLACE FUNCTION update_script_test_count()
    RETURNS TRIGGER
    LANGUAGE plpgsql
AS $$
BEGIN
    -- Update the script with the new test count
    UPDATE Scripts
    SET tests = (SELECT COUNT(*) FROM Tests WHERE scriptId = NEW.scriptId)
    WHERE scriptId = NEW.scriptId;

    RETURN NULL;
END;
$$;

CREATE TRIGGER update_script_test_count_trigger
    AFTER INSERT OR UPDATE OR DELETE ON Tests
                                  FOR EACH ROW
EXECUTE FUNCTION update_script_test_count();

CREATE OR REPLACE FUNCTION general_dashboard_data(user_id INTEGER)
RETURNS TABLE (
	total_tests BIGINT,
	successful_tests BIGINT,
	failed_tests BIGINT,
	self_healed_scripts BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
	RETURN QUERY SELECT * FROM  
		(SELECT COUNT(*) AS total_tests FROM tests WHERE userId = user_id),
		(SELECT COUNT(*) AS successful_tests FROM tests WHERE userId = user_id AND status = 'Success'),
		(SELECT COUNT(*) AS failed_tests FROM tests WHERE userId = user_id AND status = 'Failed'),
		(SELECT COUNT(*) AS self_healed_Scripts FROM scripts WHERE userId = user_id);
END; $$

CREATE OR REPLACE FUNCTION update_user_sessions()
    RETURNS TRIGGER
AS $$
DECLARE sessions_count INTEGER;
BEGIN
    SELECT COUNT(*) FROM UserSessions WHERE userId = NEW.userId INTO sessions_count;

    IF sessions_count > 5 THEN
        DELETE FROM UserSessions WHERE userId = NEW.userId AND createdAt = (SELECT MIN(createdAt) FROM UserSessions WHERE userId = NEW.userId);
    END IF;

	RETURN NULL;
END; $$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER update_user_sessions_trigger
    AFTER INSERT ON UserSessions FOR EACH ROW
EXECUTE FUNCTION update_user_sessions();