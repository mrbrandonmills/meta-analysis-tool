"""Stripe integration client for payment processing."""

from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

import stripe

from app.core.config import get_settings

settings = get_settings()
stripe.api_key = settings.stripe_secret_key

# SECURITY: Hardcoded subscription tiers to prevent payment tampering
# Never accept price_amount_cents from API callers to prevent users from
# modifying subscription costs (e.g., paying $1 instead of $100)
ALLOWED_SUBSCRIPTION_TIERS = {
    "standard": 10000,  # $100/month ($80 platform + $20 reviewer pool)
}


class StripeService:
    """Service for interacting with Stripe API."""

    @staticmethod
    def create_customer(email: str, name: str, metadata: Optional[Dict[str, Any]] = None) -> stripe.Customer:
        """
        Create a Stripe customer.

        Args:
            email: Customer email address
            name: Customer full name
            metadata: Additional metadata

        Returns:
            Stripe Customer object
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            logger.info(f"Created Stripe customer {customer.id} for {email}")
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise

    @staticmethod
    def create_subscription(
        customer_id: str,
        payment_method_id: str,
        tier: str = "standard",
        metadata: Optional[Dict[str, Any]] = None
    ) -> stripe.Subscription:
        """
        Create a monthly subscription.

        SECURITY: Only accepts tier name, not arbitrary amounts. This prevents
        payment tampering where users could modify API requests to pay less.

        Args:
            customer_id: Stripe customer ID
            payment_method_id: Payment method ID
            tier: Subscription tier name (must be in ALLOWED_SUBSCRIPTION_TIERS)
            metadata: Additional metadata

        Returns:
            Stripe Subscription object

        Raises:
            ValueError: If tier is invalid
        """
        # SECURITY FIX (CRITICAL-001): Validate tier and use hardcoded amount
        if tier not in ALLOWED_SUBSCRIPTION_TIERS:
            raise ValueError(f"Invalid subscription tier: {tier}. Allowed tiers: {list(ALLOWED_SUBSCRIPTION_TIERS.keys())}")

        price_amount_cents = ALLOWED_SUBSCRIPTION_TIERS[tier]

        try:
            # Attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )

            # Set as default payment method
            stripe.Customer.modify(
                customer_id,
                invoice_settings={
                    'default_payment_method': payment_method_id
                }
            )

            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': 'Researcher Monthly Subscription',
                                'description': 'Access to peer review platform ($80 platform + $20 reviewer pool)'
                            },
                            'unit_amount': price_amount_cents,
                            'recurring': {
                                'interval': 'month'
                            }
                        }
                    }
                ],
                expand=['latest_invoice.payment_intent'],
                metadata=metadata or {}
            )

            logger.info(f"Created subscription {subscription.id} for customer {customer_id} with tier {tier} (${price_amount_cents/100:.2f})")
            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create subscription: {e}")
            raise

    @staticmethod
    def cancel_subscription(subscription_id: str, at_period_end: bool = True) -> stripe.Subscription:
        """
        Cancel a subscription.

        Args:
            subscription_id: Stripe subscription ID
            at_period_end: If True, cancel at period end. If False, cancel immediately.

        Returns:
            Updated Stripe Subscription object
        """
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
                logger.info(f"Subscription {subscription_id} set to cancel at period end")
            else:
                subscription = stripe.Subscription.delete(subscription_id)
                logger.info(f"Subscription {subscription_id} canceled immediately")

            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {e}")
            raise

    @staticmethod
    def get_subscription(subscription_id: str) -> stripe.Subscription:
        """
        Retrieve a subscription.

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            Stripe Subscription object
        """
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve subscription: {e}")
            raise

    @staticmethod
    def create_connect_account(
        email: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> stripe.Account:
        """
        Create a Stripe Connect Express account for reviewer payouts.

        Args:
            email: Reviewer email
            metadata: Additional metadata

        Returns:
            Stripe Account object
        """
        try:
            account = stripe.Account.create(
                type='express',
                country='US',
                email=email,
                capabilities={
                    'transfers': {'requested': True},
                },
                metadata=metadata or {}
            )
            logger.info(f"Created Connect account {account.id} for {email}")
            return account

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Connect account: {e}")
            raise

    @staticmethod
    def create_account_link(
        account_id: str,
        refresh_url: str,
        return_url: str
    ) -> stripe.AccountLink:
        """
        Create an account link for Connect onboarding.

        Args:
            account_id: Stripe Connect account ID
            refresh_url: URL to redirect if link expires
            return_url: URL to redirect after completion

        Returns:
            Stripe AccountLink object
        """
        try:
            account_link = stripe.AccountLink.create(
                account=account_id,
                refresh_url=refresh_url,
                return_url=return_url,
                type='account_onboarding',
            )
            logger.info(f"Created account link for {account_id}")
            return account_link

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create account link: {e}")
            raise

    @staticmethod
    def create_transfer(
        connect_account_id: str,
        amount_cents: int,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> stripe.Transfer:
        """
        Transfer funds to a Connect account.

        Args:
            connect_account_id: Stripe Connect account ID
            amount_cents: Amount to transfer in cents
            description: Transfer description
            metadata: Additional metadata

        Returns:
            Stripe Transfer object
        """
        try:
            transfer = stripe.Transfer.create(
                amount=amount_cents,
                currency='usd',
                destination=connect_account_id,
                description=description,
                metadata=metadata or {}
            )
            logger.info(f"Created transfer {transfer.id} of ${amount_cents/100:.2f} to {connect_account_id}")
            return transfer

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create transfer: {e}")
            raise

    @staticmethod
    def get_account(account_id: str) -> stripe.Account:
        """
        Retrieve a Connect account.

        Args:
            account_id: Stripe Connect account ID

        Returns:
            Stripe Account object
        """
        try:
            return stripe.Account.retrieve(account_id)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve account: {e}")
            raise

    @staticmethod
    def construct_webhook_event(
        payload: bytes,
        sig_header: str,
        webhook_secret: str
    ) -> stripe.Event:
        """
        Construct and verify a webhook event.

        Args:
            payload: Request body bytes
            sig_header: Stripe signature header
            webhook_secret: Webhook signing secret

        Returns:
            Stripe Event object

        Raises:
            stripe.error.SignatureVerificationError: If signature is invalid
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            raise

    @staticmethod
    def list_invoices(customer_id: str, limit: int = 10) -> stripe.ListObject:
        """
        List invoices for a customer.

        Args:
            customer_id: Stripe customer ID
            limit: Maximum number of invoices to return

        Returns:
            List of Stripe Invoice objects
        """
        try:
            invoices = stripe.Invoice.list(
                customer=customer_id,
                limit=limit
            )
            return invoices
        except stripe.error.StripeError as e:
            logger.error(f"Failed to list invoices: {e}")
            raise
