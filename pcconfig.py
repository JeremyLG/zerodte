import pynecone as pc

class ZerodteConfig(pc.Config):
    pass

config = ZerodteConfig(
    app_name="zerodte",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)