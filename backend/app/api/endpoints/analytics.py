"""
Analytics Endpoints
Provides clinical, financial, and operational analytics for BI dashboards.

Note: Initial implementation returns computed/mock aggregates based on the requested
period to unblock frontend integration. Replace mocks with real SQL aggregates
over appointments, invoices, stock tables as needed.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import traceback
import logging

from fastapi import APIRouter, Depends, Query, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from database import get_async_session
from app.core.auth import get_current_user
from sqlalchemy import select, func, and_, or_, literal
from sqlalchemy.orm import aliased
from app.models import User, Appointment, Patient
from app.models.clinical import ClinicalRecord, Diagnosis
from app.models.financial import Invoice, InvoiceLine, ServiceItem, Payment, PaymentStatus, InvoiceStatus
from app.core.cache import analytics_cache
from app.services.reporting import generate_analytics_pdf, generate_analytics_excel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])
@router.get("/ping")
async def analytics_ping():
    return {"status": "ok"}



def _period_to_dates(period: str) -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    if period == "last_7_days":
        return now - timedelta(days=7), now
    if period == "last_30_days":
        return now - timedelta(days=30), now
    if period == "last_3_months":
        return now - timedelta(days=90), now
    if period == "last_year":
        return now - timedelta(days=365), now
    if period == "last_month":
        first_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_end = first_this_month - timedelta(seconds=1)
        last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return last_month_start, last_month_end
    # default
    return now - timedelta(days=30), now


@router.get("/clinical")
async def get_clinical_analytics(
    period: str = Query("last_30_days"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    start_dt, end_dt = _period_to_dates(period)

    # Cache key per clinic and period
    cache_key = f"clinical:{current_user.clinic_id}:{period}"
    cached = analytics_cache.get(cache_key)
    if cached is not None:
        return cached

    # --- Top Diagnoses (ICD-10) ---
    # Join Diagnosis -> ClinicalRecord -> Appointment (filter by clinic and date)
    diag_stmt = (
        select(
            Diagnosis.cid_code.label("icd10_code"),
            func.coalesce(Diagnosis.description, literal("")).label("description"),
            func.count(Diagnosis.id).label("count"),
        )
        .join(ClinicalRecord, ClinicalRecord.id == Diagnosis.clinical_record_id)
        .join(Appointment, Appointment.id == ClinicalRecord.appointment_id)
        .where(
            and_(
                Appointment.clinic_id == current_user.clinic_id,
                Appointment.scheduled_datetime >= start_dt,
                Appointment.scheduled_datetime <= end_dt,
            )
        )
        .group_by(Diagnosis.cid_code, Diagnosis.description)
        .order_by(func.count(Diagnosis.id).desc())
        .limit(10)
    )
    diag_rows = (await db.execute(diag_stmt)).all()
    top_diagnoses = [
        {"icd10_code": r.icd10_code, "description": r.description, "count": int(r.count)}
        for r in diag_rows
    ]

    # --- Patients by Age Group (seen in period) ---
    # Get patient DOBs who have appointments in range, then bucket in Python
    pat_stmt = (
        select(Patient.date_of_birth)
        .join(Appointment, Appointment.patient_id == Patient.id)
        .where(
            and_(
                Appointment.clinic_id == current_user.clinic_id,
                Appointment.scheduled_datetime >= start_dt,
                Appointment.scheduled_datetime <= end_dt,
            )
        )
    )
    dob_rows = (await db.execute(pat_stmt)).all()
    # Compute ages
    def _age(dob):
        if dob is None:
            return None
        today = datetime.now(tz=timezone.utc).date()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    buckets = {"0-17": 0, "18-35": 0, "36-55": 0, "56+": 0}
    for (dob,) in dob_rows:
        age = _age(dob)
        if age is None:
            continue
        if age <= 17:
            buckets["0-17"] += 1
        elif age <= 35:
            buckets["18-35"] += 1
        elif age <= 55:
            buckets["36-55"] += 1
        else:
            buckets["56+"] += 1
    patients_by_age_group = [
        {"age_group": k, "count": v} for k, v in buckets.items()
    ]

    # --- Appointments by Status ---
    status_stmt = (
        select(Appointment.status, func.count(Appointment.id).label("count"))
        .where(
            and_(
                Appointment.clinic_id == current_user.clinic_id,
                Appointment.scheduled_datetime >= start_dt,
                Appointment.scheduled_datetime <= end_dt,
            )
        )
        .group_by(Appointment.status)
    )
    status_rows = (await db.execute(status_stmt)).all()
    appointments_by_status = [
        {"status": str(r.status.value if hasattr(r.status, "value") else r.status), "count": int(r.count)}
        for r in status_rows
    ]

    # --- Consultations by Doctor ---
    doctor_stmt = (
        select(func.concat(User.first_name, literal(" "), User.last_name).label("doctor_name"), func.count(Appointment.id).label("count"))
        .join(User, User.id == Appointment.doctor_id)
        .where(
            and_(
                Appointment.clinic_id == current_user.clinic_id,
                Appointment.scheduled_datetime >= start_dt,
                Appointment.scheduled_datetime <= end_dt,
            )
        )
        .group_by(User.first_name, User.last_name)
        .order_by(func.count(Appointment.id).desc())
    )
    doctor_rows = (await db.execute(doctor_stmt)).all()
    consultations_by_doctor = [
        {"doctor_name": r.doctor_name.strip(), "count": int(r.count)} for r in doctor_rows
    ]

    resp = {
        "period": period,
        "start_date": start_dt.isoformat(),
        "end_date": end_dt.isoformat(),
        "top_diagnoses": top_diagnoses,
        "patients_by_age_group": patients_by_age_group,
        "appointments_by_status": appointments_by_status,
        "consultations_by_doctor": consultations_by_doctor,
    }

    analytics_cache.set(cache_key, resp, ttl_seconds=300)
    return resp


@router.get("/financial")
async def get_financial_analytics(
    period: str = Query("last_month"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Get financial analytics for the current user's clinic"""
    try:
        # Validate clinic_id exists
        if not hasattr(current_user, 'clinic_id') or current_user.clinic_id is None:
            raise HTTPException(
                status_code=400,
                detail="User is not associated with a clinic"
            )
        
        start_dt, end_dt = _period_to_dates(period)

        cache_key = f"financial:{current_user.clinic_id}:{period}"
        cached = analytics_cache.get(cache_key)
        if cached is not None:
            return cached

        # Revenue by doctor (from invoices linked to appointments)
        rev_doctor_stmt = (
            select(
                func.concat(User.first_name, literal(" "), User.last_name).label("doctor_name"),
                func.coalesce(func.sum(Invoice.total_amount), 0).label("total_revenue"),
            )
            .join(Appointment, Appointment.id == Invoice.appointment_id)
            .join(User, User.id == Appointment.doctor_id)
            .where(
                and_(
                    Invoice.clinic_id == current_user.clinic_id,
                    Invoice.issue_date >= start_dt,
                    Invoice.issue_date <= end_dt,
                    Invoice.status != InvoiceStatus.CANCELLED,
                )
            )
            .group_by(User.first_name, User.last_name)
            .order_by(func.sum(Invoice.total_amount).desc())
        )
        rev_doctor_rows = (await db.execute(rev_doctor_stmt)).all()
        revenue_by_doctor = [
            {"doctor_name": (r.doctor_name or "").strip(), "total_revenue": float(r.total_revenue)} for r in rev_doctor_rows
        ]

        # Revenue by service (sum of line totals by service item)
        rev_service_stmt = (
            select(
                ServiceItem.name.label("service_name"),
                func.coalesce(func.sum(InvoiceLine.line_total), 0).label("total_revenue"),
            )
            .join(Invoice, Invoice.id == InvoiceLine.invoice_id)
            .join(ServiceItem, ServiceItem.id == InvoiceLine.service_item_id)
            .where(
                and_(
                    Invoice.clinic_id == current_user.clinic_id,
                    Invoice.issue_date >= start_dt,
                    Invoice.issue_date <= end_dt,
                    Invoice.status != InvoiceStatus.CANCELLED,
                )
            )
            .group_by(ServiceItem.name)
            .order_by(func.sum(InvoiceLine.line_total).desc())
            .limit(15)
        )
        rev_service_rows = (await db.execute(rev_service_stmt)).all()
        revenue_by_service = [
            {"service_name": (r.service_name or "Desconhecido"), "total_revenue": float(r.total_revenue)} for r in rev_service_rows
        ]

        # Monthly revenue trend (sum by YYYY-MM)
        month_expr = func.date_trunc('month', Invoice.issue_date).label('month')
        month_stmt = (
            select(
                month_expr,
                func.coalesce(func.sum(Invoice.total_amount), 0).label('total_revenue'),
            )
            .where(
                and_(
                    Invoice.clinic_id == current_user.clinic_id,
                    Invoice.issue_date >= start_dt - timedelta(days=120),
                    Invoice.issue_date <= end_dt,
                    Invoice.status != InvoiceStatus.CANCELLED,
                )
            )
            .group_by(month_expr)
            .order_by(month_expr)
        )
        month_rows = (await db.execute(month_stmt)).all()
        def _fmt_month(m):
            try:
                return m.strftime('%Y-%m') if hasattr(m, 'strftime') else str(m)
            except Exception:
                return str(m)
        monthly_revenue_trend = [
            {"month": _fmt_month(r.month), "total_revenue": float(r.total_revenue)} for r in month_rows
        ]

        # Totals
        total_stmt = (
            select(
                func.count(Invoice.id),
                func.coalesce(func.sum(Invoice.total_amount), 0),
            )
            .where(
                and_(
                    Invoice.clinic_id == current_user.clinic_id,
                    Invoice.issue_date >= start_dt,
                    Invoice.issue_date <= end_dt,
                    Invoice.status != InvoiceStatus.CANCELLED,
                )
            )
        )
        total_result = (await db.execute(total_stmt)).first()
        if total_result is None:
            total_invoices = 0
            total_revenue = 0.0
        else:
            # Handle both tuple and Row object access
            try:
                if hasattr(total_result, '_mapping'):
                    # Row object - access by index
                    total_invoices = int(total_result[0] or 0)
                    total_revenue = float(total_result[1] or 0)
                else:
                    # Tuple
                    total_invoices = int(total_result[0] or 0)
                    total_revenue = float(total_result[1] or 0)
            except (IndexError, AttributeError, TypeError) as e:
                logger.error(f"Error accessing total_result: {e}, result type: {type(total_result)}, result: {total_result}")
                total_invoices = 0
                total_revenue = 0.0
        average_invoice_value = round(total_revenue / max(total_invoices, 1), 2)

        # AR Aging buckets (based on due_date and unpaid amount)
        # Unpaid amount = total_amount - sum(paid payments)
        buckets = {"current": 0.0, "1-30": 0.0, "31-60": 0.0, "61-90": 0.0, ">90": 0.0}
        try:
            paid_sum_subq = (
                select(Payment.invoice_id, func.coalesce(func.sum(Payment.amount), 0).label("paid"))
                .where(Payment.status == PaymentStatus.COMPLETED)
                .group_by(Payment.invoice_id)
                .subquery()
            )
            aging_stmt = (
                select(
                    Invoice.id,
                    Invoice.due_date,
                    (Invoice.total_amount - func.coalesce(paid_sum_subq.c.paid, 0)).label("unpaid"),
                )
                .outerjoin(paid_sum_subq, paid_sum_subq.c.invoice_id == Invoice.id)
                .where(
                    and_(
                        Invoice.clinic_id == current_user.clinic_id,
                        Invoice.status.notin_([InvoiceStatus.CANCELLED]),
                        Invoice.issue_date <= end_dt,
                    )
                )
            )
            aging_rows = (await db.execute(aging_stmt)).all()

            now = datetime.now(timezone.utc)
            for r in aging_rows:
                unpaid = float(r.unpaid or 0)
                if unpaid <= 0:
                    continue
                # Normalize due_date to timezone-aware datetime for comparison
                if r.due_date is None:
                    buckets["current"] += unpaid
                    continue
                due = r.due_date
                try:
                    from datetime import date as _date_type, datetime as _dt_type, timezone as _tz
                    if isinstance(due, _dt_type):
                        if due.tzinfo is None:
                            due = due.replace(tzinfo=_tz.utc)
                    else:
                        # assume date
                        due = _dt_type(due.year, due.month, due.day, tzinfo=_tz.utc)
                except Exception:
                    buckets["current"] += unpaid
                    continue
                if due >= now:
                    buckets["current"] += unpaid
                else:
                    days = (now - due).days
                    if days <= 30:
                        buckets["1-30"] += unpaid
                    elif days <= 60:
                        buckets["31-60"] += unpaid
                    elif days <= 90:
                        buckets["61-90"] += unpaid
                    else:
                        buckets[">90"] += unpaid
        except Exception as e:
            # If payments table does not exist or any SQL error occurs here, fall back to zeros
            # This prevents the entire endpoint from failing due to optional module data
            buckets = {"current": 0.0, "1-30": 0.0, "31-60": 0.0, "61-90": 0.0, ">90": 0.0}
            try:
                await db.rollback()
            except Exception:
                pass

        # Cost per procedure (average line_total/quantity by service item)
        try:
            cpp_stmt = (
                select(
                    ServiceItem.name.label("service_name"),
                    (func.coalesce(func.sum(InvoiceLine.line_total), 0) / func.nullif(func.coalesce(func.sum(InvoiceLine.quantity), 0), 0)).label("avg_cost"),
                )
                .join(Invoice, Invoice.id == InvoiceLine.invoice_id)
                .join(ServiceItem, ServiceItem.id == InvoiceLine.service_item_id)
                .where(
                    and_(
                        Invoice.clinic_id == current_user.clinic_id,
                        Invoice.issue_date >= start_dt,
                        Invoice.issue_date <= end_dt,
                        Invoice.status != InvoiceStatus.CANCELLED,
                    )
                )
                .group_by(ServiceItem.name)
                .order_by(literal(1))
                .limit(20)
            )
            cpp_rows = (await db.execute(cpp_stmt)).all()
            cost_per_procedure = [
                {"service_name": r.service_name, "avg_cost": float(r.avg_cost or 0)} for r in cpp_rows
            ]
        except Exception:
            try:
                await db.rollback()
            except Exception:
                pass
            cost_per_procedure = []

        resp = {
            "period": period,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "revenue_by_doctor": revenue_by_doctor,
            "revenue_by_service": revenue_by_service,
            "monthly_revenue_trend": monthly_revenue_trend,
            "total_revenue": total_revenue,
            "average_invoice_value": average_invoice_value,
            "total_invoices": total_invoices,
            "ar_aging": buckets,
            "cost_per_procedure": cost_per_procedure,
            "denial_patterns": [],  # TODO: integrate with claims/denials module when available
        }
        analytics_cache.set(cache_key, resp, ttl_seconds=300)
        return resp
    except SQLAlchemyError as e:
        # Database errors
        logger.error(f"Database error in financial analytics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        # Any other unexpected errors
        logger.error(f"Unexpected error in financial analytics: {str(e)}", exc_info=True)
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error generating financial analytics: {str(e)}"
        )


