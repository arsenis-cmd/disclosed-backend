import resend
from typing import Optional
from config import get_settings

settings = get_settings()

if settings.resend_api_key:
    resend.api_key = settings.resend_api_key


class EmailService:
    """Email service using Resend for transactional emails"""

    def __init__(self):
        self.enabled = bool(settings.resend_api_key)
        self.from_email = "PoC <noreply@poc.io>"
        self.frontend_url = settings.frontend_url

    async def send_verification_result(
        self,
        to_email: str,
        considerer_name: str,
        task_title: str,
        passed: bool,
        combined_score: float,
        earned_amount: Optional[float]
    ):
        """Send email to considerer after proof verification"""
        if not self.enabled:
            print(f"Email disabled - would send verification result to {to_email}")
            return

        if passed:
            subject = f"✅ Proof verified! You earned ${earned_amount:.2f}"
            html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #16a34a;">Great work, {considerer_name}!</h2>
                <p style="font-size: 16px;">Your response to "{task_title}" has been verified.</p>

                <div style="background-color: #f0fdf4; border: 2px solid #16a34a; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 14px; color: #15803d;">Score</p>
                    <p style="margin: 5px 0 0 0; font-size: 32px; font-weight: bold; color: #16a34a;">{int(combined_score * 100)}%</p>
                </div>

                <div style="background-color: #f0fdf4; border: 2px solid #16a34a; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 14px; color: #15803d;">Earned</p>
                    <p style="margin: 5px 0 0 0; font-size: 32px; font-weight: bold; color: #16a34a;">${earned_amount:.2f}</p>
                </div>

                <p style="color: #666; font-size: 14px;">
                    Your payment has been sent to your Stripe account and will appear in your bank within 1-2 business days.
                </p>

                <a href="{self.frontend_url}/earnings"
                   style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0;">
                    View Your Earnings →
                </a>

                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">

                <p style="color: #999; font-size: 12px;">
                    🤖 Generated with Proof of Consideration
                </p>
            </div>
            """
        else:
            subject = f"Response not verified for {task_title}"
            html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #ea580c;">Hi {considerer_name},</h2>
                <p style="font-size: 16px;">Your response to "{task_title}" didn't meet the verification threshold.</p>

                <div style="background-color: #fff7ed; border: 2px solid #ea580c; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 14px; color: #c2410c;">Your Score</p>
                    <p style="margin: 5px 0 0 0; font-size: 32px; font-weight: bold; color: #ea580c;">{int(combined_score * 100)}%</p>
                </div>

                <div style="background-color: #eff6ff; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1e40af;">💡 Tips for Next Time:</h3>
                    <ul style="color: #1e3a8a; line-height: 1.6;">
                        <li>Share specific personal experiences and examples</li>
                        <li>Explain WHY you think something, not just what</li>
                        <li>Include details that only you would know</li>
                        <li>Take your time - quality over speed</li>
                        <li>Avoid generic responses that could apply to anyone</li>
                    </ul>
                </div>

                <a href="{self.frontend_url}/tasks"
                   style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0;">
                    Find Another Task →
                </a>

                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">

                <p style="color: #999; font-size: 12px;">
                    🤖 Generated with Proof of Consideration
                </p>
            </div>
            """

        try:
            resend.Emails.send({
                "from": self.from_email,
                "to": to_email,
                "subject": subject,
                "html": html
            })
        except Exception as e:
            print(f"Failed to send verification email to {to_email}: {str(e)}")

    async def send_new_response_to_buyer(
        self,
        to_email: str,
        buyer_name: str,
        campaign_title: str,
        campaign_id: str,
        responses_count: int,
        max_responses: int
    ):
        """Notify buyer of new verified response"""
        if not self.enabled:
            print(f"Email disabled - would send new response notification to {to_email}")
            return

        subject = f"New verified response for {campaign_title}"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2563eb;">Hi {buyer_name},</h2>
            <p style="font-size: 16px;">You have a new verified response for your campaign "{campaign_title}".</p>

            <div style="background-color: #eff6ff; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <p style="margin: 0; font-size: 14px; color: #1e40af;">Progress</p>
                <p style="margin: 5px 0 0 0; font-size: 32px; font-weight: bold; color: #2563eb;">
                    {responses_count}/{max_responses}
                </p>
                <div style="background-color: #dbeafe; height: 8px; border-radius: 4px; margin-top: 10px; overflow: hidden;">
                    <div style="background-color: #2563eb; height: 100%; width: {int(responses_count/max_responses*100)}%;"></div>
                </div>
            </div>

            <a href="{self.frontend_url}/campaigns/{campaign_id}/responses"
               style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0;">
                View Response →
            </a>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">

            <p style="color: #999; font-size: 12px;">
                🤖 Generated with Proof of Consideration
            </p>
        </div>
        """

        try:
            resend.Emails.send({
                "from": self.from_email,
                "to": to_email,
                "subject": subject,
                "html": html
            })
        except Exception as e:
            print(f"Failed to send new response email to {to_email}: {str(e)}")

    async def send_campaign_complete(
        self,
        to_email: str,
        buyer_name: str,
        campaign_title: str,
        campaign_id: str,
        total_responses: int
    ):
        """Notify buyer when campaign reaches response goal"""
        if not self.enabled:
            print(f"Email disabled - would send campaign complete notification to {to_email}")
            return

        subject = f"🎉 Campaign complete: {campaign_title}"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #16a34a;">🎉 Congratulations {buyer_name}!</h2>
            <p style="font-size: 16px;">Your campaign "{campaign_title}" has reached its response goal.</p>

            <div style="background-color: #f0fdf4; border: 2px solid #16a34a; border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center;">
                <p style="margin: 0; font-size: 14px; color: #15803d;">Total Verified Responses</p>
                <p style="margin: 5px 0 0 0; font-size: 48px; font-weight: bold; color: #16a34a;">{total_responses}</p>
            </div>

            <p style="font-size: 16px;">All responses have been verified and are ready for your review.</p>

            <div style="margin: 30px 0;">
                <a href="{self.frontend_url}/campaigns/{campaign_id}/responses"
                   style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-right: 10px;">
                    View All Responses →
                </a>
                <a href="{self.frontend_url}/campaigns/{campaign_id}/analytics"
                   style="display: inline-block; background-color: #6b7280; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">
                    View Analytics →
                </a>
            </div>

            <div style="background-color: #eff6ff; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #1e40af;">Next Steps:</h3>
                <ul style="color: #1e3a8a; line-height: 1.6;">
                    <li>Review all responses in your dashboard</li>
                    <li>Export data as CSV for further analysis</li>
                    <li>Create a new campaign to gather more insights</li>
                </ul>
            </div>

            <a href="{self.frontend_url}/campaigns/new"
               style="display: inline-block; background-color: #16a34a; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0;">
                Create Another Campaign →
            </a>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">

            <p style="color: #999; font-size: 12px;">
                🤖 Generated with Proof of Consideration
            </p>
        </div>
        """

        try:
            resend.Emails.send({
                "from": self.from_email,
                "to": to_email,
                "subject": subject,
                "html": html
            })
        except Exception as e:
            print(f"Failed to send campaign complete email to {to_email}: {str(e)}")


# Singleton instance
email_service = EmailService()
