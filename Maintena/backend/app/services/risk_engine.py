from datetime import datetime, timezone


# DEMONSTRATION THRESHOLDS ONLY.
# Replace with manufacturer-approved limits before real industrial use.

TEMPERATURE_WARNING = 70.0
TEMPERATURE_CRITICAL = 90.0

VIBRATION_WARNING = 4.5
VIBRATION_CRITICAL = 7.1


def calculate_sensor_risk(value, warning, critical, weight):

    if value is None:
        return None

    if value >= critical:
        return weight

    if value >= warning:
        return weight * 0.5

    return 0


def assess_machine_risk(
    machine,
    readings,
    maintenance_records,
    service_interval_hours=None
):

    now = datetime.now(timezone.utc)

    latest = max(
        readings,
        key=lambda reading: reading.recorded_at,
        default=None
    )

    risk_points = 0
    available_weight = 0
    reasons = []

    # Temperature assessment
    if latest and latest.temperature is not None:

        available_weight += 30

        score = calculate_sensor_risk(
            latest.temperature,
            TEMPERATURE_WARNING,
            TEMPERATURE_CRITICAL,
            30
        )

        risk_points += score

        if score:
            reasons.append(
                f"Elevated temperature: {latest.temperature} C"
            )

    # Vibration assessment
    if latest and latest.vibration is not None:

        available_weight += 30

        score = calculate_sensor_risk(
            latest.vibration,
            VIBRATION_WARNING,
            VIBRATION_CRITICAL,
            30
        )

        risk_points += score

        if score:
            reasons.append(
                f"Elevated vibration: {latest.vibration} mm/s RMS"
            )

    # Operating-hour assessment
    if (
        latest
        and latest.operating_hours is not None
        and service_interval_hours is not None
        and service_interval_hours > 0
    ):

        available_weight += 15

        usage_ratio = (
            latest.operating_hours / service_interval_hours
        )

        if usage_ratio >= 1:
            risk_points += 15
            reasons.append(
                "Operating-hour service interval exceeded"
            )

        elif usage_ratio >= 0.8:
            risk_points += 7.5
            reasons.append(
                "Approaching operating-hour service interval"
            )

    # Overdue maintenance assessment
    relevant_tasks = []

    for task in maintenance_records:

        if task.status.lower() in ("completed", "cancelled"):
            continue

        if task.scheduled_date is None:
            continue

        scheduled_date = task.scheduled_date

        if scheduled_date.tzinfo is None:
            scheduled_date = scheduled_date.replace(
                tzinfo=timezone.utc
            )

        if scheduled_date < now:
            relevant_tasks.append(task)

    if maintenance_records:

        available_weight += 25

        if relevant_tasks:
            risk_points += 25

            reasons.append(
                f"{len(relevant_tasks)} overdue maintenance task(s) detected"
            )

    # Normalize risk score
    if available_weight > 0:

        risk_score = round(
            (risk_points / available_weight) * 100
        )

    else:
        risk_score = None

    # Risk classification
    if risk_score is None:
        risk_level = "INSUFFICIENT_DATA"

    elif risk_score >= 75:
        risk_level = "CRITICAL"

    elif risk_score >= 50:
        risk_level = "HIGH"

    elif risk_score >= 25:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    return {
        "machine_id": machine.id,
        "machine_name": machine.name,
        "machine_code": machine.machine_code,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "data_coverage": round(available_weight),
        "reasons": reasons,
        "latest_reading": (
            latest.recorded_at.isoformat()
            if latest else None
        )
    }
