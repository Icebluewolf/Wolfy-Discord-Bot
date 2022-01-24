# Wolfy - Discord Bot
## Discord Support Server : [Invite](https://discord.gg/f39cJ9D)
## Welcome To The GitHub For Wolfy Discord Bot.
This Is A Personal Discord Bot Created With Python To Preform Some Tasks On My Discord Server.
I Am Now Trying To Allow The Public To Use This Bot.

## Version : 0.3.0

### Table Of Contents
- [Introduction](#introduction)
- [Polls](#polls)
- [Whitelisting](#whitelisting)
- [Custom Settings](#custom-Settings)
- [Reaction Roles](#reaction-roles)


## Introduction
This is a Discord Bot That Has Been Created To Help Me Learn Python.
The Bot Uses Python 3.7 Along With Discord.py.

The prefix for all commands on this bot is : `/`

You Can Invite The Bot To Your Server With The Link Below **OR** You Can Use This Code As A Starting Template.<br>
Invite : [Invite The Bot To Your Server](https://discord.com/api/oauth2/authorize?client_id=714954765368295486&permissions=126016&scope=bot)

If You Have Any Questions Please Contact Me On Discord Or Open An Issue

Discord : Ice Wolfy#5283

Other Contributors that are helping me on this project are:<br>
Scotch101Tape<br>
Mintyfree<br>
Please Only Contact Ice Wolfy#5283 With Issues Unless Otherwise Told.


## Moderation
You Can Now Use Wolfy For Moderation! Wolfy Offers A Complete Moderation System.
This Includes Basic Moderation Like A Ban Command. It Also Offers More Advanced
Moderation Such As Timed Mutes, Bans, And Even Warnings. It Is Possible To Add A Reason While
Running A Moderation Command Or Afterwards. Wolfy Will Automatically Send Messages 
To A Configured Channel Every Time A Wolfy Moderation Command Is Used. You Can Also
List All Of A Users Punishments.


## Polls
This Feature Is For Getting The Input Of Others.<br>
You Can Type In A Command And Wolfy Will Make A Custom Embed/Message For Your Poll.
An Example Command For This Is : `/poll Title, 1d12h, Option 1, Option 2, Etc.`
/poll Is The Activation For The Command. The Title is The Title Of Your Poll.
The Time Is A Group Of Characters, You Can Use d For Days, h For Hours, m For Minutes, And s for Seconds. 
You Must Do Them In Order (dhms) But, Are Not Required To Use All Fields. If A Field Is Unused It Will Be Set To Zero. 
There Is A Limit Of 20 Options In The Poll Because Of Discords Limit Of 20 Reactions Per Message.


## Reaction Roles
This will help your server not rely on staff to give out roles.
This can be used to set up an announcement role that users can opt in for, so you dont have to ping @everyone. 
If you want to know what games your users are interested in put up a few reactions roles with the top games.
When users click the reaction they will get the specified role. When the remove the reaction there role will be removed!
The format for this command is `/rr <add|remove> <emoji> <message_id> <role_id> [channel_id, for add only]`.
You can also list your servers reaction roles with `/rr list` and if you need help with copying IDs run `w!rr id`


## Whitelisting 
##### (Not Usable For Invited Bot *Yet*)
This command will make it easy for you to allow users that are on your discord to whitelist themselves on your
Minecraft server. As this bot was designed on a discord for a small Minecraft server I thought it would be a 
good idea to add automatic whitelisting. This feature is not available to be used *yet.*
I am current working on a new feature(Custom Settings) that will allow this.
The command for this feature is `/whitelist IGN` With IGN being the players Minecraft Username they want to whitelist



## Custom Settings 
Are you tired of people using a command you dont want them to use.
This feature will allow you to lock a command to only be accessed by specific roles. 
It will also allow you to set up items such as connection to your Minecraft server.
This command comes with 2 options on how to run it. If you are to the command you 
can run `/settings` to get a step by step walkthrough of the command. 
If you know exactly what you want to do you can run `/settings <feature> <setting>` 
where feature is what you want to change as a category `EX: poll` and setting is the 
specific thing within the feature you want to change `EX: roles`.



## More?
See Update 0.2.0 for info on new features in this update.