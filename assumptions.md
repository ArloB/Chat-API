**Account Assumptions**
* Handle is a unique identifier of user that is displayed by default
* Logging out clears token
* Registering adds token and logs in
* Logging in adds token
* Token is based on time and unique
* U_ID is a based on same function as Token
* The owner flag in accounts refers to whether a user is an owner or not. By default, the first user inside the flockr is an owner.

**Channel Assumptions**
* Tokens when passed through channel functions are active (not invalid) in this iteration
* Channel_details: Owners of the channel also appear in all_members
* Channel_invite: User of token doesn't need to be an owner of the channel to invite another user
* Channel_messages: Flockr owner can't access channel_messages if they're not part of the channel (they need to join first :) )
* Channel_leave: If token is an owner that leaves, they are unable to leave the channel
* Messages are inserted into a list based on time created
* Channel_addowner and channel_removeowner: The owner of the server is able to add and remove owners from a channel without being invited
* Channel_addowner and channel_removeowner: u_ids are assumed to belong to a user
* Channel_addowner: A user can be added as an owner even if they aren't a member of the channel. This causes them to be added as a member at the same time.
* Channel_removeowner: an owner is able to remove themselves
* Channel_removeowner: a channel owner is able to remove the server owner as a channel owner as they have the same permissions

**Channels Assumptions**
* Assume all owners are equal (flockr owner has same permissions as a normal owner in the same channel) 
* Channels_create: Creator of the server automatically becomes an owner of the channel 

**Message Assumptions**
* If there are more than 10 000 messages in a specific channel, there will be duplicate message_ids :)