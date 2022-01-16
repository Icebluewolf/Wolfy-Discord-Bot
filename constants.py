SETTINGS = {
    "description": "These Are All The Setting Groups Use `w!settings <group>` To See More Info About A Group",

    "bypass": {
        "description": "These Settings Will Give The Same Permissions As If The Activation Was Done By A Admin",

        "role": {
            "description": "Users With This Role Is The Equivalent Of Having The Admin Permission On Your Discord "
                           "Server",

            "type": "role",
        }
    },
    "ban": {
        "description": "ban-d",

        "role": {
            "description": "bypass-role-d",

            "type": "xxx",
        }
    },
    "poll": {
        "description": "Make Polls To Get Input For Your Community",

        "role": {
            "description": "Users With This Role Will Be Able To Create Polls",

            "type": "role",
        },
        "channel": {
            "description": "Users Will Only Be Able To Make Polls In This Channel",

            "type": "channel",
        }
    },
    "rr": {
        "description": "Link A Message To A Role. When Users Click The Reaction On This Message A Role Will Be Added "
                       "To Them.",

        "role": {
            "description": "Users With This Role Will Be Able To Manage Reaction Roles",

            "type": "role",
        },
        "channel": {
            "description": "Reaction Role Commands Can Be Used In These Channels.",

            "type": "channel",
        }
    },
    "staff": {
        "description": "This Is To Help Keep Your Server Running Well. This Section Is For Moderation Functions",

        "log_channel": {
            "description": "The Channel That All Moderation Actions Will Be Logged In",

            "type": "channel",
        },
        "role": {
            "description": "Users Who Can Use Moderation Commands",

            "type": "role",
        }
    },
}
