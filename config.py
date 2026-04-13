class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:xt226s@localhost:5432/inv_mgmt"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "secret-key"