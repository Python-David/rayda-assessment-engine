user_event = {
    "event_type": "user.created",
    "event_id": "evt_user_001",
    "timestamp": "2024-02-15T10:30:00Z",
    "organization_id": "org_001",
    "data": {
        "user_id": "ext_user_new_123",
        "email": "new.employee@techcorp.com",
        "first_name": "Frank",
        "last_name": "Maduka",
        "department": "Product",
        "title": "Product Manager",
        "status": "active",
        "hire_date": "2024-02-15",
    },
    "metadata": {
        "source": "hr_system",
        "version": "1.2",
        "correlation_id": "hr_sync_456",
    },
}


payment_event = {
    "event_type": "subscription.created",
    "event_id": "evt_pay_101",
    "timestamp": "2024-02-15T09:00:00Z",
    "organization_id": "org_002",
    "data": {
        "subscription_id": "sub_new_789",
        "customer_id": "cust_startup_123",
        "plan": "professional",
        "status": "active",
        "billing_cycle": "monthly",
        "amount": 299.99,
        "currency": "USD",
        "trial_end": "2024-03-15T23:59:59Z",
    },
    "metadata": {"source": "billing_system", "version": "2.1", "sales_rep": "rep_456"},
}

communication_event = {
    "event_id": "evt_comm_test_001",
    "organization_id": "org_001",
    "event_type": "message.delivered",
    "timestamp": "2025-06-29T14:00:00Z",
    "data": {
        "message_id": "msg_001",
        "recipient": "user@example.com",
        "template": "welcome_email",
        "status": "delivered",
    },
    "metadata": {
        "source": "email_test",
        "version": "1.0",
        "correlation_id": "test_corr_003",
    },
}

batch_user_events = {
    "events": [
        {
            "event_type": "user.created",
            "event_id": "evt_user_batch_001",
            "timestamp": "2025-06-29T12:00:00Z",
            "organization_id": "org_001",
            "data": {
                "user_id": "ext_user_batch_001",
                "email": "batch.user1@example.com",
                "first_name": "Batch",
                "last_name": "UserOne",
                "department": "Engineering",
                "title": "Engineer",
                "status": "active",
                "hire_date": "2025-06-29",
            },
            "metadata": {
                "source": "batch_test",
                "version": "1.0",
                "correlation_id": "batch_corr_001",
            },
        },
        {
            "event_type": "user.updated",
            "event_id": "evt_user_batch_002",
            "timestamp": "2025-06-29T12:30:00Z",
            "organization_id": "org_001",
            "data": {
                "user_id": "ext_user_batch_002",
                "changes": {"department": "Product", "title": "Senior PM"},
                "previous_values": {"department": "Engineering", "title": "PM"},
            },
            "metadata": {
                "source": "batch_test",
                "version": "1.0",
                "correlation_id": "batch_corr_002",
            },
        },
    ]
}

batch_payment_events = {
    "events": [
        {
            "event_type": "subscription.created",
            "event_id": "evt_pay_batch_001",
            "timestamp": "2025-06-29T10:00:00Z",
            "organization_id": "org_002",
            "data": {
                "subscription_id": "sub_batch_001",
                "customer_id": "cust_batch_001",
                "plan": "enterprise",
                "status": "active",
                "billing_cycle": "annual",
                "amount": 1999.99,
                "currency": "USD",
                "trial_end": "2025-07-29T23:59:59Z",
            },
            "metadata": {
                "source": "batch_billing",
                "version": "2.0",
                "sales_rep": "rep_batch_001",
            },
        },
        {
            "event_type": "payment.failed",
            "event_id": "evt_pay_batch_002",
            "timestamp": "2025-06-29T11:00:00Z",
            "organization_id": "org_002",
            "data": {
                "payment_id": "pay_batch_002",
                "subscription_id": "sub_batch_002",
                "amount": 499.99,
                "currency": "USD",
                "failure_reason": "insufficient_funds",
                "failure_code": "card_declined",
                "retry_at": "2025-07-01T10:00:00Z",
                "attempt_number": 1,
            },
            "metadata": {
                "source": "batch_billing",
                "version": "2.0",
                "gateway": "stripe_batch",
            },
        },
    ]
}

batch_communication_events = {
    "events": [
        {
            "event_type": "message.delivered",
            "event_id": "evt_comm_batch_001",
            "timestamp": "2025-06-29T09:30:00Z",
            "organization_id": "org_001",
            "data": {
                "message_id": "msg_batch_001",
                "recipient": "batch.user1@example.com",
                "template": "welcome_email",
                "status": "delivered",
            },
            "metadata": {
                "source": "batch_email",
                "version": "1.0",
                "correlation_id": "batch_corr_comm_001",
            },
        },
        {
            "event_type": "message.bounced",
            "event_id": "evt_comm_batch_002",
            "timestamp": "2025-06-29T10:00:00Z",
            "organization_id": "org_001",
            "data": {
                "message_id": "msg_batch_002",
                "recipient": "invalid.user@example.com",
                "template": "promo_email",
                "bounce_reason": "recipient_not_found",
                "bounce_type": "permanent",
                "esp_bounce_code": "550",
            },
            "metadata": {
                "source": "batch_email",
                "version": "1.0",
                "correlation_id": "batch_corr_comm_002",
            },
        },
    ]
}
