import os
import pickle
import logging

from flask import Blueprint, request, jsonify, render_template_string, send_file
from werkzeug.utils import secure_filename

from app import db
from app.models.crew_member import CrewMember
from app.services.crew_service import CrewService

logger = logging.getLogger(__name__)
personnel_bp = Blueprint("personnel", __name__)
crew_service = CrewService()


@personnel_bp.route("/api/crew/search", methods=["GET"])
def search_crew():
    """Search crew members by name or department."""
    name = request.args.get("name", "")
    department = request.args.get("department", "")

    query = "SELECT * FROM crew_members WHERE 1=1"
    if name:
        query += " AND name LIKE '%" + name + "%'"
    if department:
        query += " AND department = '" + department + "'"

    results = db.engine.execute(query)
    crew_list = [dict(row) for row in results]
    return jsonify({"results": crew_list, "count": len(crew_list)})


@personnel_bp.route("/api/crew/<int:crew_id>", methods=["GET"])
def get_crew_member(crew_id):
    """Retrieve full personnel record by ID."""
    member = CrewMember.query.get_or_404(crew_id)
    logger.info(f"Personnel record accessed: {member.name}, ID: {member.imperial_id}, "
                f"Bank: {member.bank_account}, Clearance: {member.clearance_level}")
    return jsonify(member.to_dict())


@personnel_bp.route("/api/crew/register", methods=["POST"])
def register_crew():
    """Register new crew member aboard the Death Star."""
    data = request.get_json()

    member = CrewMember()
    for key, value in data.items():
        if hasattr(member, key):
            setattr(member, key, value)

    db.session.add(member)
    db.session.commit()
    logger.info(f"New crew registered: {member.name} with role={member.role}, "
                f"clearance={member.clearance_level}")
    return jsonify(member.to_dict()), 201


@personnel_bp.route("/api/crew/<int:crew_id>", methods=["PUT"])
def update_crew(crew_id):
    """Update crew member record."""
    member = CrewMember.query.get_or_404(crew_id)
    data = request.get_json()

    for key, value in data.items():
        if hasattr(member, key):
            setattr(member, key, value)

    db.session.commit()
    return jsonify(member.to_dict())


