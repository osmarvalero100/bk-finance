import smtplib
import logging
import calendar
from datetime import datetime, date, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.core.config import settings
from app.models.fixed_expense import FixedExpense
from app.models.user import User

logger = logging.getLogger(__name__)


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    Envía un correo electrónico utilizando SMTP configurado.
    Si SMTP no está configurado o está deshabilitado, registra la notificación en log
    para facilitar pruebas y desarrollo local.
    """
    if not settings.EMAIL_NOTIFICATIONS_ENABLED:
        logger.info(f"[Email Simulado] Notificaciones deshabilitadas en configuración. Destinatario: {to_email} | Asunto: {subject}")
        return True

    # Si no hay credenciales configuradas o el host es localhost sin servidor activo, simular
    if not settings.SMTP_USER or settings.SMTP_HOST == "localhost":
        logger.info(
            f"[Email Simulado / Modo Desarrollo]\n"
            f"  Para: {to_email}\n"
            f"  De: {settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>\n"
            f"  Asunto: {subject}\n"
            f"  Contenido: Notificación generada exitosamente."
        )
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        msg["To"] = to_email

        if text_content:
            part1 = MIMEText(text_content, "plain", "utf-8")
            msg.attach(part1)

        part2 = MIMEText(html_content, "html", "utf-8")
        msg.attach(part2)

        if settings.SMTP_TLS:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
            server.starttls()
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)

        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        server.sendmail(settings.EMAILS_FROM_EMAIL, [to_email], msg.as_string())
        server.quit()
        logger.info(f"Correo electrónico enviado exitosamente a {to_email}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar correo electrónico a {to_email}: {str(e)}", exc_info=True)
        return False


def get_month_due_date(due_day: int, year: int, month: int) -> date:
    """Devuelve la fecha de vencimiento ajustada a los días máximos del mes."""
    _, max_days = calendar.monthrange(year, month)
    valid_day = min(due_day, max_days)
    return date(year, month, valid_day)


def calculate_next_due_date_and_days(due_day: int, today: Optional[date] = None) -> Tuple[date, int]:
    """
    Calcula la fecha de vencimiento más cercana (del mes actual o próximo)
    y los días restantes con respecto a la fecha de hoy.
    """
    if today is None:
        today = date.today()

    current_month_due = get_month_due_date(due_day, today.year, today.month)
    days_left = (current_month_due - today).days

    # Si la fecha límite de este mes ya pasó (hace más de 1 día), calcular para el próximo mes
    if days_left < 0:
        if today.month == 12:
            next_month = 1
            next_year = today.year + 1
        else:
            next_month = today.month + 1
            next_year = today.year
        next_due = get_month_due_date(due_day, next_year, next_month)
        return next_due, (next_due - today).days

    return current_month_due, days_left


def render_reminder_email_html(
    user_name: str,
    expense_name: str,
    amount: float,
    currency: str,
    due_date: date,
    days_left: int,
    category_name: Optional[str] = None,
    payment_method_name: Optional[str] = None,
    is_test: bool = False
) -> str:
    """Genera el contenido HTML del recordatorio de vencimiento con diseño limpio y moderno."""
    formatted_amount = f"{amount:,.2f}"
    formatted_date = due_date.strftime("%d/%m/%Y")

    if days_left == 0:
        urgency_label = "¡Vence HOY!"
        badge_bg = "#dc2626"  # Red
    elif days_left == 1:
        urgency_label = "Vence MAÑANA (en 1 día)"
        badge_bg = "#ea580c"  # Orange
    elif days_left < 0:
        urgency_label = f"Venció hace {abs(days_left)} días"
        badge_bg = "#991b1b"
    else:
        urgency_label = f"Vence en {days_left} días"
        badge_bg = "#4f46e5"  # Indigo

    test_banner = ""
    if is_test:
        test_banner = """
        <div style="background-color: #fef3c7; color: #92400e; padding: 12px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; text-align: center; border: 1px solid #fde68a;">
            🔔 [CORREO DE PRUEBA] Este es un recordatorio de prueba de tu aplicación de Finanzas.
        </div>
        """

    category_row = ""
    if category_name:
        category_row = f"""
        <tr>
            <td style="padding: 10px 0; color: #6b7280; font-size: 14px;">Categoría:</td>
            <td style="padding: 10px 0; color: #111827; font-weight: 600; text-align: right; font-size: 14px;">{category_name}</td>
        </tr>
        """

    payment_row = ""
    if payment_method_name:
        payment_row = f"""
        <tr>
            <td style="padding: 10px 0; color: #6b7280; font-size: 14px;">Método sugerido:</td>
            <td style="padding: 10px 0; color: #111827; font-weight: 600; text-align: right; font-size: 14px;">{payment_method_name}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Recordatorio de Pago</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f3f4f6; margin: 0; padding: 24px; color: #1f2937;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0">
            <tr>
                <td align="center">
                    <table width="600" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%); padding: 30px 40px; text-align: center;">
                                <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px;">
                                    Recordatorio de Pago
                                </h1>
                                <p style="color: #e0e7ff; margin: 8px 0 0 0; font-size: 15px;">
                                    Tu aplicación de Finanzas Personales
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 36px 40px;">
                                {test_banner}
                                <p style="margin: 0 0 20px 0; font-size: 16px; color: #374151;">
                                    Hola <strong>{user_name}</strong>,
                                </p>
                                <p style="margin: 0 0 24px 0; font-size: 15px; color: #4b5563; line-height: 1.5;">
                                    Te recordamos que se acerca la fecha límite de pago para el siguiente gasto fijo registrado en tu cuenta:
                                </p>
                                
                                <!-- Card Details -->
                                <div style="background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 24px; margin-bottom: 24px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px dashed #e5e7eb; padding-bottom: 12px;">
                                        <span style="font-size: 18px; font-weight: 700; color: #111827;">{expense_name}</span>
                                        <span style="background-color: {badge_bg}; color: #ffffff; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 9999px; text-transform: uppercase;">
                                            {urgency_label}
                                        </span>
                                    </div>
                                    <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                        <tr>
                                            <td style="padding: 10px 0; color: #6b7280; font-size: 14px;">Monto a pagar:</td>
                                            <td style="padding: 10px 0; color: #111827; font-weight: 700; font-size: 20px; text-align: right; color: #4f46e5;">
                                                {currency} {formatted_amount}
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 10px 0; color: #6b7280; font-size: 14px;">Fecha límite:</td>
                                            <td style="padding: 10px 0; color: #111827; font-weight: 600; text-align: right; font-size: 14px;">
                                                {formatted_date} (Día {due_date.day})
                                            </td>
                                        </tr>
                                        {category_row}
                                        {payment_row}
                                    </table>
                                </div>
                                
                                <p style="margin: 0 0 24px 0; font-size: 14px; color: #6b7280; line-height: 1.5;">
                                    💡 <em>Consejo:</em> Realizar tus pagos puntuales te ayuda a evitar recargos por mora e intereses adicionales, manteniendo un excelente puntaje crediticio.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f9fafb; padding: 20px 40px; border-top: 1px solid #e5e7eb; text-align: center;">
                                <p style="margin: 0; font-size: 13px; color: #9ca3af;">
                                    Este recordatorio automático fue generado según tus preferencias de gastos fijos.<br>
                                    Puedes administrar o desactivar estos avisos ingresando a tu sección de <strong>Gastos Fijos</strong>.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html


