class MissingSetting(Exception):
    def __init__(self, setting,
                 message="The `{s_name}` Setting Is Not Set. Set It For Full Capability Of This Feature."):
        self.setting = setting
        self.message = message.format(s_name=setting)
        super().__init__(self.message)
