import yaml

def load_config(configFile) -> dict[str, any]:
    with open(configFile) as f:
        config=yaml.safe_load(f)
    return config