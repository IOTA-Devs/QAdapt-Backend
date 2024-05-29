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
    WHERE collectionId = NEW.collectionId;

    -- Get the number of tests for the collection
    SELECT SUM(tests) INTO test_count
    FROM Scripts
    WHERE collectionId = NEW.collectionId;

    -- Update the collection with the new counts
    UPDATE Collections
    SET scripts = script_count, tests = test_count, lastModified = CURRENT_TIMESTAMP
    WHERE collectionId = NEW.collectionId;

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