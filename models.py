from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Tanto(db.Model):
    __tablename__ = "tm_tanto"

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50))
    password_hash = db.Column(db.String(255))
    authority = db.Column(db.SmallInteger)
    update_time = db.Column(db.DateTime)
    update_user_id = db.Column(db.Integer)

    inout_list = db.relationship("Inout", back_populates="tanto")


class Hinmoku(db.Model):
    __tablename__ = "tm_hinmoku"

    hinmoku_cd = db.Column(db.Integer, primary_key=True)
    hinmoku_name = db.Column(db.String(100))
    now_count = db.Column(db.Numeric(10,2))
    tani = db.Column(db.String(20))
    alert_count = db.Column(db.Numeric(10,2))
    update_time = db.Column(db.DateTime)
    update_user_id = db.Column(db.Integer)

    inout_list = db.relationship("Inout", back_populates="hinmoku")


class Inout(db.Model):
    __tablename__ = "td_inout"

    den_no = db.Column(db.Integer, primary_key=True)

    hinmoku_cd = db.Column(
        db.Integer,
        db.ForeignKey("tm_hinmoku.hinmoku_cd"),
        nullable=False
    )

    inout_kbn = db.Column(db.SmallInteger, nullable=False)

    count = db.Column(db.Numeric(10, 2), nullable=False)

    update_time = db.Column(db.DateTime, nullable=False)

    update_user_id = db.Column(
        db.Integer,
        db.ForeignKey("tm_tanto.user_id"),
        nullable=False
    )

    hinmoku = db.relationship("Hinmoku", back_populates="inout_list")
    tanto = db.relationship("Tanto", back_populates="inout_list")