def send_fixed_expense_reminder(
    user: User,
    fixed_expense: FixedExpense,
    days_left: int,
    due_date: date,
    is_test: bool = False
) -> bool:
    """Envía el correo de recordatorio para un gasto fijo específico."""
    user_name = user.full_name or user.username
    category_name = fixed_expense.category.name if fixed_expense.category else None
    payment_name = fixed_expense.payment_method.name if fixed_expense.payment_method else None

    if is_test:
        subject = f"[Prueba] Recordatorio de Pago: {fixed_expense.name}"
    elif days_left == 0:
        subject = f"⚠️ ¡VENCE HOY! Pago pendiente de {fixed_expense.name}"
    elif days_left == 1:
        subject = f"⏳ Vence mañana: Pago de {fixed_expense.name}"
    else:
        subject = f"🔔 Recordatorio: Pago de {fixed_expense.name} vence en {days_left} días"

    html_content = render_reminder_email_html(
        user_name=user_name,
        expense_name=fixed_expense.name,
        amount=fixed_expense.amount,
        currency=fixed_expense.currency,
        due_date=due_date,
        days_left=days_left,
        category_name=category_name,
        payment_method_name=payment_name,
        is_test=is_test
    )

    text_content = (
        f"Hola {user_name},\n\n"
        f"Recordatorio de pago para '{fixed_expense.name}'.\n"
        f"Monto: {fixed_expense.currency} {fixed_expense.amount:,.2f}\n"
        f"Fecha límite: {due_date.strftime('%d/%m/%Y')}\n"
        f"Días restantes: {days_left}\n\n"
        f"Finanzas Personales."
    )

    return send_email(user.email, subject, html_content, text_content)


