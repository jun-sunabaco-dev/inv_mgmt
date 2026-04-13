from flask import Flask, render_template, request, redirect, url_for, session
from config import Config
from models import db, Tanto, Hinmoku, Inout
from datetime import datetime
from decimal import Decimal
import bcrypt

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


@app.route("/", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        user = Tanto.query.filter_by(user_id=user_id).first()

        if user and bcrypt.checkpw(
                password.encode("utf-8"),
                user.password_hash.encode("utf-8")):
            session["user_id"] = user.user_id
            session["user_name"] = user.user_name
            session["authority"] = user.authority
            return redirect(url_for("menu"))
        else:
            error = "ユーザーID、または、パスワードが異なっています。"

    return render_template("login.html", error=error)


@app.route("/menu")
def menu():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "menu.html",
        user_name=session.get("user_name"),
        authority=session.get("authority")
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/hinmoku", methods=["GET", "POST"])
def hinmoku_list():
    if "user_id" not in session:
        return redirect(url_for("login"))

    error = ""

    if request.method == "POST":
        hinmoku_cd = request.form.get("hinmoku_cd")
        hinmoku_name = request.form.get("hinmoku_name")
        now_count = request.form.get("now_count")
        tani = request.form.get("tani")
        alert_count = request.form.get("alert_count")

        exists = Hinmoku.query.filter_by(hinmoku_cd=hinmoku_cd).first()
        if exists:
            error = "その品目コードはすでに登録されています。"
        else:
            item = Hinmoku(
                hinmoku_cd=hinmoku_cd,
                hinmoku_name=hinmoku_name,
                now_count=now_count,
                tani=tani,
                alert_count=alert_count,
                update_time=datetime.now(),
                update_user_id=session["user_id"]
            )
            db.session.add(item)
            db.session.commit()
            return redirect(url_for("hinmoku_list"))

    items = Hinmoku.query.order_by(Hinmoku.hinmoku_cd).all()
    return render_template("hinmoku.html", items=items, error=error)


@app.route("/hinmoku/edit/<int:hinmoku_cd>", methods=["GET", "POST"])
def hinmoku_edit(hinmoku_cd):
    if "user_id" not in session:
        return redirect(url_for("login"))

    item = Hinmoku.query.get_or_404(hinmoku_cd)
    error = ""

    if request.method == "POST":
        item.hinmoku_name = request.form.get("hinmoku_name")
        item.now_count = request.form.get("now_count")
        item.tani = request.form.get("tani")
        item.alert_count = request.form.get("alert_count")
        item.update_time = datetime.now()
        item.update_user_id = session["user_id"]

        db.session.commit()
        return redirect(url_for("hinmoku_list"))

    return render_template("hinmoku_edit.html", item=item, error=error)


@app.route("/hinmoku/delete/<int:hinmoku_cd>", methods=["POST"])
def hinmoku_delete(hinmoku_cd):
    if "user_id" not in session:
        return redirect(url_for("login"))

    item = Hinmoku.query.get_or_404(hinmoku_cd)
    db.session.delete(item)
    db.session.commit()

    return redirect(url_for("hinmoku_list"))

@app.route("/tanto", methods=["GET", "POST"])
def tanto_list():
    if "user_id" not in session:
        return redirect(url_for("login"))

    error = ""

    if request.method == "POST":
        user_id = request.form.get("user_id")
        user_name = request.form.get("user_name")
        password_hash = request.form.get("password_hash")
        authority = request.form.get("authority")

        exists = Tanto.query.filter_by(user_id=user_id).first()
        if exists:
            error = "そのユーザIDはすでに登録されています。"
        else:
            item = Tanto(
                user_id=user_id,
                user_name=user_name,
                password_hash=password_hash,
                authority=authority,
                update_time=datetime.now(),
                update_user_id=session["user_id"]
            )
            db.session.add(item)
            db.session.commit()
            return redirect(url_for("tanto_list"))

    items = Tanto.query.order_by(Tanto.user_id).all()
    return render_template("tanto.html", items=items, error=error)


@app.route("/tanto/edit/<int:user_id>", methods=["GET", "POST"])
def tanto_edit(user_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    item = Tanto.query.get_or_404(user_id)
    error = ""

    if request.method == "POST":
        item.user_name = request.form.get("user_name")
        item.password_hash = request.form.get("password_hash")
        item.authority = request.form.get("authority")
        item.update_time = datetime.now()
        item.update_user_id = session["user_id"]

        db.session.commit()
        return redirect(url_for("tanto_list"))

    return render_template("tanto_edit.html", item=item, error=error)


@app.route("/tanto/delete/<int:user_id>", methods=["POST"])
def tanto_delete(user_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    item = Tanto.query.get_or_404(user_id)
    db.session.delete(item)
    db.session.commit()

    return redirect(url_for("tanto_list"))


@app.route("/inout", methods=["GET", "POST"])
def inout_input():
    if "user_id" not in session:
        return redirect(url_for("login"))

    error = ""
    message = ""

    # 品目選択用
    items = Hinmoku.query.order_by(Hinmoku.hinmoku_cd).all()

    if request.method == "POST":
        hinmoku_cd = request.form.get("hinmoku_cd")
        quantity_str = request.form.get("quantity")
        action = request.form.get("action")

        item = Hinmoku.query.filter_by(hinmoku_cd=hinmoku_cd).first()

        if not item:
            error = "品目が見つかりません。"
        elif not quantity_str:
            error = "数量を入力してください。"
        else:
            try:
                quantity = Decimal(quantity_str)

                if quantity <= 0:
                    error = "数量は0より大きい値を入力してください。"
                else:
                    if action == "nyuko":
                        item.now_count = Decimal(item.now_count) + quantity
                        inout_kbn = 1

                    elif action == "shukko":
                        if Decimal(item.now_count) < quantity:
                            error = "在庫不足のため出庫できません。"
                        else:
                            item.now_count = Decimal(item.now_count) - quantity
                            inout_kbn = 2

                    elif action == "tyousei":
                        item.now_count = Decimal(item.now_count) + quantity
                        inout_kbn = 3

                    else:
                        error = "処理区分が不正です。"

                    if error == "":
                        item.update_time = datetime.now()
                        item.update_user_id = session["user_id"]

                        history = Inout(
                            hinmoku_cd=item.hinmoku_cd,
                            inout_kbn=inout_kbn,
                            count=quantity,
                            update_time=datetime.now(),
                            update_user_id=session["user_id"]
                        )

                        db.session.add(history)
                        db.session.commit()

                        return redirect(url_for("inout_input"))

            except Exception as e:
                db.session.rollback()
                error = f"登録に失敗しました: {e}"
    
    # 履歴一覧用
    inout_items = Inout.query.order_by(Inout.den_no.desc()).all()

    return render_template(
        "inout.html",
        hinmoku_items=items,
        inout_items=inout_items,
        error=error,
        message=message
    )

@app.route("/inout/edit/<int:den_no>", methods=["GET", "POST"])
def inout_edit(den_no):
    if "user_id" not in session:
        return redirect(url_for("login"))

    item = Inout.query.get_or_404(den_no)
    error = ""

    if request.method == "POST":
        try:
            new_hinmoku_cd = int(request.form.get("hinmoku_cd"))
            new_inout_kbn = int(request.form.get("inout_kbn"))
            new_count = Decimal(request.form.get("count"))

            if new_count <= 0:
                error = "数量は0より大きい値を入力してください。"
                return render_template("inout_edit.html", item=item, error=error)

            old_hinmoku_cd = item.hinmoku_cd
            old_inout_kbn = item.inout_kbn
            old_count = Decimal(item.count)

            old_hinmoku = Hinmoku.query.get_or_404(old_hinmoku_cd)
            new_hinmoku = Hinmoku.query.get_or_404(new_hinmoku_cd)

            # 1. 旧データの影響を戻す
            if old_inout_kbn == 1:      # 入庫
                old_hinmoku.now_count = Decimal(old_hinmoku.now_count) - old_count
            elif old_inout_kbn == 2:    # 出庫
                old_hinmoku.now_count = Decimal(old_hinmoku.now_count) + old_count
            elif old_inout_kbn == 3:    # 調整
                old_hinmoku.now_count = Decimal(old_hinmoku.now_count) - old_count

            # 2. 新データの影響を反映
            if new_inout_kbn == 1:      # 入庫
                new_hinmoku.now_count = Decimal(new_hinmoku.now_count) + new_count
            elif new_inout_kbn == 2:    # 出庫
                if Decimal(new_hinmoku.now_count) < new_count:
                    error = "在庫不足のため出庫できません。"
                    db.session.rollback()
                    return render_template("inout_edit.html", item=item, error=error)
                new_hinmoku.now_count = Decimal(new_hinmoku.now_count) - new_count
            elif new_inout_kbn == 3:    # 調整
                new_hinmoku.now_count = Decimal(new_hinmoku.now_count) + new_count
            else:
                error = "入出庫区分が不正です。"
                return render_template("inout_edit.html", item=item, error=error)

            # 3. 履歴を更新
            item.hinmoku_cd = new_hinmoku_cd
            item.inout_kbn = new_inout_kbn
            item.count = new_count
            item.update_time = datetime.now()
            item.update_user_id = session["user_id"]

            db.session.commit()
            return redirect(url_for("inout_input"))

        except Exception as e:
            db.session.rollback()
            error = f"更新に失敗しました: {e}"

    return render_template("inout_edit.html", item=item, error=error)


@app.route("/inout/delete/<int:den_no>", methods=["POST"])
def inout_delete(den_no):

    item = Inout.query.get_or_404(den_no)

    hinmoku = Hinmoku.query.get(item.hinmoku_cd)

    # 在庫を戻す処理
    if item.inout_kbn == 1:      # 入庫
        hinmoku.now_count -= item.count

    elif item.inout_kbn == 2:    # 出庫
        hinmoku.now_count += item.count

    elif item.inout_kbn == 3:    # 調整
        hinmoku.now_count -= item.count

    db.session.delete(item)
    db.session.commit()

    return redirect(url_for("inout_input"))


@app.route("/alert")
def alert_list():

    if "user_id" not in session:
        return redirect(url_for("login"))

    items = Hinmoku.query.filter(
        Hinmoku.now_count <= Hinmoku.alert_count
    ).order_by(Hinmoku.hinmoku_cd).all()

    return render_template("alert.html", items=items)

if __name__ == "__main__":
    app.run(debug=True)