class DistributionTypeException(Exception):
    def __init__(self, msg="This distribution is not supported. ['stream', 'poission', 'fixed']", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class NoAppConfigException(Exception):
    pass
