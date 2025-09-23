from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__, template_folder="../templates/dashboard")


@main_bp.route("/", endpoint="index")
def home():
    return render_template("dashboard/index.html")
