import requests
import os
from graph import graph

token = os.environ.get('SLACK_TOKEN')

def insert_channels() :
    res = requests.get("https://slack.com/api/channels.list?token={}".format(token))

    if res.status_code != 200: 
        raise Exception(u"Invalid Response from Channels endpoint {}".format(res.status_code))

    channels = res.json()['channels']

    query = """
    UNWIND {channels} AS channel
    MERGE (c:Channel {id:channel.id})
    ON CREATE SET c.name = channel.name
    RETURN COUNT(channel)
    """

    return graph.cypher.execute_one(query, {'channels': channels})

def insert_users():
    res = requests.get('https://slack.com/api/users.list?token={}'.format(token))

    if res.status_code != 200:
        raise Exception(u"Invalid Response from Users endpoint {}".format(res.status_code))

    users = res.json()['members']

    query = """
    UNWIND {users} AS user
    MERGE (u:User {id:user.id})
    SET u.username = user.name,
        u.fullname = user.profile.real_name
    RETURN COUNT(user)
    """

    return graph.cypher.execute_one(query, {'users': users})

def insert_channels_users():
    res = requests.get("https://slack.com/api/channels.list?token={}".format(token))

    if res.status_code != 200:
        raise Exception(u"Invalid Response from Channels endpoint {}".format(res.status_code))

    channels = res.json()['channels']

    query = """
    MATCH (channel:Channel {id: {channel_id} })
    MATCH (user:User {id: {user_id} })
    MERGE (user)-[:MEMBER_OF]->(channel)
    """

    count = 0

    for channel in channels:
        channel_id = channel['id']
        users = channel['members']

        for user_id in users:
            graph.cypher.execute(query, {'channel_id':channel_id, 'user_id': user_id})
            count += 1

    return count