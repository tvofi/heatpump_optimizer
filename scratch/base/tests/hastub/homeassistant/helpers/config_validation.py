def string(v): return str(v)
def boolean(v): return bool(v)
def positive_int(v): return int(v)
def positive_float(v): return float(v)


def config_entry_only_config_schema(domain):
    """The CONFIG_SCHEMA of a UI-only integration.

    The real one passes the configuration through and raises a repair issue
    when YAML carries the domain's key; nothing here reads YAML, so the
    pass-through is all that is mirrored.
    """

    def validator(config):
        return config

    return validator