def check_and_send_due_reminders(
    db: Session,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Revisa todos los gastos fijos activos que tengan habilitado el recordatorio por email.
    Si la fecha límite está próxima a vencer según 'reminder_days_before' y no se ha
    enviado recordatorio para este ciclo, envía el correo al usuario y actualiza la fecha.
    """
    today = date.today()
    query = (
        db.query(FixedExpense)
        .options(
            joinedload(FixedExpense.user),
            joinedload(FixedExpense.category),
            joinedload(FixedExpense.payment_method)
        )
        .filter(
            and_(
                FixedExpense.is_active == True,
                FixedExpense.email_reminder_enabled == True
            )
        )
    )

    if user_id:
        query = query.filter(FixedExpense.user_id == user_id)

    fixed_expenses: List[FixedExpense] = query.all()

    processed = len(fixed_expenses)
    reminders_sent = 0
    details = []

    for fe in fixed_expenses:
        if not fe.user or not fe.user.email:
            continue

        # Calcular fecha de vencimiento actual
        current_month_due = get_month_due_date(fe.due_day, today.year, today.month)
        days_left = (current_month_due - today).days

        # Si ya pasó en este mes, no enviar para este mes a menos que hoy sea el día
        if days_left < 0:
            continue

        # Verificar si está dentro del umbral de días de anticipación
        if 0 <= days_left <= fe.reminder_days_before:
            # Verificar si ya se envió notificación para esta ventana de vencimiento
            # Si se envió hoy o dentro de los últimos días de esta misma ventana
            already_sent = False
            if fe.last_reminder_sent_at:
                last_sent_date = fe.last_reminder_sent_at.date() if isinstance(fe.last_reminder_sent_at, datetime) else fe.last_reminder_sent_at
                # Si se envió hoy, o si se envió en el mismo mes y dentro de la ventana de anticipación
                if last_sent_date == today:
                    already_sent = True
                elif last_sent_date.year == today.year and last_sent_date.month == today.month:
                    # Si ya se envió hace menos de reminder_days_before días, evitar spam
                    if (today - last_sent_date).days < fe.reminder_days_before:
                        already_sent = True

            if not already_sent:
                success = send_fixed_expense_reminder(fe.user, fe, days_left, current_month_due)
                if success:
                    fe.last_reminder_sent_at = datetime.now(timezone.utc)
                    db.add(fe)
                    reminders_sent += 1
                    details.append({
                        "id": fe.id,
                        "name": fe.name,
                        "recipient": fe.user.email,
                        "days_left": days_left,
                        "due_date": current_month_due.isoformat()
                    })

    if reminders_sent > 0:
        db.commit()

    return {
        "processed": processed,
        "reminders_sent": reminders_sent,
        "details": details
    }
