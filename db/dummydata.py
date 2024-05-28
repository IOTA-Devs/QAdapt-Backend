import random
import datetime
import psycopg2

"""
LINE 50: user ids for which to create collections
LINE 54 - range(): number of COLLECTIONS to create for each user
LINE 65 - random.randint(): range of SCRIPTS to create for each collection
LINE 73 - random.randint(): range of TESTS to create for each script
        check last loop to modify test DURATION and TIME BETWEEN tests
"""
# Connect to your database
conn = psycopg2.connect("postgresql://postgres:ZJ8FGQ8Z7XpH4cj@qadapt-db-server.postgres.database.azure.com:5432/qadapt")
cur = conn.cursor()

# List of dummy collections
dummy_collections = [
    {'name': 'Google', 'description': 'Search engine'},
    {'name': 'Facebook', 'description': 'Social media'},
    {'name': 'Twitter', 'description': 'Social media'},
    {'name': 'Instagram', 'description': 'Social media'},
    {'name': 'LinkedIn', 'description': 'Professional networking'},
    {'name': 'Reddit', 'description': 'Social news aggregation'},
    {'name': 'Pinterest', 'description': 'Image sharing'},
    {'name': 'Tumblr', 'description': 'Microblogging'},
    {'name': 'Snapchat', 'description': 'Multimedia messaging'},
    {'name': 'WhatsApp', 'description': 'Messaging'},
    {'name': 'Telegram', 'description': 'Messaging'},
    {'name': 'Signal', 'description': 'Messaging'},
    {'name': 'Skype', 'description': 'Messaging'},
    {'name': 'Zoom', 'description': 'Video conferencing'},
    {'name': 'Slack', 'description': 'Messaging'},
    {'name': 'Discord', 'description': 'Messaging'},
    {'name': 'Twitch', 'description': 'Streaming'},
    {'name': 'Spotify', 'description': 'Music streaming'},
    {'name': 'Netflix', 'description': 'Video streaming'},
    {'name': 'YouTube', 'description': 'Video sharing'},
    {'name': 'QAdapt', 'description': 'Automated testing platform'},
]
# List of dummy scripts
dummy_scripts = [
    'Log In', 'Log Out', 'Search', 'Create Post', 'Edit Post', 'Delete Post', 'Like Post',
    'Comment on Post', 'Share Post', 'Send Message', 'Receive Message', 'Block User',
    'Unblock User', 'Report User', 'Report Post', 'View Profile', 'Edit Profile',
    'Change Password', 'Delete Account', 'Upload Image', 'Upload Video', 'Upload Audio',
    'Upload Document', 'Upload File', 'Download Image', 'Download Video', 'Download Audio',
    'Download Document', 'Download File'
]

# User ID for which to create collections
user_ids = [21, 22, 23]  # Replace with the desired user ID

for user_id in user_ids:
    # Create collections with random names and descriptions
    for i in range(3):
        collection = random.choice(dummy_collections)
        name = collection['name']
        description = collection['description']
        last_modified = datetime.date.today()
        
        cur.execute("INSERT INTO Collections (name, lastModified, description, userId) VALUES (%s, %s, %s, %s) RETURNING collectionId",
                    (name, last_modified, description, user_id))
        collection_id = cur.fetchone()[0]
        
        # Create scripts for the collection
        num_scripts = random.randint(4, 8)
        for j in range(num_scripts):
            script_name = random.choice(dummy_scripts)
            cur.execute("INSERT INTO Scripts (collectionId, userId, name) VALUES (%s, %s, %s) RETURNING scriptId",
                        (collection_id, user_id, script_name))
            test_id = cur.fetchone()[0]

            # Create tests for each script
            num_tests = random.randint(20, 100) # Number of tests to create for each script
            start_timestamp = datetime.datetime.now() - datetime.timedelta(days=2) # Start timestamp for the first test
            for k in range(num_tests):
                test_name = f'Test {k}'
                end_timestamp = start_timestamp + datetime.timedelta(seconds=random.randint(15, 25)) # Duration of the test
                status = random.choice(['Success', 'Failed'])

                cur.execute("INSERT INTO Tests (scriptId, userId, name, startTimestamp, endTimestamp, status) VALUES (%s, %s, %s, %s, %s, %s)",
                            (test_id, user_id, test_name, start_timestamp, end_timestamp, status))

                start_timestamp = end_timestamp + datetime.timedelta(minutes=random.randint(3, 97))

conn.commit()
cur.close()
conn.close()
