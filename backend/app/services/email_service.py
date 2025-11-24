"""
Email service for sending notification emails.

Handles all tier application notifications, verification emails, and admin communications.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

from app.core.config import get_settings
from app.schemas.tier_applications import ApplicationTierEnum

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailService:
    """Service for sending emails via SMTP."""

    @staticmethod
    def _send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML body content
            text_content: Plain text fallback (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Check if SMTP is configured
            if not settings.smtp_username or not settings.smtp_password:
                logger.warning(
                    f"SMTP not configured. Would send email to {to_email}: {subject}"
                )
                # In development, just log the email
                logger.info(f"Email subject: {subject}")
                logger.info(f"Email to: {to_email}")
                logger.info(f"Email body:\n{html_content}")
                return True

            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)

            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                if settings.smtp_use_tls:
                    server.starttls()
                server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    @staticmethod
    def _get_tier_name(tier: ApplicationTierEnum) -> str:
        """Get friendly name for tier."""
        tier_names = {
            ApplicationTierEnum.TIER_2_REVIEWER: "Tier 2 - Peer Reviewer",
            ApplicationTierEnum.TIER_3_EDITOR: "Tier 3 - Editor"
        }
        return tier_names.get(tier, str(tier))

    @staticmethod
    def _get_base_template(content: str) -> str:
        """Wrap content in base email template."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 8px 8px 0 0;
                    text-align: center;
                }}
                .content {{
                    background: #ffffff;
                    padding: 30px;
                    border: 1px solid #e0e0e0;
                    border-top: none;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 0 0 8px 8px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .button:hover {{
                    background: #5568d3;
                }}
                .alert {{
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .alert-success {{
                    background: #d4edda;
                    border: 1px solid #c3e6cb;
                    color: #155724;
                }}
                .alert-warning {{
                    background: #fff3cd;
                    border: 1px solid #ffeeba;
                    color: #856404;
                }}
                .alert-danger {{
                    background: #f8d7da;
                    border: 1px solid #f5c6cb;
                    color: #721c24;
                }}
                .alert-info {{
                    background: #d1ecf1;
                    border: 1px solid #bee5eb;
                    color: #0c5460;
                }}
                ul {{
                    padding-left: 20px;
                }}
                li {{
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Meta-Analysis Tool</h1>
                <p>Academic Research Platform</p>
            </div>
            <div class="content">
                {content}
            </div>
            <div class="footer">
                <p>&copy; {datetime.utcnow().year} Meta-Analysis Tool. All rights reserved.</p>
                <p>This is an automated email. Please do not reply directly to this message.</p>
            </div>
        </body>
        </html>
        """

    # ===========================
    # APPLICATION SUBMISSION
    # ===========================

    @staticmethod
    def send_application_submitted_email(
        to_email: str,
        tier: ApplicationTierEnum,
        application_id: str
    ):
        """Send confirmation email when application is submitted."""
        tier_name = EmailService._get_tier_name(tier)

        content = f"""
        <h2>Application Received</h2>
        <p>Dear Applicant,</p>
        <p>Thank you for submitting your application for <strong>{tier_name}</strong> access.</p>

        <div class="alert alert-info">
            <strong>Application ID:</strong> {application_id}<br>
            <strong>Submitted:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
        </div>

        <h3>What Happens Next?</h3>
        <ol>
            <li><strong>Automatic Verification (24-48 hours)</strong>
                <ul>
                    <li>ORCID profile verification</li>
                    <li>Google Scholar metrics analysis</li>
                    <li>Publication DOI validation</li>
                    <li>Background checks for research integrity</li>
                </ul>
            </li>
            <li><strong>Manual Review (3-5 business days)</strong>
                <ul>
                    <li>Academic credentials review</li>
                    <li>Peer review experience assessment</li>
                    <li>Research expertise evaluation</li>
                </ul>
            </li>
            <li><strong>Final Decision</strong>
                <ul>
                    <li>You will receive an email with the decision</li>
                    <li>If approved, tier access will be granted immediately</li>
                    <li>If denied, you can submit an appeal</li>
                </ul>
            </li>
        </ol>

        <p>You can track your application status in your dashboard.</p>

        <a href="https://app.metaanalysistool.com/dashboard/applications" class="button">View Application Status</a>

        <p>If you have any questions, please contact our support team.</p>

        <p>Best regards,<br>The Meta-Analysis Tool Team</p>
        """

        html_content = EmailService._get_base_template(content)
        subject = f"Application Received - {tier_name}"

        return EmailService._send_email(to_email, subject, html_content)

    # ===========================
    # AUTO-VERIFICATION RESULTS
    # ===========================

    @staticmethod
    def send_auto_verification_passed_email(to_email: str, tier: ApplicationTierEnum):
        """Send email when automatic verification passes."""
        tier_name = EmailService._get_tier_name(tier)

        content = f"""
        <h2>Automatic Verification Complete</h2>
        <p>Dear Applicant,</p>

        <div class="alert alert-success">
            <strong>✓ Automatic verification passed!</strong><br>
            Your credentials have been successfully verified.
        </div>

        <p>Your application for <strong>{tier_name}</strong> has passed our automatic verification process:</p>

        <ul>
            <li>✓ ORCID profile verified</li>
            <li>✓ Google Scholar profile confirmed</li>
            <li>✓ Publications validated</li>
            <li>✓ Background checks clear</li>
        </ul>

        <h3>Next Steps</h3>
        <p>Your application will now proceed to manual review by our admin team. This typically takes 3-5 business days.</p>

        <p>We will notify you as soon as a decision has been made.</p>

        <a href="https://app.metaanalysistool.com/dashboard/applications" class="button">View Application Status</a>

        <p>Best regards,<br>The Meta-Analysis Tool Team</p>
        """

        html_content = EmailService._get_base_template(content)
        subject = "Automatic Verification Passed"

        return EmailService._send_email(to_email, subject, html_content)

    @staticmethod
    def send_auto_verification_failed_email(
        to_email: str,
        tier: ApplicationTierEnum,
        reasons: List[str]
    ):
        """Send email when automatic verification fails."""
        tier_name = EmailService._get_tier_name(tier)

        reasons_html = "".join([f"<li>{reason}</li>" for reason in reasons])

        content = f"""
        <h2>Automatic Verification Results</h2>
        <p>Dear Applicant,</p>

        <div class="alert alert-warning">
            <strong>Your automatic verification did not pass.</strong>
        </div>

        <p>Unfortunately, your application for <strong>{tier_name}</strong> did not pass our automatic verification process.</p>

        <h3>Reasons:</h3>
        <ul>
            {reasons_html}
        </ul>

        <h3>What You Can Do</h3>
        <p>You have the following options:</p>
        <ol>
            <li><strong>Review and update your credentials:</strong> Ensure your ORCID and Google Scholar profiles are up to date and publicly visible.</li>
            <li><strong>Submit an appeal:</strong> If you believe this decision is incorrect, you can submit an appeal with additional evidence.</li>
            <li><strong>Continue with Tier 1:</strong> You can still use our platform with Tier 1 (Researcher) access while working on meeting the requirements.</li>
        </ol>

        <a href="https://app.metaanalysistool.com/dashboard/applications" class="button">Submit Appeal</a>

        <p>If you need assistance, please contact our support team.</p>

        <p>Best regards,<br>The Meta-Analysis Tool Team</p>
        """

        html_content = EmailService._get_base_template(content)
        subject = "Application Update - Verification Results"

        return EmailService._send_email(to_email, subject, html_content)

    # ===========================
    # APPROVAL / DENIAL
    # ===========================

    @staticmethod
    def send_application_approved_email(to_email: str, tier: ApplicationTierEnum):
        """Send approval email."""
        tier_name = EmailService._get_tier_name(tier)

        content = f"""
        <h2>🎉 Application Approved!</h2>
        <p>Dear Applicant,</p>

        <div class="alert alert-success">
            <strong>Congratulations!</strong><br>
            Your application for <strong>{tier_name}</strong> has been approved.
        </div>

        <p>Your account has been upgraded and you now have access to:</p>

        <ul>
            <li>✓ Advanced research tools</li>
            <li>✓ Peer review assignment system</li>
            <li>✓ Editorial dashboard (if Tier 3)</li>
            <li>✓ Priority support</li>
            <li>✓ Enhanced collaboration features</li>
        </ul>

        <h3>Next Steps</h3>
        <ol>
            <li>Complete your reviewer/editor profile</li>
            <li>Set your availability and preferences</li>
            <li>Start receiving review assignments</li>
        </ol>

        <a href="https://app.metaanalysistool.com/dashboard" class="button">Go to Dashboard</a>

        <p>Thank you for joining our academic community!</p>

        <p>Best regards,<br>The Meta-Analysis Tool Team</p>
        """

        html_content = EmailService._get_base_template(content)
        subject = f"Application Approved - Welcome to {tier_name}!"

        return EmailService._send_email(to_email, subject, html_content)

    @staticmethod
    def send_application_denied_email(
        to_email: str,
        denial_reasons: List[str],
        explanation: str
    ):
        """Send denial email with appeal option."""
        reasons_html = "".join([f"<li>{reason.replace('_', ' ').title()}</li>" for reason in denial_reasons])

        content = f"""
        <h2>Application Decision</h2>
        <p>Dear Applicant,</p>

        <div class="alert alert-warning">
            After careful review, we are unable to approve your application at this time.
        </div>

        <h3>Reasons for Denial:</h3>
        <ul>
            {reasons_html}
        </ul>

        <h3>Detailed Explanation:</h3>
        <p>{explanation}</p>

        <h3>Your Options</h3>
        <ol>
            <li><strong>Submit an Appeal:</strong> If you believe this decision is incorrect or if you have additional evidence to support your qualifications, you can submit an appeal within 30 days.</li>
            <li><strong>Reapply Later:</strong> You can work on addressing the reasons listed above and reapply after 6 months.</li>
            <li><strong>Continue with Tier 1:</strong> You can continue using our platform with Tier 1 (Researcher) access.</li>
        </ol>

        <a href="https://app.metaanalysistool.com/dashboard/applications/appeal" class="button">Submit Appeal</a>

        <p>We encourage you to reach out to our support team if you have questions about this decision.</p>

        <p>Best regards,<br>The Meta-Analysis Tool Team</p>
        """

        html_content = EmailService._get_base_template(content)
        subject = "Application Decision - Additional Information Needed"

        return EmailService._send_email(to_email, subject, html_content)

    @staticmethod
    def send_probationary_approval_email(
        to_email: str,
        tier: ApplicationTierEnum,
        probation_end_date: datetime
    ):
        """Send probationary approval email."""
        tier_name = EmailService._get_tier_name(tier)
        end_date = probation_end_date.strftime('%Y-%m-%d')

        content = f"""
        <h2>Application Approved (Probationary)</h2>
        <p>Dear Applicant,</p>

        <div class="alert alert-success">
            <strong>Your application for {tier_name} has been approved with a 90-day probationary period.</strong>
        </div>

        <h3>Probation Details:</h3>
        <ul>
            <li><strong>Start Date:</strong> {datetime.utcnow().strftime('%Y-%m-%d')}</li>
            <li><strong>End Date:</strong> {end_date}</li>
            <li><strong>Duration:</strong> 90 days</li>
        </ul>

        <h3>What This Means:</h3>
        <p>During the probationary period:</p>
        <ul>
            <li>You have full access to {tier_name} features</li>
            <li>Your performance will be monitored</li>
            <li>You must complete at least 5 reviews (if Tier 2) or handle 3 manuscripts (if Tier 3)</li>
            <li>Reviews must maintain a quality rating of 4.0+ out of 5.0</li>
        </ul>

        <h3>After Probation:</h3>
        <p>If you meet the requirements, your tier access will be confirmed permanently. If not, we'll work with you to address any concerns.</p>

        <a href="https://app.metaanalysistool.com/dashboard" class="button">Go to Dashboard</a>

        <p>Best regards,<br>The Meta-Analysis Tool Team</p>
        """

        html_content = EmailService._get_base_template(content)
        subject = f"Application Approved - {tier_name} (Probationary)"

        return EmailService._send_email(to_email, subject, html_content)

    # ===========================
    # MORE INFO REQUESTED
    # ===========================

    @staticmethod
    def send_more_info_requested_email(to_email: str, requested_info: List[str]):
        """Send email requesting additional information."""
        info_html = "".join([f"<li>{info}</li>" for info in requested_info])

        content = f"""
        <h2>Additional Information Needed</h2>
        <p>Dear Applicant,</p>

        <div class="alert alert-info">
            <strong>We need additional information to process your application.</strong>
        </div>

        <h3>Please provide the following:</h3>
        <ul>
            {info_html}
        </ul>

        <h3>How to Submit:</h3>
        <ol>
            <li>Log in to your dashboard</li>
            <li>Navigate to your application</li>
            <li>Upload the requested documents or information</li>
            <li>Click "Submit Additional Information"</li>
        </ol>

        <p><strong>Timeline:</strong> Please submit this information within 14 days to avoid application closure.</p>

        <a href="https://app.metaanalysistool.com/dashboard/applications" class="button">Submit Information</a>

        <p>If you have any questions about what we're requesting, please contact our support team.</p>

        <p>Best regards,<br>The Meta-Analysis Tool Team</p>
        """

        html_content = EmailService._get_base_template(content)
        subject = "Additional Information Required - Tier Application"

        return EmailService._send_email(to_email, subject, html_content)

    # ===========================
    # APPEALS
    # ===========================

    @staticmethod
    def send_appeal_submitted_email(to_email: str):
        """Confirm appeal submission."""
        content = f"""
        <h2>Appeal Received</h2>
        <p>Dear Applicant,</p>

        <div class="alert alert-info">
            <strong>Your appeal has been received and will be reviewed.</strong>
        </div>

        <h3>What Happens Next?</h3>
        <ol>
            <li><strong>Senior Review (7-10 business days):</strong> Your appeal will be reviewed by a senior admin or advisory board member.</li>
            <li><strong>Comprehensive Assessment:</strong> We will carefully consider all the evidence and information you provided.</li>
            <li><strong>Final Decision:</strong> You will receive a final decision via email. This decision is final.</li>
        </ol>

        <p><strong>Expected Response Time:</strong> 7-10 business days</p>

        <a href="https://app.metaanalysistool.com/dashboard/applications" class="button">View Appeal Status</a>

        <p>Thank you for your patience.</p>

        <p>Best regards,<br>The Meta-Analysis Tool Team</p>
        """

        html_content = EmailService._get_base_template(content)
        subject = "Appeal Received - Under Review"

        return EmailService._send_email(to_email, subject, html_content)

    @staticmethod
    def send_appeal_approved_email(to_email: str, tier: ApplicationTierEnum):
        """Send appeal approval email."""
        tier_name = EmailService._get_tier_name(tier)

        content = f"""
        <h2>🎉 Appeal Approved!</h2>
        <p>Dear Applicant,</p>

        <div class="alert alert-success">
            <strong>Great news!</strong><br>
            Your appeal has been approved and you have been granted <strong>{tier_name}</strong> access.
        </div>

        <p>After careful review of your appeal and additional evidence, we are pleased to approve your application.</p>

        <h3>Next Steps:</h3>
        <ol>
            <li>Complete your reviewer/editor profile</li>
            <li>Set your availability and preferences</li>
            <li>Start receiving assignments</li>
        </ol>

        <a href="https://app.metaanalysistool.com/dashboard" class="button">Go to Dashboard</a>

        <p>Thank you for your persistence and for joining our academic community!</p>

        <p>Best regards,<br>The Meta-Analysis Tool Team</p>
        """

        html_content = EmailService._get_base_template(content)
        subject = f"Appeal Approved - Welcome to {tier_name}!"

        return EmailService._send_email(to_email, subject, html_content)

    @staticmethod
    def send_appeal_denied_email(to_email: str, explanation: str):
        """Send appeal denial email."""
        content = f"""
        <h2>Appeal Decision</h2>
        <p>Dear Applicant,</p>

        <div class="alert alert-warning">
            After careful review, we must uphold the original decision to deny your application.
        </div>

        <h3>Explanation:</h3>
        <p>{explanation}</p>

        <h3>Your Options:</h3>
        <ol>
            <li><strong>Reapply in 6 Months:</strong> You may submit a new application after addressing the concerns raised.</li>
            <li><strong>Continue with Tier 1:</strong> You can continue using our platform with Tier 1 (Researcher) access.</li>
            <li><strong>Contact Support:</strong> If you have questions about this decision, our support team is here to help.</li>
        </ol>

        <p>This decision is final and cannot be appealed further.</p>

        <a href="https://app.metaanalysistool.com/support" class="button">Contact Support</a>

        <p>We appreciate your interest in our platform.</p>

        <p>Best regards,<br>The Meta-Analysis Tool Team</p>
        """

        html_content = EmailService._get_base_template(content)
        subject = "Appeal Decision - Final"

        return EmailService._send_email(to_email, subject, html_content)

    # ===========================
    # REFERENCE CHECKS (TIER 3)
    # ===========================

    @staticmethod
    def send_reference_check_email(
        to_email: str,
        reference_name: str,
        application_id: str,
        applicant_user_id: str
    ):
        """Send reference check email to professional reference."""
        content = f"""
        <h2>Professional Reference Request</h2>
        <p>Dear {reference_name},</p>

        <p>You have been listed as a professional reference for a Tier 3 (Editor) application on the Meta-Analysis Tool platform.</p>

        <h3>What We're Asking:</h3>
        <p>We would appreciate your candid feedback on the applicant's qualifications as an academic editor, including:</p>
        <ul>
            <li>Academic credentials and research expertise</li>
            <li>Editorial experience and judgment</li>
            <li>Professional conduct and ethics</li>
            <li>Ability to manage peer review processes</li>
        </ul>

        <h3>Time Commitment:</h3>
        <p>The reference form takes approximately 5-10 minutes to complete.</p>

        <a href="https://app.metaanalysistool.com/references/{application_id}" class="button">Complete Reference Form</a>

        <p><strong>Deadline:</strong> Please complete this within 7 days.</p>

        <p>Your feedback is confidential and will only be shared with our admin team.</p>

        <p>Thank you for taking the time to support academic excellence.</p>

        <p>Best regards,<br>The Meta-Analysis Tool Team</p>
        """

        html_content = EmailService._get_base_template(content)
        subject = "Professional Reference Request - Meta-Analysis Tool"

        return EmailService._send_email(to_email, subject, html_content)