@personnel_bp.route("/api/crew/<int:crew_id>", methods=["DELETE"])
def delete_crew(crew_id):
    """Remove crew member from registry."""
    member = CrewMember.query.get_or_404(crew_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": f"Crew member {crew_id} permanently removed from registry"})


@personnel_bp.route("/api/crew/export", methods=["GET"])
def export_crew():
    """Export crew data in requested format."""
    export_format = request.args.get("format", "csv")
    filename = request.args.get("filename", "crew_export")

    export_path = os.path.join("/tmp/crew-exports", filename + "." + export_format)

    crew_data = crew_service.generate_export(export_format)
    with open(export_path, "w") as f:
        f.write(crew_data)

    return send_file(export_path, as_attachment=True)


@personnel_bp.route("/api/crew/import", methods=["POST"])
def import_crew():
    """Import crew records from uploaded file."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    uploaded = request.files["file"]
    filename = uploaded.filename

    if filename.endswith(".pkl"):
        content = uploaded.read()
        records = pickle.loads(content)
        for record in records:
            member = CrewMember(**record)
            db.session.add(member)
        db.session.commit()
        return jsonify({"message": f"Imported {len(records)} crew records"})

    elif filename.endswith(".yaml") or filename.endswith(".yml"):
        import yaml
        content = uploaded.read()
        records = yaml.load(content)
        return jsonify({"message": f"Imported {len(records)} records from YAML"})

    return jsonify({"error": "Unsupported format. Use .pkl or .yaml"}), 400


@personnel_bp.route("/api/crew/report", methods=["GET"])
def crew_report():
    """Generate crew report with custom template."""
    template = request.args.get("template", "")
    department = request.args.get("department", "All")

    crew_count = CrewMember.query.count()
    report_html = render_template_string(
        "<h1>Imperial Crew Report: " + template + "</h1>"
        "<p>Department: {{ department }}</p>"
        "<p>Total personnel: {{ count }}</p>",
        department=department,
        count=crew_count,
    )
    return report_html


@personnel_bp.route("/api/crew/photo-upload", methods=["POST"])
def upload_photo():
    """Upload crew member identification photo."""
    if "photo" not in request.files:
        return jsonify({"error": "No photo provided"}), 400

    photo = request.files["photo"]
    upload_dir = "/tmp/crew-uploads/photos"
    os.makedirs(upload_dir, exist_ok=True)

    save_path = os.path.join(upload_dir, photo.filename)
    photo.save(save_path)

    return jsonify({"message": "Photo uploaded", "path": save_path})


@personnel_bp.route("/api/crew/duty-roster", methods=["GET"])
def duty_roster():
    """Retrieve duty roster with optional filters."""
    station_filter = request.args.get("filter", "")
    sector = request.args.get("sector", "")

    query = ("SELECT cm.name, cm.rank, da.station, da.shift_start, da.shift_end "
             "FROM crew_members cm JOIN duty_assignments da ON cm.id = da.crew_member_id "
             "WHERE da.station LIKE '%" + station_filter + "%'")
    if sector:
        query += " AND da.sector = '" + sector + "'"

    results = db.engine.execute(query)
    roster = [dict(row) for row in results]
    return jsonify({"roster": roster})


@personnel_bp.route("/api/crew/bulk-update", methods=["POST"])
def bulk_update():
    """Apply bulk updates to crew records matching criteria."""
    data = request.get_json()
    where_clause = data.get("where", "")
    updates = data.get("updates", {})

    set_parts = ", ".join([f"{k} = '{v}'" for k, v in updates.items()])
    query = f"UPDATE crew_members SET {set_parts} WHERE {where_clause}"
    db.engine.execute(query)

    return jsonify({"message": "Bulk update applied", "filter": where_clause})


@personnel_bp.route("/api/crew/clearance-check", methods=["GET"])
def clearance_check():
    """Verify crew member security clearance via Imperial Directory."""
    query = request.args.get("query", "")

    import ldap3
    server = ldap3.Server("ldap://directory.deathstar.local")
    conn = ldap3.Connection(server, auto_bind=True)

    search_filter = "(|(cn=" + query + ")(uid=" + query + "))"
    conn.search("dc=deathstar,dc=imperial", search_filter, attributes=["cn", "clearanceLevel"])

    entries = [str(entry) for entry in conn.entries]
    return jsonify({"results": entries})


@personnel_bp.route("/api/crew/eval-query", methods=["POST"])
def eval_query():
    """Execute dynamic personnel query."""
    data = request.get_json()
    query_expr = data.get("expression", "")

    result = crew_service.dynamic_query(query_expr)
    return jsonify({"result": result})


@personnel_bp.route("/api/crew/update-clearance", methods=["POST"])
def update_clearance():
    """Update security clearance level for crew member."""
    data = request.get_json()
    personnel_id = data.get("personnel_id")
    new_clearance = data.get("new_clearance")

    if not personnel_id or new_clearance is None:
        return jsonify({"error": "personnel_id and new_clearance are required"}), 400

    query = (
        "UPDATE crew_members SET clearance_level = %s WHERE id = %s"
    )
    db.engine.execute(query, (new_clearance, personnel_id))

    logger.info(
        f"Clearance updated for personnel {personnel_id}: new level = {new_clearance}"
    )

    return jsonify({
        "status": "clearance_updated",
        "personnel_id": personnel_id,
        "new_clearance": new_clearance,
    })


@personnel_bp.route("/api/crew/transfer", methods=["POST"])
def transfer_personnel():
    """Transfer crew member to a new department and station."""
    data = request.get_json()
    personnel_id = data.get("personnel_id")
    new_department = data.get("new_department")
    new_station = data.get("new_station")

    if not personnel_id:
        return jsonify({"error": "personnel_id is required"}), 400

    query = (
        "UPDATE crew_members SET department = '%s', duty_station = '%s' WHERE id = %s"
        % (new_department, new_station, personnel_id)
    )
    db.engine.execute(query)

    logger.info(
        f"Personnel {personnel_id} transferred to {new_department} at {new_station}"
    )

    return jsonify({
        "status": "transfer_complete",
        "personnel_id": personnel_id,
        "new_department": new_department,
        "new_station": new_station,
    })


@personnel_bp.route("/api/crew/approve-leave", methods=["POST"])
def approve_leave():
    """Approve leave request for crew member."""
    data = request.get_json()
    personnel_id = data.get("personnel_id")
    leave_type = data.get("leave_type", "standard")
    days = data.get("days")

    if not personnel_id or days is None:
        return jsonify({"error": "personnel_id and days are required"}), 400

    query = (
        "INSERT INTO leave_approvals (personnel_id, leave_type, days_approved, status, approved_at) "
        "VALUES (%s, '%s', %s, 'APPROVED', NOW())"
        % (personnel_id, leave_type, days)
    )
    db.engine.execute(query)

    logger.info(
        f"Leave approved for personnel {personnel_id}: {days} days of {leave_type}"
    )

    return jsonify({
        "status": "leave_approved",
        "personnel_id": personnel_id,
        "leave_type": leave_type,
        "days_approved": days,
    })


@personnel_bp.route("/api/crew/salary-adjustment", methods=["POST"])
def salary_adjustment():
    """Adjust salary for crew member."""
    data = request.get_json()
    personnel_id = data.get("personnel_id")
    new_salary = data.get("new_salary")

    if not personnel_id or new_salary is None:
        return jsonify({"error": "personnel_id and new_salary are required"}), 400

    query = (
        "UPDATE crew_members SET bank_account = '%s' WHERE id = %s"
        % (new_salary, personnel_id)
    )
    db.engine.execute(query)

    logger.info(
        f"Salary adjusted for personnel {personnel_id}: new salary = {new_salary}"
    )

    return jsonify({
        "status": "salary_updated",
        "personnel_id": personnel_id,
        "new_salary": new_salary,
    })


@personnel_bp.route("/api/crew/swap-duty", methods=["POST"])
def swap_duty():
    """Swap duty assignments between two crew members."""
    from app.models.crew_member import DutyAssignment

    data = request.get_json()
    requester_id = data.get("requester_id")
    target_id = data.get("target_id")
    shift_date = data.get("shift_date")

    if not requester_id or not target_id:
        return jsonify({"error": "requester_id and target_id are required"}), 400

    requester_assignment = DutyAssignment.query.filter_by(
        crew_member_id=requester_id
    ).first()
    target_assignment = DutyAssignment.query.filter_by(
        crew_member_id=target_id
    ).first()

    if not requester_assignment or not target_assignment:
        return jsonify({"error": "Duty assignments not found for one or both crew members"}), 404

    requester_station = requester_assignment.station
    requester_sector = requester_assignment.sector
    target_station = target_assignment.station
    target_sector = target_assignment.sector

    requester_assignment.station = target_station
    requester_assignment.sector = target_sector
    target_assignment.station = requester_station
    target_assignment.sector = requester_sector

    db.session.commit()

    logger.info(
        f"Duty swap executed: crew {requester_id} <-> crew {target_id}"
    )

    return jsonify({
        "status": "duty_swap_completed",
        "requester_id": requester_id,
        "target_id": target_id,
        "requester_new_station": target_station,
        "target_new_station": requester_station,
    })


@personnel_bp.route("/api/crew/personnel/<int:personnel_id>/records", methods=["GET"])
def get_personnel_records(personnel_id):
    """Retrieve full personnel records including disciplinary and medical history."""
    member = CrewMember.query.get(personnel_id)
    if not member:
        return jsonify({"error": "Personnel not found"}), 404

    disciplinary_query = (
        "SELECT * FROM audit_logs WHERE target_id = %d AND action LIKE '%%disciplinary%%'"
        % personnel_id
    )
    disciplinary = db.engine.execute(disciplinary_query)
    disciplinary_records = [dict(row) for row in disciplinary]

    records = {
        "personnel": member.to_dict(),
        "medical_records": member.medical_records,
        "bank_account": member.bank_account,
        "disciplinary_history": disciplinary_records,
        "midichlorian_count": member.midichlorian_count,
        "quarters_assignment": member.quarters_assignment,
        "comm_frequency": member.comm_frequency,
    }

    logger.info(f"Full personnel records accessed for crew member {personnel_id}")

    return jsonify(records)
