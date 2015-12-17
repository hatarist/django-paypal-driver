# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from paypal_driver.driver import PayPal
from paypal_driver.models import PayPalResponse


def process_payment_request(amount, currency, token, payerid, email=None):
    """
    utility function to perform PayPal payment
    """
    # call PayPal driver and perform the relevant PayPal API method to charge the money
    driver = PayPal(email=email)
    result = driver.DoExpressCheckoutPayment(
        currency=currency,
        amount=str(amount),
        token=token,
        payerid=payerid
    )

    # persist the response to the db with PayPalResponse instance
    paypal_response = PayPalResponse()
    paypal_response.fill_from_response(driver.GetPaymentResponse())
    paypal_response.status = PayPalResponse.get_default_status()

    if result:
        # Amount charged successfully.
        paypal_response.payment_received = True
        paypal_response.save()
        return True, paypal_response
    else:
        # Amount charged could not be charged successfully. Note that
        # the paypal_response is going to be saved.
        paypal_response.error = _(driver.doexpresscheckoutpaymenterror)
        paypal_response.save()
        return False, paypal_response


def process_refund_request(response, amount):
    """
    utility function to perform PayPal refund
    """
    # call PayPal driver and perform the relevant PayPal API method to refund the money
    driver = PayPal()
    result = driver.RefundTransaction(
        response.trans_id,
        refundtype="Partial",
        amount=str(amount),
        currency=response.currencycode
    )

    # persist the response to the db with PayPalResponse instance
    paypal_response = PayPalResponse()
    paypal_response.fill_from_response(driver.GetRefundResponse(), action="Refund")
    paypal_response.status = PayPalResponse.get_cancel_status()

    if result:
        # Amount refunded successfully.
        paypal_response.payment_received = True
        paypal_response.save()
        return True, paypal_response
    else:
        # Amount charged could not be refunded successfully. Note that
        # the paypal_response is going to be saved
        paypal_response.error = _(driver.refundtransactionerror)
        paypal_response.save()
        return False, paypal_response
