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