@router.get("/inventory")
async def get_inventory_analytics(
    period: str = Query("last_30_days"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    start_dt, end_dt = _period_to_dates(period)

    # Operational metrics are surfaced here for simplicity
    # Utilization by weekday: count appointments per weekday in period
    util_stmt = (
        select(func.extract('dow', Appointment.scheduled_datetime).label('dow'), func.count(Appointment.id))
        .where(
            and_(
                Appointment.clinic_id == current_user.clinic_id,
                Appointment.scheduled_datetime >= start_dt,
                Appointment.scheduled_datetime <= end_dt,
            )
        )
        .group_by(func.extract('dow', Appointment.scheduled_datetime))
        .order_by(func.extract('dow', Appointment.scheduled_datetime))
    )
    util_rows = (await db.execute(util_stmt)).all()
    weekdays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
    utilization = [
        {"label": weekdays[int(r.dow)], "value": int(r.count)} for r in util_rows
    ]

    # Wait time analysis: avg minutes between checked_in_at and started_at
    wt_stmt = (
        select(func.avg(func.extract('epoch', Appointment.started_at - Appointment.checked_in_at) / 60.0))
        .where(
            and_(
                Appointment.clinic_id == current_user.clinic_id,
                Appointment.checked_in_at.isnot(None),
                Appointment.started_at.isnot(None),
                Appointment.scheduled_datetime >= start_dt,
                Appointment.scheduled_datetime <= end_dt,
            )
        )
    )
    wt_val = (await db.execute(wt_stmt)).scalar()
    avg_wait_time_minutes = float(wt_val or 0)

    # No-show patterns: count appointments where completed_at is null and past scheduled, or explicit status if available
    ns_stmt = (
        select(func.count(Appointment.id))
        .where(
            and_(
                Appointment.clinic_id == current_user.clinic_id,
                Appointment.scheduled_datetime >= start_dt,
                Appointment.scheduled_datetime <= end_dt,
                Appointment.completed_at.is_(None),
                Appointment.cancelled_at.is_(None),
            )
        )
    )
    no_show_count = int((await db.execute(ns_stmt)).scalar() or 0)

    resp = {
        "period": period,
        "start_date": start_dt.isoformat(),
        "end_date": end_dt.isoformat(),
        "utilization": utilization,
        "avg_wait_time_minutes": avg_wait_time_minutes,
        "no_shows": no_show_count,
        "stock_movements_by_type": [],
        "top_products_by_movement": [],
        "low_stock_products": [],
    }
    return resp


# --------- Exports ---------

@router.get("/export/clinical/pdf")
async def export_clinical_pdf(
    period: str = Query("last_30_days"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    data = await get_clinical_analytics(period, current_user, db)
    pdf = generate_analytics_pdf("Relatório Clínico", data, clinic_name=current_user.clinic.name if getattr(current_user, 'clinic', None) else "CliniCore")
    headers = {"Content-Disposition": f"attachment; filename=clinical_{period}.pdf"}
    return Response(content=pdf, media_type="application/pdf", headers=headers)


@router.get("/export/financial/excel")
async def export_financial_excel(
    period: str = Query("last_month"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    data = await get_financial_analytics(period, current_user, db)
    xls = generate_analytics_excel("Relatório Financeiro", data)
    headers = {"Content-Disposition": f"attachment; filename=financial_{period}.xlsx"}
    return Response(content=xls, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)


@router.post("/schedule")
async def schedule_report(
    report_type: str = Query(..., description="clinical|financial|operational"),
    period: str = Query("last_30_days"),
    email: str = Query(...),
    current_user: User = Depends(get_current_user),
):
    # Stub scheduling: accept request and return success. Integrate with a task queue later.
    return {"message": "Report scheduled", "report_type": report_type, "period": period, "email": email}


# --------- Custom Reports (MVP) ---------

from pydantic import BaseModel
from fastapi import HTTPException


class CustomReportConfig(BaseModel):
    domain: str  # 'appointments' | 'financial' | 'clinical'
    period: str = "last_30_days"
    group_by: list[str] = []  # e.g., ['doctor'] or ['status']
    metrics: list[str] = ["count"]  # e.g., ['count'] or ['sum_revenue']


@router.post("/custom/run")
async def run_custom_report(
    config: CustomReportConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    start_dt, end_dt = _period_to_dates(config.period)
    domain = config.domain
    if domain not in {"appointments", "financial", "clinical"}:
        raise HTTPException(status_code=400, detail="Unsupported domain")

    if domain == "appointments":
        # Supported group_by: 'status', 'doctor'
        cols = []
        if "status" in config.group_by:
            cols.append(Appointment.status.label("status"))
        if "doctor" in config.group_by:
            cols.append(func.concat(User.first_name, literal(" "), User.last_name).label("doctor"))
        sel = select(*cols, func.count(Appointment.id).label("count")) if cols else select(func.count(Appointment.id).label("count"))
        if "doctor" in config.group_by:
            sel = sel.join(User, User.id == Appointment.doctor_id)
        sel = sel.where(and_(
            Appointment.clinic_id == current_user.clinic_id,
            Appointment.scheduled_datetime >= start_dt,
            Appointment.scheduled_datetime <= end_dt,
        ))
        if cols:
            sel = sel.group_by(*cols)
        rows = (await db.execute(sel)).all()
        data = [dict(r._mapping) for r in rows]
        # Normalize enums
        for d in data:
            if "status" in d and hasattr(d["status"], "value"):
                d["status"] = d["status"].value
        return {"columns": [c.key if hasattr(c, 'key') else c for c in cols] + ["count"], "rows": data}

    if domain == "financial":
        # Supported group_by: 'doctor', 'service'
        cols = []
        sel = None
        if "doctor" in config.group_by:
            cols.append(func.concat(User.first_name, literal(" "), User.last_name).label("doctor"))
            sel = select(*cols, func.coalesce(func.sum(Invoice.total_amount), 0).label("sum_revenue")) \
                .join(Appointment, Appointment.id == Invoice.appointment_id) \
                .join(User, User.id == Appointment.doctor_id)
        elif "service" in config.group_by:
            cols.append(ServiceItem.name.label("service"))
            sel = select(*cols, func.coalesce(func.sum(InvoiceLine.line_total), 0).label("sum_revenue")) \
                .join(Invoice, Invoice.id == InvoiceLine.invoice_id) \
                .join(ServiceItem, ServiceItem.id == InvoiceLine.service_item_id)
        else:
            sel = select(func.coalesce(func.sum(Invoice.total_amount), 0).label("sum_revenue"))

        sel = sel.where(and_(
            Invoice.clinic_id == current_user.clinic_id,
            Invoice.issue_date >= start_dt,
            Invoice.issue_date <= end_dt,
            Invoice.status != InvoiceStatus.CANCELLED,
        ))
        if cols:
            sel = sel.group_by(*cols)
        rows = (await db.execute(sel)).all()
        data = [dict(r._mapping) for r in rows]
        return {"columns": [c.key if hasattr(c, 'key') else c for c in cols] + ["sum_revenue"], "rows": data}

    if domain == "clinical":
        # Supported group_by: 'cid10'
        cols = [Diagnosis.cid_code.label("cid10")]
        sel = select(*cols, func.count(Diagnosis.id).label("count")) \
            .join(ClinicalRecord, ClinicalRecord.id == Diagnosis.clinical_record_id) \
            .join(Appointment, Appointment.id == ClinicalRecord.appointment_id) \
            .where(and_(
                Appointment.clinic_id == current_user.clinic_id,
                Appointment.scheduled_datetime >= start_dt,
                Appointment.scheduled_datetime <= end_dt,
            )) \
            .group_by(*cols)
        rows = (await db.execute(sel)).all()
        data = [dict(r._mapping) for r in rows]
        return {"columns": ["cid10", "count"], "rows": data}


class CustomReportExport(BaseModel):
    title: str = "Custom Report"
    columns: list[str]
    rows: list[dict]


@router.post("/export/custom/excel")
async def export_custom_excel(
    payload: CustomReportExport,
    current_user: User = Depends(get_current_user),
):
    # Flatten rows to string values
    simple = {"columns": ",".join(payload.columns), "rows": len(payload.rows)}
    xls = generate_analytics_excel(payload.title, simple)
    headers = {"Content-Disposition": f"attachment; filename=custom_report.xlsx"}
    return Response(content=xls, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)


 
